#===import module===
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import sys
from tools import ai, sourceformat as sf, ui


#===config===
st.set_page_config(
    page_title="Coconut",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ui.apply_app_style()

ui.render_tool_menu()
ui.render_page_header("Sunburst Visualization", "Explore publication types, sources, and years in a layered visual summary.")
with st.expander("Before you start", expanded = True):
     
        tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download"])
        with tab1:
            st.write("Sunburst's ability to present a thorough and intuitive picture of complex hierarchical data is an essential benefit. Librarians can easily browse and grasp the relationships between different levels of the hierarchy by employing sunburst visualizations. Sunburst visualizations can also be interactive, letting librarians and users drill down into certain categories or subcategories for further information. This interactive and visually appealing depiction improves the librarian's understanding of the collection and provides users with an engaging and user-friendly experience, resulting in improved information retrieval and decision-making.")
            
        with tab2:
            st.text("1. Put your CSV file.")
            st.text("2. You can set the range of years to see how it changed.")
            st.text("3. The sunburst has 3 levels. The inner circle is the type of data, meanwhile, the middle is the source title and the outer is the year the article was published.")
            st.text("4. The size of the slice depends on total documents. The average of inner and middle levels is calculated by formula below:")
            st.code('avg = sum(a * weights) / sum(weights)', language='python')
            
        with tab3:
            st.code("""
            +----------------+------------------------+--------------------------------------+
            |     Source     |       File Type        |     Column                           |
            +----------------+------------------------+--------------------------------------+
            | Scopus         | Comma-separated values | Source title,                        |
            |                | (.csv)                 | Document Type,                       |
            +----------------+------------------------| Cited by, Year                       |
            | Web of Science | Tab delimited file     |                                      |
            |                | (.txt)                 |                                      |
            +----------------+------------------------+--------------------------------------+
            | Lens.org       | Comma-separated values | Publication Year,                    |
            |                | (.csv)                 | Publication Type,                    | 
            |                |                        | Source Title,                        |
            |                |                        | Citing Works Count                   |
            +----------------+------------------------+--------------------------------------+
            | OpenAlex       | Comma-separated values | publication_year,                    |
            |                | (.csv)                 | cited_by_count,                      | 
            |                |                        | type,                                |
            |                |                        | primary_location.source.display_name |
            +----------------+------------------------+--------------------------------------+
            | Hathitrust     | .json                  | htid(Hathitrust ID)                  |
            +----------------+------------------------+--------------------------------------+
            """, language=None)          

        with tab4:  
            st.subheader(':blue[Sunburst]', anchor=False)
            st.text("Click the camera icon on the top right menu (you may need to hover your cursor within the visualization)")
            st.markdown("![Downloading visualization](https://raw.githubusercontent.com/faizhalas/library-tools/main/images/download_bertopic.jpg)")
            st.subheader(":blue[Download table as CSV]", anchor=False)
            st.text("Hover cursor over table, and click download arrow")
            st.markdown("![Downloading table](https://raw.githubusercontent.com/faizhalas/library-tools/refs/heads/main/images/tablenetwork.png)")
    

#===clear cache===
def reset_all():
    st.cache_data.clear()

#===check type===
@st.cache_data(ttl=3600)
def get_ext(extype):
    extype = uploaded_file.name
    return extype

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
        papers.rename(columns={'publication_year': 'Year', 'cited_by_count': 'Cited by',
                               'type': 'Document Type', 'primary_location.source.display_name': 'Source title'}, inplace=True)
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
    'content_provider_code': 'Document Type',
    'Keywords':'Source title'
    }
    keywords = pd.read_json(uploaded_file)
    keywords = sf.htrc(keywords)
    keywords['Cited by'] = keywords.groupby(['Keywords'])['Keywords'].transform('size')
    keywords.rename(columns=col_dict,inplace=True)
    return keywords

def conv_pub(extype):
    if (get_ext(extype)).endswith('.tar.gz'):
        bytedata = extype.read()
        keywords = sf.readPub(bytedata)
    elif (get_ext(extype)).endswith('.xml'):
        bytedata = extype.read()
        keywords = sf.readxml(bytedata)
    keywords['Cited by'] = keywords.groupby(['Keywords'])['Keywords'].transform('size')
    st.write(keywords)
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

        @st.cache_data(ttl=3600)
        def get_minmax(extype):
            extype = extype
            MIN = int(papers['Year'].min())
            MAX = int(papers['Year'].max())
            MIN1 = int(papers['Cited by'].min())
            MAX1 = int(papers['Cited by'].max())
            GAP = MAX - MIN
            unique_stitle = set()
            unique_stitle.update(papers['Source title'].dropna())
            list_stitle = sorted(list(unique_stitle))
            return papers, MIN, MAX, GAP, MIN1, MAX1, list_stitle

        tab1, tab2 = st.tabs(["📈 Generate visualization", "📓 Recommended Reading"])
        
        with tab1:    
            #===sunburst===
            try:
                papers, MIN, MAX, GAP, MIN1, MAX1, list_stitle = get_minmax(extype)
            except KeyError:
                st.error('Error: Please check again your columns.')
                st.stop()

            stitle = st.selectbox('Focus on', (list_stitle), index=None, on_change=reset_all)
            col1, col2 = st.columns(2)
            invert_keys = False
            keylist = []
            select_col = 'Source title'
            
            if (GAP != 0):
                YEAR = col1.slider('Year', min_value=MIN, max_value=MAX, value=(MIN, MAX))
                KEYLIM = col2.slider('Cited By Count',min_value = MIN1, max_value = MAX1, value = (MIN1,MAX1))
                with st.expander("Filtering settings"):
                    invert_keys = st.toggle("Invert keys")
                    filtered_keys = st.text_input("Filter words in source, seperate with semicolon (;)", value = "\n", on_change=None) 
                    select_col = st.selectbox("Column to filter from", (list(papers)))
                keylist = filtered_keys.split(";")
                
            else:
                col1.write('You only have data in ', (MAX))
                YEAR = (MIN, MAX)
                KEYLIM = col2.slider('Cited By Count',min_value = MIN1, max_value = MAX1, value = (MIN1,MAX1))
                
            @st.cache_data(ttl=3600)
            def listyear(extype):
                global papers
                years = list(range(YEAR[0],YEAR[1]+1))
                cited = list(range(KEYLIM[0],KEYLIM[1]+1))
                if stitle:
                    papers = papers[papers['Source title'].str.contains(stitle, case=False, na=False)]
                papers = papers.loc[papers['Year'].isin(years)]
                papers = papers.loc[papers['Cited by'].isin(cited)]
                papers['Cited by'] = papers['Cited by'].fillna(0)
                return years, papers
            
            @st.cache_data(ttl=3600)
            def vis_sunburst(extype):
                data = papers.copy()
                data['Cited by'] = data['Cited by'].fillna(0)

                #filtering
                filter_pattern = '|'.join([word.strip() for word in keylist if word.strip()])
                if filter_pattern:
                    if(invert_keys):
                        data = data[data[select_col].astype(str).str.contains(filter_pattern, na=False)]
                    else:
                        data = data[~data[select_col].astype(str).str.contains(filter_pattern, na=False)]

                vis = pd.DataFrame()
                vis[['doctype','source','citby','year']] = data[['Document Type','Source title','Cited by','Year']]
                viz=vis.groupby(['doctype', 'source', 'year'])['citby'].agg(['sum','count']).reset_index()  
                viz.rename(columns={'sum': 'cited by', 'count': 'total docs'}, inplace=True)
        
                fig = px.sunburst(viz, path=['doctype', 'source', 'year'], values='total docs',
                              color='cited by', 
                              color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(viz['cited by'], weights=viz['total docs']))
                fig.update_layout(height=800, width=1200)
                return fig, viz
            
            years, papers = listyear(extype)
    
            
            if {'Document Type','Source title','Cited by','Year'}.issubset(papers.columns):
              
                if st.button("Submit", on_click = reset_all):
                    fig, viz = vis_sunburst(extype)
                    st.plotly_chart(fig, height=800, width=1200)
                    st.dataframe(viz, width="stretch", hide_index=True)

                    payload = ai.table_payload(
                        "Sunburst Visualization",
                        "Document type, source, and year hierarchy",
                        viz.sort_values(["total docs", "cited by"], ascending=False),
                        metadata={
                            "year_range": list(YEAR),
                            "cited_by_range": list(KEYLIM),
                            "source_focus": stitle or "All sources",
                            "filter_column": select_col,
                        },
                    )
                    ai.render_ai_insights(
                        "Sunburst Visualization",
                        payload,
                        f"sunburst_{MIN}_{MAX}",
                        "Explain the dominant hierarchy patterns and what source/year/document-type combinations stand out.",
                    )
               
            else:
                st.error('We require these columns: Document Type, Source title, Cited by, Year', icon="🚨")
        
        with tab2:
            st.markdown('**numpy.average — NumPy v1.24 Manual. (n.d.). Numpy.Average — NumPy v1.24 Manual.** https://numpy.org/doc/stable/reference/generated/numpy.average.html')
            st.markdown('**Sunburst. (n.d.). Sunburst Charts in Python.** https://plotly.com/python/sunburst-charts/')
            
    except:
        st.error("Please ensure that your file is correct. Please contact us if you find that this is an error.", icon="🚨")
        st.stop()
