import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import time
import sys
import json
from tools import ai, runtime, sourceformat as sf, textprep, ui
#===config===
st.set_page_config(
    page_title="Coconut",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

runtime.ensure_nltk_data('wordnet', 'stopwords')

ui.apply_app_style()

ui.render_tool_menu()
ui.render_page_header("Scattertext", "Compare how words differ across sources, years, labels, or custom term groups.")
with st.expander("Before you start", expanded = True):
            
        tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download"])
        with tab1:
            st.write("Scattertext is an open-source tool designed to visualize linguistic variations between document categories in a language-independent way. It presents a scatterplot, with each axis representing the rank-frequency of a term's occurrence within a category of documents.") 
            st.divider()
            st.write('💡 The idea came from this:') 
            st.write('Kessler, J. S. (2017). Scattertext: a Browser-Based Tool for Visualizing how Corpora Differ. https://doi.org/10.48550/arXiv.1703.00565')
                
        with tab2:
            st.text("1. Put your file. Choose your preferred column to analyze.")
            st.text("2. Choose your preferred method to compare and decide words you want to remove.")
            st.text("3. Finally, you can visualize your data.")
            st.error("This app includes lemmatization and stopwords. Currently, we only offer English words.", icon="💬")
            
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
            st.subheader(':blue[Image]', anchor=False)
            st.write("Click the :blue[Download SVG] on the right side.")  
            st.divider()
            st.subheader(':blue[Scattertext Dataframe]', anchor=False)
            st.button('📥 Click to download result.', on_click=None)
            st.text("Click the Download button to get the CSV result.")


def reset_all():
    st.cache_data.clear()


@st.cache_resource(show_spinner=False)
def scattertext_lib():
    import scattertext as stx
    return stx

@st.cache_data(ttl=3600)
def get_ext(extype):
    extype = uploaded_file.name
    return extype

#===upload file===
@st.cache_data(ttl=3600)
def upload(extype):
    papers = pd.read_csv(uploaded_file)
    #lens.org
    if 'Publication Year' in papers.columns:
               papers.rename(columns={'Publication Year': 'Year', 'Citing Works Count': 'Cited by',
                                     'Publication Type': 'Document Type', 'Source Title': 'Source title'}, inplace=True)
    
    elif "About the data" in papers.columns[0]:
        papers = sf.dim(papers)
        col_dict = {'MeSH terms': 'Keywords',
        'PubYear': 'Year',
        'Times cited': 'Cited by',
        'Publication Type': 'Document Type'
        }
        papers.rename(columns=col_dict, inplace=True)

    elif "ids.openalex" in papers.columns:
        papers.rename(columns={'abstract': 'Abstract', 'title': 'Title'}, inplace=True)
    
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

@st.cache_data(ttl=3600)
def get_data(extype): 
    df_col = sorted(papers.select_dtypes(include=['object']).columns.tolist())
    list_title = [col for col in df_col if col.lower() == "title"]
    abstract_pattern = re.compile(r'abstract', re.IGNORECASE)
    list_abstract = [col for col in df_col if abstract_pattern.search(col)]

    if all(col in df_col for col in list_title) and all(col in df_col for col in list_abstract):
        selected_cols = list_abstract + list_title
    elif all(col in df_col for col in list_title):
        selected_cols = list_title
    elif all(col in df_col for col in list_abstract):
        selected_cols = list_abstract
    else:
        selected_cols = df_col

    if not selected_cols:
        selected_cols = df_col
    
    return df_col, selected_cols

@st.cache_data(ttl=3600)
def check_comparison(extype):
    comparison = ['Word-to-word', 'Manual label']
    
    if any('year' in col.lower() for col in papers.columns):
        comparison.append('Years')
    if any('source title' in col.lower() for col in papers.columns):
        comparison.append('Sources')

    comparison.sort(reverse=False)
    return comparison

#===clean csv===
@st.cache_data(ttl=3600, show_spinner=False)
def clean_csv(extype):
    return textprep.clean_frame_column(
        papers,
        ColCho,
        stop_words=stopwords.words('english'),
        remove_words=words_to_remove,
        remove_punctuation=rem_punc,
        remove_copyright=rem_copyright,
        lemmatize=True,
    )

@st.cache_data(ttl=3600)
def get_minmax(extype):
    MIN = int(papers['Year'].min())
    MAX = int(papers['Year'].max())
    GAP = MAX - MIN
    MID = round((MIN + MAX) / 2)
    return MIN, MAX, GAP, MID

@st.cache_data(ttl=3600)
def running_scattertext(cat_col, catname, noncatname):
    try:
        stx = scattertext_lib()
        corpus = stx.CorpusFromPandas(filtered_df,         
                                category_col = cat_col,
                                text_col = ColCho,
                                nlp = stx.whitespace_nlp_with_sentences,
                                ).build().get_unigram_corpus().remove_infrequent_words(minimum_term_count = min_term)        
                                
        #table results
        disp = stx.Dispersion(corpus)
        disp_df = disp.get_df()

        disp_csv = disp_df.to_csv(index=False).encode('utf-8')
            
        try:
            html = stx.produce_scattertext_explorer(corpus,
                                                category = catname,
                                                category_name = catname,
                                                not_category_name = noncatname,
                                                width_in_pixels = 900,
                                                minimum_term_frequency = 0,
                                                metadata = filtered_df['Title'],
                                                save_svg_button=True)
    
        except KeyError:
            html = stx.produce_scattertext_explorer(corpus,
                                                category = catname,
                                                category_name = catname,
                                                not_category_name = noncatname,
                                                width_in_pixels = 900,
                                                minimum_term_frequency = 0,
                                                save_svg_button=True)

        return disp_df, disp_csv, html 

    except ValueError:
        st.warning('Please decrease the Minimum term count in the advanced settings.', icon="⚠️")
        st.stop()

@st.cache_data(ttl=3600)
def df_w2w(search_terms1, search_terms2):
    selected_col = [ColCho]
    def matching_rows(terms):
        if not terms:
            return paper.iloc[0:0].copy()
        pattern = r'\b(?:' + '|'.join(re.escape(term) for term in terms) + r')\b'
        return paper[paper[selected_col[0]].astype(str).str.contains(pattern, case=False, na=False, regex=True)].copy()

    dfs1 = matching_rows(search_terms1)
    dfs1['Topic'] = 'First Term'
    dfs1 = dfs1.drop_duplicates()
        
    dfs2 = matching_rows(search_terms2)
    dfs2['Topic'] = 'Second Term'
    dfs2 = dfs2.drop_duplicates()
    filtered_df = pd.concat([dfs1, dfs2], ignore_index=True)
    
    return dfs1, dfs2, filtered_df

@st.cache_data(ttl=3600)
def df_sources(stitle1, stitle2):
    dfs1 = paper[paper['Source title'].str.contains(stitle1, case=False, na=False)]
    dfs1['Topic'] = stitle1
    dfs2 = paper[paper['Source title'].str.contains(stitle2, case=False, na=False)]
    dfs2['Topic'] = stitle2
    filtered_df = pd.concat([dfs1, dfs2], ignore_index=True)

    return filtered_df  

@st.cache_data(ttl=3600)
def df_years(first_range, second_range):
    first_range_filter_df = paper[(paper['Year'] >= first_range[0]) & (paper['Year'] <= first_range[1])].copy()
    first_range_filter_df['Topic Range'] = 'First range'
        
    second_range_filter_df = paper[(paper['Year'] >= second_range[0]) & (paper['Year'] <= second_range[1])].copy()
    second_range_filter_df['Topic Range'] = 'Second range'
        
    filtered_df = pd.concat([first_range_filter_df, second_range_filter_df], ignore_index=True)

    return filtered_df 

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
    
        df_col, selected_cols = get_data(extype)
        comparison = check_comparison(extype)
    
        #Menu
        c1, c2, c3 = st.columns([4,0.1,4])
        ColCho = c1.selectbox(
                'Choose column to analyze',
                (selected_cols), on_change=reset_all)
    
        c2.write('')
    
        compare = c3.selectbox(
                'Type of comparison',
                (comparison), on_change=reset_all)
        
        with st.expander("🧮 Show advance settings"):
            y1, y2 = st.columns([8,2])
            t1, t2 = st.columns([3,3])
            words_to_remove = y1.text_input('Input your text', on_change=reset_all, placeholder='Remove specific words. Separate words by semicolons (;)')
            min_term = y2.number_input("Minimum term count", min_value=0, max_value=10, value=3, step=1, on_change=reset_all)
            rem_copyright = t1.toggle('Remove copyright statement', value=True, on_change=reset_all)
            rem_punc = t2.toggle('Remove punctuation', value=False, on_change=reset_all)
    
        st.info('Scattertext is an expensive process when dealing with a large volume of text with our existing resources. Please kindly wait until the visualization appears.', icon="ℹ️")
        
        paper = clean_csv(extype)
    
        tab1, tab2, tab3 = st.tabs(["📈 Generate visualization", "📃 Reference", "📓 Recommended Reading"])
    
        with tab1:
             #===visualization===
            if compare == 'Word-to-word':
                col1, col2, col3 = st.columns([4,0.1,4])
                text1 = col1.text_input('First Term', on_change=reset_all, placeholder='put comma if you have more than one')
                search_terms1 = [term.strip() for term in text1.split(",") if term.strip()]
                col2.write('')
                text2 = col3.text_input('Second Term', on_change=reset_all, placeholder='put comma if you have more than one')
                search_terms2 = [term.strip() for term in text2.split(",") if term.strip()]
                
                dfs1, dfs2, filtered_df = df_w2w(search_terms1, search_terms2)
        
                if dfs1.empty and dfs2.empty:
                    st.warning('We cannot find anything in your document.', icon="⚠️")
                elif dfs1.empty:
                    st.warning(f'We cannot find {text1} in your document.', icon="⚠️")
                elif dfs2.empty:
                    st.warning(f'We cannot find {text2} in your document.', icon="⚠️")
                else:
                    with st.spinner('Processing. Please wait until the visualization comes up'):
                        disp_df, disp_csv, html = running_scattertext('Topic', 'First Term', 'Second Term')
        
            elif compare == 'Manual label':
                col1, col2, col3 = st.columns(3)
        
                df_col_sel = sorted([col for col in paper.columns.tolist()])
                     
                column_selected = col1.selectbox(
                    'Choose column',
                    (df_col_sel), on_change=reset_all)
        
                list_words = paper[column_selected].dropna()  # remove NaN
                list_words = [w for w in list_words if str(w).strip() != ""]  # remove empty strings
                list_unique = sorted(set(list_words))
                
                if column_selected is not None:
                    label1 = col2.selectbox(
                        'Choose first label',
                        (list_unique), on_change=reset_all)
        
                    default_index = 0 if len(list_unique) == 1 else 1
                    label2 = col3.selectbox(
                        'Choose second label',
                        (list_unique), on_change=reset_all, index=default_index)
        
                filtered_df = paper[paper[column_selected].isin([label1, label2])].reset_index(drop=True)
                
                with st.spinner('Processing. Please wait until the visualization comes up'):
                    disp_df, disp_csv, html = running_scattertext(column_selected, label1, label2)
        
            elif compare == 'Sources':
                col1, col2, col3 = st.columns([4,0.1,4])
        
                unique_stitle = set()
                unique_stitle.update(paper['Source title'].dropna())
                list_stitle = sorted(list(unique_stitle))
                     
                stitle1 = col1.selectbox(
                    'Choose first label',
                    (list_stitle), on_change=reset_all)
                col2.write('')
                default_index = 0 if len(list_stitle) == 1 else 1
                stitle2 = col3.selectbox(
                    'Choose second label',
                    (list_stitle), on_change=reset_all, index=default_index)
        
                filtered_df = df_sources(stitle1, stitle2)
        
                with st.spinner('Processing. Please wait until the visualization comes up'):
                    disp_df, disp_csv, html = running_scattertext('Source title', stitle1, stitle2)
        
            elif compare == 'Years':
                col1, col2, col3 = st.columns([4,0.1,4])
                
                MIN, MAX, GAP, MID = get_minmax(extype)
                if (GAP != 0):
                    first_range = col1.slider('First Range', min_value=MIN, max_value=MAX, value=(MIN, MID), on_change=reset_all)
                    col2.write('')
                    second_range = col3.slider('Second Range', min_value=MIN, max_value=MAX, value=(MID, MAX), on_change=reset_all)
                
                    filtered_df = df_years(first_range, second_range)
        
                    with st.spinner('Processing. Please wait until the visualization comes up'):
                        disp_df, disp_csv, html = running_scattertext('Topic Range', 'First range', 'Second range')
                        
                else:
                    st.write('You only have data in ', (MAX))

            if html:
                st.toast('Process completed', icon='🎉')
                time.sleep(1)
                st.toast('Visualizing', icon='⏳')
                components.html(ui.themed_embedded_html(html), height=1200, scrolling=True)
    
                st.download_button(
                    "📥 Click to download result",
                    disp_csv,
                    "scattertext_dataframe.csv",
                    "text/csv",
                    on_click="ignore")

                payload = ai.table_payload(
                    "Scattertext",
                    "Term dispersion table",
                    disp_df,
                    metadata={
                        "selected_column": ColCho,
                        "comparison_type": compare,
                        "minimum_term_count": min_term,
                        "compared_rows": int(len(filtered_df)) if "filtered_df" in locals() else None,
                    },
                )
                ai.render_ai_insights(
                    "Scattertext",
                    payload,
                    f"scattertext_{compare.lower().replace(' ', '_')}",
                    "Explain which terms separate the compared groups and what caveats matter.",
                )
    
        with tab2:
            st.markdown('**Jason Kessler. 2017. Scattertext: a Browser-Based Tool for Visualizing how Corpora Differ. In Proceedings of ACL 2017, System Demonstrations, pages 85–90, Vancouver, Canada. Association for Computational Linguistics.** https://doi.org/10.48550/arXiv.1703.00565')
    
        with tab3:
            st.markdown('**Sánchez-Franco, M. J., & Rey-Tienda, S. (2023). The role of user-generated content in tourism decision-making: an exemplary study of Andalusia, Spain. Management Decision, 62(7).** https://doi.org/10.1108/md-06-2023-0966')
            st.markdown('**Marrone, M., & Linnenluecke, M.K. (2020). Interdisciplinary Research Maps: A new technique for visualizing research topics. PLoS ONE, 15.** https://doi.org/10.1371/journal.pone.0242283')
            st.markdown('**Moreno, A., & Iglesias, C.A. (2021). Understanding Customers’ Transport Services with Topic Clustering and Sentiment Analysis. Applied Sciences.** https://doi.org/10.3390/app112110169')
            st.markdown('**Santosa, F. A. (2025). Artificial Intelligence in Library Studies: A Textual Analysis. JLIS.It, 16(1).** https://doi.org/10.36253/jlis.it-626')

    except NameError:
        pass
    
    except Exception as e:
        st.error("Please ensure that your file is correct. Please contact us if you find that this is an error.", icon="🚨")
        st.stop()
