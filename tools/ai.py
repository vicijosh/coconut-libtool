import hashlib
import json
import os
import urllib.error
import urllib.request

import streamlit as st


PROVIDERS = ("OpenAI", "OpenAI-compatible endpoint", "Ollama local")

SYSTEM_PROMPT = """
You are Coconut AI, an assistant for library, information science, and text
analysis workflows. Interpret only the aggregate analysis results provided.
Do not claim to have read the uploaded source file unless raw excerpts are
explicitly included. Be clear, concise, and practical.
"""


class AIConfigurationError(Exception):
    """Raised when the selected AI provider is missing required settings."""


def _json_default(value):
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return str(value)


def _to_jsonable(value):
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return str(value)
    return value


def _records_from_frame(frame, limit=20):
    if frame is None:
        return []
    if hasattr(frame, "head") and hasattr(frame, "to_dict"):
        return _to_jsonable(frame.head(limit).to_dict("records"))
    return _to_jsonable(frame)


def frequency_payload(module_name, selected_column, frequency_frame, limit=20):
    records = _records_from_frame(frequency_frame, limit=limit)
    total = 0
    for row in records:
        if not isinstance(row, dict):
            continue
        for key in ("Frequency", "Count", "size", "count", "frequency"):
            if key in row:
                try:
                    total += int(float(row[key]))
                except Exception:
                    pass
                break

    return {
        "module": module_name,
        "privacy": "Aggregate counts only. Raw uploaded text is omitted.",
        "selected_column": str(selected_column),
        "top_items": records,
        "visible_item_count": len(records),
        "visible_frequency_total": total,
    }


def sentiment_payload(
    module_name,
    selected_column,
    method,
    distribution,
    mean_scores=None,
    top_terms=None,
    record_count=None,
):
    return {
        "module": module_name,
        "privacy": "Aggregate sentiment scores only. Raw uploaded text is omitted.",
        "selected_column": str(selected_column),
        "method": str(method),
        "record_count": record_count,
        "sentiment_distribution": _to_jsonable(distribution),
        "mean_scores": _to_jsonable(mean_scores or {}),
        "top_terms": _to_jsonable(top_terms or {}),
    }


def table_payload(module_name, result_name, frame, metadata=None, limit=25):
    records = _records_from_frame(frame, limit=limit)
    row_count = len(frame) if hasattr(frame, "__len__") else len(records)
    return {
        "module": module_name,
        "result_name": str(result_name),
        "privacy": "Aggregate result table only. Raw uploaded text is omitted.",
        "metadata": _to_jsonable(metadata or {}),
        "visible_rows": records,
        "visible_row_count": len(records),
        "total_row_count": int(row_count) if isinstance(row_count, int) else row_count,
    }


def comparison_counter_payload(
    module_name,
    selected_column,
    comparison_type,
    first_label,
    second_label,
    first_counter,
    second_counter,
    method=None,
    limit=20,
):
    first_items = sorted(first_counter.items(), key=lambda item: item[1], reverse=True)[:limit]
    second_items = sorted(second_counter.items(), key=lambda item: item[1], reverse=True)[:limit]
    shared_words = sorted(set(first_counter).intersection(second_counter))[:limit]

    return {
        "module": module_name,
        "privacy": "Aggregate word counts only. Raw uploaded text is omitted.",
        "selected_column": str(selected_column),
        "comparison_type": str(comparison_type),
        "method": str(method) if method else "",
        "first_group": {
            "label": str(first_label),
            "total_terms": int(sum(first_counter.values())),
            "unique_terms": len(first_counter),
            "top_terms": [{"term": term, "count": int(count)} for term, count in first_items],
        },
        "second_group": {
            "label": str(second_label),
            "total_terms": int(sum(second_counter.values())),
            "unique_terms": len(second_counter),
            "top_terms": [{"term": term, "count": int(count)} for term, count in second_items],
        },
        "shared_terms_sample": shared_words,
    }


def _prompt_from_payload(module_name, result_payload, user_goal="", max_payload_chars=12000):
    payload = json.dumps(_to_jsonable(result_payload), indent=2, default=_json_default)
    if len(payload) > max_payload_chars:
        payload = payload[:max_payload_chars] + "\n... [payload truncated]"

    goal = user_goal.strip() or "Explain the most important findings for a non-technical user."
    return f"""
Analyze these aggregate Coconut Libtool results.

Tool:
{module_name}

User question:
{goal}

Aggregate result payload:
{payload}

Return Markdown with these sections:
1. Quick take
2. What stands out
3. Caveats
4. Recommended next steps
"""


def _payload_signature(result_payload):
    payload = json.dumps(_to_jsonable(result_payload), sort_keys=True, default=_json_default)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:10]


def _extract_response_text(response):
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    if isinstance(response, dict):
        if response.get("output_text"):
            return response["output_text"]
        output = response.get("output", [])
    else:
        output = getattr(response, "output", [])

    chunks = []
    for item in output or []:
        content = item.get("content", []) if isinstance(item, dict) else getattr(item, "content", [])
        for part in content or []:
            if isinstance(part, dict):
                text = part.get("text")
            else:
                text = getattr(part, "text", None)
            if text:
                chunks.append(text)
    return "\n".join(chunks).strip()


def _post_json(url, payload, headers=None, timeout=120):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {details}") from exc


def _extract_chat_text(response):
    choices = response.get("choices", []) if isinstance(response, dict) else []
    if not choices:
        return ""
    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, list):
        return "\n".join(part.get("text", "") for part in content if isinstance(part, dict)).strip()
    return str(content).strip()


def _chat_completion_http(url, api_key, model, prompt, max_output_tokens, temperature):
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_output_tokens,
    }
    if temperature is not None:
        payload["temperature"] = temperature

    try:
        response = _post_json(url, payload, headers=headers)
    except RuntimeError as exc:
        message = str(exc).lower()
        if temperature is not None and "temperature" in message and ("unsupported" in message or "not support" in message):
            return _chat_completion_http(url, api_key, model, prompt, max_output_tokens, None)
        if "max_tokens" in message and "max_completion_tokens" in message:
            payload.pop("max_tokens", None)
            payload["max_completion_tokens"] = max_output_tokens
            response = _post_json(url, payload, headers=headers)
        else:
            raise

    text = _extract_chat_text(response)
    if not text:
        raise RuntimeError("The provider returned an empty response.")
    return text


def _openai_completion(api_key, model, prompt, base_url=None, max_output_tokens=700, temperature=0.2):
    if not model:
        raise AIConfigurationError("Enter the model name you want to use.")
    if not api_key and not base_url:
        raise AIConfigurationError("Enter your OpenAI API key.")

    if base_url:
        endpoint = base_url.rstrip("/")
        if not endpoint.endswith("/chat/completions"):
            endpoint = f"{endpoint}/chat/completions"
        return _chat_completion_http(endpoint, api_key, model, prompt, max_output_tokens, temperature)

    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "instructions": SYSTEM_PROMPT.strip(),
        "input": prompt,
        "max_output_tokens": max_output_tokens,
    }
    if temperature is not None:
        payload["temperature"] = temperature
    try:
        response = _post_json("https://api.openai.com/v1/responses", payload, headers=headers)
        text = _extract_response_text(response)
        if text:
            return text
    except RuntimeError as exc:
        message = str(exc).lower()
        if temperature is not None and "temperature" in message and ("unsupported" in message or "not support" in message):
            return _openai_completion(
                api_key=api_key,
                model=model,
                prompt=prompt,
                base_url=base_url,
                max_output_tokens=max_output_tokens,
                temperature=None,
            )
        raise

    raise RuntimeError("OpenAI returned an empty response.")


def _ollama_completion(base_url, model, prompt, max_output_tokens=700, temperature=0.2):
    if not model:
        raise AIConfigurationError("Enter the Ollama model name you have pulled locally.")

    base_url = (base_url or "http://localhost:11434").rstrip("/")
    options = {"num_predict": max_output_tokens}
    if temperature is not None:
        options["temperature"] = temperature
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": options,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        f"{base_url}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise AIConfigurationError("Could not reach Ollama. Start Ollama or check the URL.") from exc

    if "message" in payload and isinstance(payload["message"], dict):
        return payload["message"].get("content", "")
    return payload.get("response", "")


def generate_ai_insight(
    module_name,
    result_payload,
    provider,
    model,
    api_key="",
    base_url="",
    user_goal="",
    max_output_tokens=700,
    temperature=0.2,
):
    prompt = _prompt_from_payload(module_name, result_payload, user_goal=user_goal)

    if provider == "OpenAI":
        return _openai_completion(
            api_key=api_key,
            model=model,
            prompt=prompt,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )

    if provider == "OpenAI-compatible endpoint":
        if not base_url:
            raise AIConfigurationError("Enter the endpoint base URL, for example http://localhost:8000/v1.")
        return _openai_completion(
            api_key=api_key or "not-needed",
            model=model,
            prompt=prompt,
            base_url=base_url,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )

    if provider == "Ollama local":
        return _ollama_completion(
            base_url=base_url,
            model=model,
            prompt=prompt,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )

    raise AIConfigurationError("Choose a supported AI provider.")


def render_ai_insights(module_name, result_payload, page_key, default_goal=""):
    with st.expander("Coconut AI Insights", expanded=False):
        st.markdown(
            """
            <div class="coconut-ai-note">
                By default, Coconut Libtool sends only summarized analysis results, not full uploaded files.
                API keys are used only while you are working and are not stored by Coconut Libtool.
                AI insights are interpretive support; verify important claims against your tables, charts, source data, and domain knowledge.
            </div>
            """,
            unsafe_allow_html=True,
        )

        provider = st.selectbox("AI provider", PROVIDERS, key=f"{page_key}_provider")
        col1, col2 = st.columns(2)

        api_key = ""
        base_url = ""
        model = ""

        if provider == "OpenAI":
            api_key = col1.text_input(
                "OpenAI API key",
                type="password",
                placeholder="sk-...",
                key=f"{page_key}_openai_key",
            )
            model = col2.text_input(
                "OpenAI model",
                value=os.getenv("COCONUT_OPENAI_MODEL", "gpt-5.4-mini"),
                placeholder="Example: gpt-5.4-mini",
                key=f"{page_key}_openai_model",
            )
            col2.caption("Use the exact lowercase API model ID your OpenAI account supports, such as gpt-5.4-mini, gpt-5.4, or gpt-5.5.")
        elif provider == "OpenAI-compatible endpoint":
            api_key = col1.text_input(
                "API key",
                type="password",
                placeholder="Optional for local servers",
                key=f"{page_key}_compatible_key",
            )
            base_url = col2.text_input(
                "Base URL",
                value=os.getenv("COCONUT_OPENAI_COMPATIBLE_URL", "http://localhost:8000/v1"),
                key=f"{page_key}_compatible_url",
            )
            model = st.text_input(
                "Model",
                value=os.getenv("COCONUT_OPENAI_COMPATIBLE_MODEL", ""),
                placeholder="Type the served model name",
                key=f"{page_key}_compatible_model",
            )
        else:
            base_url = col1.text_input(
                "Ollama URL",
                value=os.getenv("COCONUT_OLLAMA_URL", "http://localhost:11434"),
                key=f"{page_key}_ollama_url",
            )
            model = col2.text_input(
                "Ollama model",
                value=os.getenv("COCONUT_OLLAMA_MODEL", ""),
                placeholder="Type a local model name",
                key=f"{page_key}_ollama_model",
            )

        user_goal = st.text_area(
            "Question for the AI",
            value=default_goal or "Explain the main pattern, caveats, and what I should do next.",
            key=f"{page_key}_goal",
        )
        max_output_tokens = st.slider(
            "Response length",
            min_value=250,
            max_value=1200,
            value=700,
            step=50,
            key=f"{page_key}_tokens",
        )

        if st.checkbox("Show aggregate payload before sending", key=f"{page_key}_show_payload"):
            st.json(result_payload)

        result_key = f"{page_key}_{_payload_signature(result_payload)}_ai_result"
        if st.button("Generate AI insight", key=f"{page_key}_generate_ai"):
            try:
                with st.spinner("Asking the selected model to interpret the aggregate results..."):
                    st.session_state[result_key] = generate_ai_insight(
                        module_name=module_name,
                        result_payload=result_payload,
                        provider=provider,
                        model=model.strip(),
                        api_key=api_key.strip(),
                        base_url=base_url.strip(),
                        user_goal=user_goal,
                        max_output_tokens=max_output_tokens,
                    )
            except AIConfigurationError as exc:
                st.warning(str(exc))
            except Exception as exc:
                st.error(f"The AI provider returned an error: {exc}")

        if st.session_state.get(result_key):
            st.markdown("#### AI interpretation")
            st.markdown(st.session_state[result_key])
            st.download_button(
                "Download AI insight",
                data=st.session_state[result_key],
                file_name=f"{module_name.lower().replace(' ', '_')}_ai_insight.md",
                mime="text/markdown",
                key=f"{page_key}_{_payload_signature(result_payload)}_download_ai",
            )
