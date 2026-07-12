import streamlit as st
import pandas as pd
import numpy as np
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from pprint import pprint
import pickle
import streamlit.components.v1 as components
from io import StringIO
from nltk.stem.snowball import SnowballStemmer
import csv
import sys
import json
from tools import ai, runtime, sourceformat as sf, ui
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
ui.render_page_header("Keywords Stem", "Clean, stem, and normalize keyword fields for downstream analysis.")
with st.expander("Before you start", expanded = True):
    tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download Result"])
    with tab1:
        st.write("This approach is effective for locating basic words and aids in catching the true meaning of the word, which can lead to improved semantic analysis and comprehension of the text. Some people find it difficult to check keywords before performing bibliometrics (using software such as VOSviewer and Bibliometrix). This strategy makes it easy to combine and search for fundamental words from keywords, especially if you have a large number of keywords. To do stemming or lemmatization on other text, change the column name to 'Keyword' in your file.")
        st.divider()
        st.write('💡 The idea came from this:')
        st.write('Santosa, F. A. (2022). Prior steps into knowledge mapping: Text mining application and comparison. Issues in Science and Technology Librarianship, 102. https://doi.org/10.29173/istl2736')
        
    with tab2:
        st.text("1. Put your file.")
        st.text("2. Choose your preferable method. Picture below may help you to choose wisely.")
        st.markdown("![Source: https://studymachinelearning.com/stemming-and-lemmatization/](https://studymachinelearning.com/wp-content/uploads/2019/09/stemmin_lemm_ex-1.png)")
        st.text('Source: https://studymachinelearning.com/stemming-and-lemmatization/')
        st.text("3. Now you need to select what kind of keywords you need.")
        st.text("4. Finally, you can download and use the file on VOSviewer, Bibliometrix, or put it on OpenRefine to get better result!")
        st.error("Please check what has changed. It's possible some keywords failed to find their roots.", icon="🚨")
        
    with tab3:
        st.code("""
        +----------------+------------------------+---------------------------------+
        |     Source     |       File Type        |             Column              |
        +----------------+------------------------+---------------------------------+
        | Scopus         | Comma-separated values | Author Keywords                 |
        |                | (.csv)                 | Index Keywords                  |
        +----------------+------------------------+---------------------------------+
        | Web of Science | Tab delimited file     | Author Keywords                 |
        |                | (.txt)                 | Keywords Plus                   |
        +----------------+------------------------+---------------------------------+
        | Lens.org       | Comma-separated values | Keywords (Scholarly Works)      |
        |                | (.csv)                 |                                 |
        +----------------+------------------------+---------------------------------+
        | Dimensions     | Comma-separated values | MeSH terms                      |
        |                | (.csv)                 |                                 |
        +----------------+------------------------+---------------------------------+
        | OpenAlex       | Comma-separated values | Keywords                        |
        |                | (.csv)                 |                                 |
        +----------------+------------------------+---------------------------------+
        | Other          | .csv .xls .xlsx        | Change your column to 'Keyword' |
        +----------------+------------------------+---------------------------------+
        | Hathitrust     | .json                  | htid (Hathitrust ID)            |
        +----------------+------------------------+---------------------------------+
        """, language=None)

    with tab4:
        st.subheader(':blue[Result]', anchor=False)
        st.button('Click to download result 👈.')
        st.text("Go to Result and click Download button.")  

        st.divider()
        st.subheader(':blue[List of Keywords]', anchor=False)
        st.button('Click to download keywords 👈.')
        st.text("Go to List of Keywords and click Download button.")  


def reset_data():
     st.cache_data.clear()

#===check filetype===
@st.cache_data(ttl=3600)
def get_ext(extype):
    extype = uploaded_file.name
    return extype
     
#===upload===
@st.cache_data(ttl=3600)
def upload(extype):
    keywords = pd.read_csv(uploaded_file)

    if "About the data" in keywords.columns[0]:
        keywords = sf.dim(keywords)
        col_dict = {'MeSH terms': 'Keywords',
        'PubYear': 'Year',
        'Times cited': 'Cited by',
        'Publication Type': 'Document Type'
        }
        keywords.rename(columns=col_dict, inplace=True)

    elif "ids.openalex" in keywords.columns:
        keywords.rename(columns={'keywords.display_name': 'Keywords'}, inplace=True)
        keywords["Keywords"] = keywords["Keywords"].astype(str).str.replace("|", "; ")

    return keywords
    
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
def rev_conv_txt(extype):
    col_dict_rev = {'Title': 'TI',
            'Source title': 'SO',
            'Author Keywords': 'DE',
            'Keywords Plus': 'ID'}
    keywords.rename(columns=col_dict_rev, inplace=True)
    return keywords

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
    list_of_column_key = list(keywords.columns)
    list_of_column_key = [k for k in list_of_column_key if 'Keyword' in k]
    return list_of_column_key

uploaded_file = st.file_uploader('Upload file', type=['csv', 'txt', 'json', 'tar.gz', 'xml', 'xls', 'xlsx'], on_change=reset_data, label_visibility="collapsed")

if uploaded_file is not None:
    try:
        extype = get_ext(uploaded_file)
        if extype.endswith('.csv'):
            keywords = upload(extype)        
        elif extype.endswith('.txt'):
            keywords = conv_txt(extype)
        elif extype.endswith('.json'):
            keywords = conv_json(extype)
        elif extype.endswith('.tar.gz') or extype.endswith('.xml'):
            keywords = conv_pub(uploaded_file)
        elif extype.endswith(('.xls', '.xlsx')):
            keywords = readxls(uploaded_file)

        list_of_column_key = get_data(extype)
    
        col1, col2 = st.columns(2)
        with col1:
            method = st.selectbox(
                'Choose method',
                ('Lemmatization', 'Stemming'), on_change=reset_data)
        with col2:
            keyword = st.selectbox(
                'Choose column',
                (list_of_column_key), on_change=reset_data)
    
        @st.cache_data(ttl=3600)
        def clean_keyword(extype):      
            global keyword, keywords
            try:
                key = keywords[keyword]
            except KeyError:
                st.error('Error: Please check your Author/Index Keywords column.')
                st.stop()
            keywords = keywords.replace(np.nan, '', regex=True)
            keywords[keyword] = keywords[keyword].astype(str)
            keywords[keyword] = keywords[keyword].map(lambda x: re.sub('-', ' ', x))
            keywords[keyword] = keywords[keyword].map(lambda x: re.sub('; ', ' ; ', x))
            keywords[keyword] = keywords[keyword].map(lambda x: x.lower())
            
            #===Keywords list===
            key = key.dropna()
            key = pd.concat([key.str.split('; ', expand=True)], axis=1)
            key = pd.Series(np.ravel(key)).dropna().drop_duplicates().sort_values().reset_index()
            key[0] = key[0].map(lambda x: re.sub('-', ' ', x))
            key['new']=key[0].map(lambda x: x.lower())
    
            return keywords, key
         
        #===stem/lem===
        @st.cache_data(ttl=3600)
        def Lemmatization(extype):
            lemmatizer = WordNetLemmatizer()
            def lemmatize_words(text):
                words = text.split()
                words = [lemmatizer.lemmatize(word) for word in words]
                return ' '.join(words)
            keywords[keyword] = keywords[keyword].apply(lemmatize_words)
            key['new'] = key['new'].apply(lemmatize_words)
            keywords[keyword] = keywords[keyword].map(lambda x: re.sub(' ; ', '; ', x))
            return keywords, key
                    
        @st.cache_data(ttl=3600)
        def Stemming(extype):
            stemmer = SnowballStemmer("english")
            def stem_words(text):
                words = text.split()
                words = [stemmer.stem(word) for word in words]
                return ' '.join(words)
            keywords[keyword] = keywords[keyword].apply(stem_words)
            key['new'] = key['new'].apply(stem_words)
            keywords[keyword] = keywords[keyword].map(lambda x: re.sub(' ; ', '; ', x))
            return keywords, key
         
        keywords, key = clean_keyword(extype) 
         
        if method == 'Lemmatization':
            keywords, key = Lemmatization(extype)
        else:
            keywords, key = Stemming(extype)
                
        st.write('Congratulations! 🤩 You choose',keyword ,'with',method,'method. Now, you can easily download the result by clicking the button below')
        st.divider()
              
        #===show & download csv===
        tab1, tab2, tab3, tab4 = st.tabs(["📥 Result", "📥 List of Keywords", "📃 Reference", "📃 Recommended Reading"])
         
        with tab1:
            st.dataframe(keywords, width="stretch", hide_index=True)
            @st.cache_data(ttl=3600)
            def convert_df(extype):
                return keywords.to_csv(index=False).encode('utf-8')
             
            @st.cache_data(ttl=3600)
            def convert_txt(extype):
                return keywords.to_csv(index=False, sep='\t', lineterminator='\r').encode('utf-8')
             
            if extype.endswith('.csv'):
                csv = convert_df(extype)
                st.download_button(
                    "Click to download result 👈",
                    csv,
                    "result.csv",
                    "text/csv")
      
            elif extype.endswith('.txt'):
                keywords = rev_conv_txt(extype)
                txt = convert_txt(extype)
                st.download_button(
                    "Click to download result 👈",
                    txt,
                    "result.txt",
                    "text/csv")    
             
        with tab2:
            @st.cache_data(ttl=3600)
            def table_keyword(extype):
                keytab = key.drop(['index'], axis=1).rename(columns={0: 'label'})
                return keytab
                
            #===coloring the same keywords===
            @st.cache_data(ttl=3600)
            def highlight_cells(value):
                if keytab['new'].duplicated(keep=False).any() and keytab['new'].duplicated(keep=False)[keytab['new'] == value].any():
                    return 'background-color: yellow'
                return '' 
            keytab = table_keyword(extype) 
            st.dataframe(keytab.style.map(highlight_cells, subset=['new']), width="stretch", hide_index=True)

            changed_count = int((keytab['label'] != keytab['new']).sum())
            duplicate_map = keytab[keytab['new'].duplicated(keep=False)].sort_values('new')
            ai_frame = duplicate_map if not duplicate_map.empty else keytab
            payload = ai.table_payload(
                "Keywords Stem",
                "Keyword normalization map",
                ai_frame,
                metadata={
                    "keyword_column": keyword,
                    "normalization_method": method,
                    "total_unique_keywords": int(len(keytab)),
                    "changed_keywords": changed_count,
                    "collapsed_keyword_rows": int(len(duplicate_map)),
                },
            )
            ai.render_ai_insights(
                "Keywords Stem",
                payload,
                f"keywords_stem_{keyword}_{method}",
                "Explain which normalized keyword forms deserve human review before export.",
            )
                      
            @st.cache_data(ttl=3600)
            def convert_dfs(extype):
                return key.to_csv(index=False).encode('utf-8')
                    
            csv = convert_dfs(extype)
    
            st.download_button(
                "Click to download keywords 👈",
                csv,
                "keywords.csv",
                "text/csv")
                 
        with tab3:
            st.markdown('**Santosa, F. A. (2023). Prior steps into knowledge mapping: Text mining application and comparison. Issues in Science and Technology Librarianship, 102.** https://doi.org/10.29173/istl2736')
         
        with tab4:
            st.markdown('**Beri, A. (2021, January 27). Stemming vs Lemmatization. Medium.** https://towardsdatascience.com/stemming-vs-lemmatization-2daddabcb221')
            st.markdown('**Khyani, D., Siddhartha B S, Niveditha N M, &amp; Divya B M. (2020). An Interpretation of Lemmatization and Stemming in Natural Language Processing. Journal of University of Shanghai for Science and Technology , 22(10), 350–357.**  https://jusst.org/an-interpretation-of-lemmatization-and-stemming-in-natural-language-processing/')
            st.markdown('**Lamba, M., & Madhusudhan, M. (2021, July 31). Text Pre-Processing. Text Mining for Information Professionals, 79–103.** https://doi.org/10.1007/978-3-030-85085-2_3')         
            
    except Exception as e:
        st.error("Please ensure that your file is correct. Please contact us if you find that this is an error.", icon="🚨")
        st.stop()
