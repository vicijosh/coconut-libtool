#import module
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import re
import nltk
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
import os
import numpy as np
import plotly.express as px
import json
from tools import ai, runtime, sourceformat as sf, textprep, ui
#===config===
st.set_page_config(
    page_title="Coconut",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

runtime.ensure_nltk_data('stopwords', 'punkt', 'punkt_tab', 'vader_lexicon')

ui.apply_app_style()

ui.render_tool_menu()
ui.render_page_header("Sentiment Analysis", "Score and inspect sentiment patterns in text data.")
with st.expander("Before you start", expanded = True):
    tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download"])
    with tab1:
        st.write('Sentiment analysis uses natural language processing to identify patterns in large text datasets, revealing the writer’s opinions, emotions, and attitudes. It assesses subjectivity (objective vs. subjective), polarity (positive, negative, neutral), and emotions (e.g., anger, joy, sadness, surprise, jealousy).') 
        st.divider()
        st.write('💡 The idea came from this:')
        st.write('Lamba, M., & Madhusudhan, M. (2021, July 31). Sentiment Analysis. Text Mining for Information Professionals, 191–211. https://doi.org/10.1007/978-3-030-85085-2_7')
        
    with tab2:
        st.write("1. Put your file. Choose your prefered column to analyze")
        st.write("2. Choose your preferred method and decide which words you want to remove")
        st.write("3. Finally, you can visualize your data.")
        
    with tab3:
        st.code("""
        +----------------+------------------------+----------------------------------+
        |     Source     |       File Type        |              Column              |
        +----------------+------------------------+----------------------------------+
        | Scopus         | Comma-separated values | Choose your preferred column     |
        |                | (.csv)                 | that you have                    |
        +----------------+------------------------|                                  |
        | Web of Science | Tab delimited file     |                                  |
        |                | (.txt)                 |                                  |
        +----------------+------------------------|                                  |
        | Lens.org       | Comma-separated values |                                  |
        |                | (.csv)                 |                                  |
        +----------------+------------------------|                                  |
        | Dimensions     | Comma-separated values |                                  |
        |                | (.csv)                 |                                  |
        +----------------+------------------------|                                  |
        | OpenAlex       | Comma-separated values |                                  |
        |                | (.csv)                 |                                  |
        +----------------+------------------------|                                  |
        | Other          | .csv .xls .xlsx        |                                  |
        +----------------+------------------------|                                  |
        | Hathitrust     | .json                  |                                  |
        +----------------+------------------------+----------------------------------+
        """, language=None)
        
    with tab4:
        st.subheader(':blue[Sentiment Analysis]', anchor=False)
        st.write("Click the three dots at the top right then select the desired format")
        st.markdown("![Downloading visualization](https://raw.githubusercontent.com/faizhalas/library-tools/main/images/download_sentiment.png)")
        st.divider()
        st.subheader(':blue[CSV Results]', anchor=False)
        st.text("Click Download button")
        st.markdown("![Downloading results](https://raw.githubusercontent.com/faizhalas/library-tools/main/images/sentitable.png)")
        

#========unique id========
@st.cache_resource(ttl=3600)
def create_list():
    l = [1, 2, 3]
    return l

l = create_list()
first_list_value = l[0]
l[0] = first_list_value + 1
uID = str(l[0])

@st.cache_data(ttl=3600)
def get_ext(uploaded_file):
    extype = uID+uploaded_file.name
    return extype

#===clear cache===
def reset_all():
    st.cache_data.clear()

#===avoiding deadlock===
os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
#===upload file===
@st.cache_data(ttl=3600)
def upload(file):
    papers = pd.read_csv(uploaded_file)
    
    if "About the data" in papers.columns[0]:
        papers = sf.dim(papers)
        col_dict = {'MeSH terms': 'Keywords',
        'PubYear': 'Year',
        'Times cited': 'Cited by',
        'Publication Type': 'Document Type'
        }
        papers.rename(columns=col_dict, inplace=True)

    
    return papers

@st.cache_data(ttl=3600)
def conv_txt(extype):
    if("PMID" in (uploaded_file.read()).decode()):
        uploaded_file.seek(0)
        papers = sf.medline(uploaded_file)
        print(papers)
        return papers
    col_dict = {'TI': 'Title',
            'SO': 'Source title',
            'DE': 'Author Keywords',
            'DT': 'Document Type',
            'AB': 'Abstract',
            'TC': 'Cited by',
            'PY': 'Year',
            'ID': 'Keywords Plus',
            'rights_date_used': 'Year'}
    uploaded_file.seek(0)
    papers = pd.read_csv(uploaded_file, sep='\t')
    if("htid" in papers.columns):
        papers = sf.htrc(papers)
    papers.rename(columns=col_dict, inplace=True)
    print(papers)
    return papers

@st.cache_data(ttl=3600)
def conv_json(extype):
    col_dict={'title': 'title',
    'rights_date_used': 'Year',
    }

    data = json.load(uploaded_file)
    hathifile = data['gathers']
    keywords = pd.DataFrame.from_records(hathifile)

    keywords = sf.htrc(keywords)
    keywords.rename(columns=col_dict,inplace=True)
    return keywords

@st.cache_data(ttl=3600)
def conv_pub(extype):
    if (get_ext(extype)).endswith('.tar.gz'):
        bytedata = extype.read()
        keywords = sf.readPub(bytedata)
    elif (get_ext(extype)).endswith('.xml'):
        bytedata = extype.read()
        keywords = sf.readxml(bytedata)
    return keywords

@st.cache_data(ttl=3600)
def readxls(file):
    papers = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl')
    if "About the data" in papers.columns[0]:
        papers = sf.dim(papers)
        col_dict = {'MeSH terms': 'Keywords',
        'PubYear': 'Year',
        'Times cited': 'Cited by',
        'Publication Type': 'Document Type'
        }
        papers.rename(columns=col_dict, inplace=True)
    
    return papers

def compound_label(score):
    if score >= 0.05:
        return "Positive"
    if score <= -0.05:
        return "Negative"
    return "Neutral"

def rounded_mean(frame, columns):
    return {
        column: round(float(frame[column].mean()), 3)
        for column in columns
        if column in frame.columns
    }

def render_sentiment_ai(payload, method):
    ai.render_ai_insights(
        "Sentiment Analysis",
        payload,
        f"sentiment_{method.lower()}_{uID}",
        "Explain the sentiment balance, any caveats, and what to inspect next.",
    )

#===Read data===
uploaded_file = st.file_uploader('Upload file', type=['csv', 'txt', 'json', 'tar.gz', 'xml', 'xls', 'xlsx'], on_change=reset_all, label_visibility="collapsed")

if uploaded_file is not None:
    try:
        extype = get_ext(uploaded_file)
    
        if extype.endswith('.csv'):
             papers = upload(extype) 
        elif extype.endswith('.txt'):
             papers = conv_txt(extype)
        elif extype.endswith('.json'):
            papers = conv_json(extype)
        elif extype.endswith('.tar.gz') or extype.endswith('.xml'):
            papers = conv_pub(uploaded_file)
        elif extype.endswith(('.xls', '.xlsx')):
            papers = readxls(uploaded_file)

        coldf = sorted(papers.select_dtypes(include=['object']).columns.tolist())
            
        c1, c2 = st.columns(2)
        ColCho = c1.selectbox(
                'Choose column',
                (coldf), on_change=reset_all)
        method = c2.selectbox(
            'Choose method',[
            'TextBlob','NLTKvader']
        )
        words_to_remove = c1.text_input("Remove specific words. Separate words by semicolons (;)", on_change=reset_all)        
        wordcount = c2.number_input(label = "Words displayed", min_value = 1, step = 1, value=5, on_change=reset_all)-1
        rem_copyright = c1.toggle('Remove copyright statement', value=True, on_change=reset_all)
        rem_punc = c2.toggle('Remove punctuation', value=True, on_change=reset_all)

        #===clean csv===
        @st.cache_data(ttl=3600, show_spinner=False)
        def clean_csv(extype):
            return textprep.clean_frame_column(
                papers,
                ColCho,
                remove_words=words_to_remove,
                remove_punctuation=rem_punc,
                remove_copyright=rem_copyright,
                lemmatize=False,
                output_column='Sentences__',
            )
            
        paper=clean_csv(extype) 
    
        if method == 'NLTKvader':
            analyzer = SentimentIntensityAnalyzer()

            @st.cache_resource(ttl=3600)
            def get_sentiment(text):
                score = analyzer.polarity_scores(text)
                return score

            tab1, tab2, tab3, tab4 = st.tabs(["📈 Result", "📃 Reference", "📓 Recommended Reading", "⬇️ Download Help"])
            with tab1:
                
                paper['Scores'] = paper['Sentences__'].apply(get_sentiment)

                scoreframe = pd.DataFrame()

                scoreframe['Phrase'] = pd.Series(paper['Sentences__'])

                scoreframe[['Negativity','Neutrality','Positivity','Compound']] = pd.DataFrame.from_records(paper['Scores'])

                scoreframe = scoreframe.groupby(scoreframe.columns.tolist(),as_index=False).size()

                score_summary = scoreframe.copy()
                scoreframe = scoreframe.truncate(after = wordcount)

                with st.expander("Sentence and Results"):
                    finalframe = pd.DataFrame()
                    finalframe['Sentence'] = scoreframe['Phrase']
                    finalframe[['Negativity','Neutrality','Positivity','Compound']] = scoreframe[['Negativity','Neutrality','Positivity','Compound']]
                    finalframe[['Count']] = scoreframe[['size']]

                    st.dataframe(finalframe, width="stretch")

                score_summary["Sentiment"] = score_summary["Compound"].apply(compound_label)
                distribution = score_summary.groupby("Sentiment")["size"].sum().to_dict()
                payload = ai.sentiment_payload(
                    "Sentiment Analysis",
                    ColCho,
                    method,
                    distribution,
                    mean_scores=rounded_mean(score_summary, ["Negativity", "Neutrality", "Positivity", "Compound"]),
                    record_count=int(len(paper)),
                )
                render_sentiment_ai(payload, method)

            with tab2:
                st.markdown('**Hutto, C. and Gilbert, E. (2014) ‘VADER: A Parsimonious Rule-Based Model for Sentiment Analysis of Social Media Text’, Proceedings of the International AAAI Conference on Web and Social Media, 8(1), pp. 216–225.** https://doi.org/10.1609/icwsm.v8i1.14550')

            with tab3:
                st.markdown('**Lamba, M., & Madhusudhan, M. (2021, July 31). Sentiment Analysis. Text Mining for Information Professionals, 191–211.** https://doi.org/10.1007/978-3-030-85085-2_7')

            with tab4:
                st.subheader(':blue[CSV Results]', anchor=False)
                st.text("Click Download button")
                st.markdown("![Downloading results](https://raw.githubusercontent.com/faizhalas/library-tools/main/images/sentitable.png)")
        
        elif(method == 'TextBlob'):
            
            @st.cache_resource(ttl=3600)
            def get_sentimentb(text):
                line = TextBlob(text)
                return line.sentiment

            @st.cache_resource(ttl=3600)
            def get_assessments(frame):
                text = TextBlob(str(frame))

                polar, subject, assessment = text.sentiment_assessments

                try:
                    phrase, phrasepolar, phrasesubject, unknown = assessment[0]
                except: #this only happens if assessment is empty
                    phrase, phrasepolar, phrasesubject = "empty", 0, 0

                return phrase, phrasepolar, phrasesubject

            @st.cache_data(ttl=3600)
            def mergelist(data):
                return ' '.join(data)

            @st.cache_data(ttl=3600)
            def assignscore(data):
                if data>0:
                    return "Positive"
                elif data<0:
                    return "Negative"
                else:
                    return "Neutral"

            phrases = paper['Sentences__'].apply(get_assessments)

            phraselist = phrases.to_list()

            phraseframe = pd.DataFrame(phraselist, columns =["Phrase","Polarity","Subjectivity"])

            phraseframe["Phrase"] = phraseframe["Phrase"].apply(mergelist)

            phraseframe = phraseframe.groupby(phraseframe.columns.tolist(),as_index=False).size()

            phraseframe["Score"] = phraseframe["Polarity"].apply(assignscore)

            neut = phraseframe.loc[phraseframe['Score']=="Neutral"]
            neut.reset_index(inplace = True)

            pos = phraseframe.loc[phraseframe['Score']=="Positive"]
            pos.reset_index(inplace = True)

            neg = phraseframe.loc[phraseframe['Score']=="Negative"]
            neg.reset_index(inplace = True)

            paper['Sentiment'] = paper['Sentences__'].apply(get_sentimentb)

            pos.sort_values(by=["size"], inplace = True, ascending = False, ignore_index = True)
            pos = pos.truncate(after = wordcount)

            neg.sort_values(by=["size"], inplace = True, ascending = False, ignore_index = True)
            neg = neg.truncate(after = wordcount)
        
            neut.sort_values(by=["size"], inplace = True, ascending = False, ignore_index = True)
            neut = neut.truncate(after = wordcount)

            tab1, tab2, tab3 = st.tabs(["📈 Generate visualization", "📃 Reference", "📓 Recommended Reading"])
            with tab1:
                #display tables and graphs
    
                with st.expander("Positive Sentiment"):
                    st.dataframe(pos, width="stretch")
                    figpos = px.bar(pos, x="Phrase", y="size", labels={"size": "Count", "Phrase": "Word"})      
                    st.plotly_chart(figpos, width="stretch")
    
                with st.expander("Negative Sentiment"):
                    st.dataframe(neg, width="stretch")
                    figneg = px.bar(neg, x="Phrase", y="size", labels={"size": "Count", "Phrase": "Word"}, color_discrete_sequence=["#e57d7d"])
                    st.plotly_chart(figneg, width="stretch")
    
                with st.expander("Neutral Sentiment"):
                    st.dataframe(neut, width="stretch")
                    figneut = px.bar(neut, x="Phrase", y="size", labels={"size": "Count", "Phrase": "Word"}, color_discrete_sequence=["#737a72"])
                    st.plotly_chart(figneut, width="stretch")


                with st.expander("Sentence and Results"):
                    finalframe = pd.DataFrame()
                    finalframe['Sentence'] = paper['Sentences__']
                    finalframe[['Polarity','Subjectivity']] = pd.DataFrame(paper['Sentiment'].tolist(), index = paper.index)
            
                    st.dataframe(finalframe, width="stretch")

                distribution = phraseframe.groupby("Score")["size"].sum().to_dict()
                top_terms = {
                    "positive": pos[["Phrase", "Polarity", "Subjectivity", "size"]].head(10).to_dict("records"),
                    "negative": neg[["Phrase", "Polarity", "Subjectivity", "size"]].head(10).to_dict("records"),
                    "neutral": neut[["Phrase", "Polarity", "Subjectivity", "size"]].head(10).to_dict("records"),
                }
                payload = ai.sentiment_payload(
                    "Sentiment Analysis",
                    ColCho,
                    method,
                    distribution,
                    mean_scores=rounded_mean(phraseframe, ["Polarity", "Subjectivity"]),
                    top_terms=top_terms,
                    record_count=int(len(paper)),
                )
                render_sentiment_ai(payload, method)

            with tab2:
                st.markdown('**Steven, L. et al. (2018) TextBlob: Simplified Text Processing — TextBlob 0.15.2 documentation, Readthedocs.io.** https://textblob.readthedocs.io/en/dev/')

            with tab3:
                st.markdown('**Lamba, M., & Madhusudhan, M. (2021, July 31). Sentiment Analysis. Text Mining for Information Professionals, 191–211.** https://doi.org/10.1007/978-3-030-85085-2_7')
   
    except Exception as e:
        st.error("Please ensure that your file is correct. Please contact us if you find that this is an error.", icon="🚨")
        st.stop()
