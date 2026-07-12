#import module
import streamlit as st
from tools import samples, ui, workbench

#===config===
st.set_page_config(
    page_title="Coconut",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="collapsed"    
)

ui.apply_app_style()
ui.render_theme_toggle()

ui.render_page_header("Coconut Libtool", "All-in-one data mining and textual analysis tool for everyone.", "Where Text Meets Insights")

#===page===
mt1, mt2, mt3 = st.tabs(["Guided Start", "Tool Menu", "How to"])

with mt1:
    st.subheader("What are you trying to do?", anchor=False)
    st.caption("Choose a goal first. Coconut will point you toward the best starting tool.")

    workflows = [
        ("Understand my file", "Inspect rows, columns, missing values, text fields, and recommended next tools.", "pages/12 Corpus Overview.py", "🔎"),
        ("Clean my data", "Normalize spacing, blank values, years, and duplicate records before analysis.", "pages/13 Data Cleaner.py", "🧹"),
        ("Map research trends", "Summarize years, sources, document types, keywords, and citation signals.", "pages/14 Bibliometric Overview.py", "📚"),
        ("Find rising terms", "Track selected terms over time or detect sudden bursts of attention.", "pages/17 Term Keyword Evolution.py", "📈"),
        ("Search by meaning", "Find records related to a concept even when the exact words differ.", "pages/16 Semantic Search.py", "🔍"),
        ("Explain results with AI", "Use aggregate results and careful caveats to interpret a dataset or method.", "pages/18 Ask Your Dataset.py", "💬"),
        ("Summarize text", "Create concise summaries, key points, and takeaways from abstracts or text columns.", "pages/21 Text Summarization.py", "✂️"),
        ("Make quick visuals", "Create word clouds, histograms, and pie charts from selected columns.", "pages/9 WordCloud.py", "☁️"),
        ("Write a report", "Turn methods, findings, caveats, and optional dataset context into a report.", "pages/19 AI Report Builder.py", "📝"),
    ]

    for row_start in range(0, len(workflows), 4):
        cols = st.columns(4)
        for offset, (col, (title, body, page, icon)) in enumerate(
            zip(cols, workflows[row_start:row_start + 4])
        ):
            with col:
                with st.container(
                    border=True,
                    height=260,
                    key=f"workflow_card_{row_start + offset}",
                ):
                    workbench.render_workflow_card(title, body, page, icon)

    st.divider()
    st.subheader("Try It Without Your Own File", anchor=False)
    sample_cols = st.columns(len(samples.names()))
    for col, sample_name in zip(sample_cols, samples.names()):
        with col:
            st.download_button(
                f"Download {sample_name}",
                samples.csv_bytes(sample_name),
                f"{sample_name.lower().replace(' ', '_')}.csv",
                "text/csv",
                width="stretch",
            )

with mt2:
    tools = [
        ("Scattertext", "Compare how language differs between two groups.", "pages/1 Scattertext.py", None, "🔀"),
        ("Topic Modeling", "Discover themes across abstracts and other text fields.", "pages/2 Topic Modeling.py", None, "🧩"),
        ("Bidirected Network", "Map two-way keyword relationships.", "pages/3 Bidirected Network.py", None, "🕸️"),
        ("Sunburst", "Explore document type, source, and year at once.", "pages/4 Sunburst.py", None, "☀️"),
        ("Burst Detection", "Find terms that spike across time.", "pages/5 Burst Detection.py", None, "🚀"),
        ("Keywords Stem", "Normalize keyword fields for cleaner analysis.", "pages/6 Keywords Stem.py", None, "🌱"),
        ("Sentiment Analysis", "Score and review positive, negative, and neutral text.", "pages/7 Sentiment Analysis.py", None, "😊"),
        ("Shifterator", "Compare word contribution shifts between text groups.", "pages/8 Shifterator.py", None, "⚖️"),
        ("WordCloud", "Create a fast visual summary of frequent terms.", "pages/9 WordCloud.py", None, "☁️"),
        ("Histogram", "Compare frequent values from a selected column.", "pages/10 Histogram.py", None, "📊"),
        ("Pie Chart", "Show each frequent value as a share of the whole.", "pages/11 Pie Chart.py", None, "🥧"),
        ("Corpus Overview", "Profile a dataset before choosing an analysis path.", "pages/12 Corpus Overview.py", None, "🔎"),
        ("Data Cleaner", "Find duplicates, missing values, and export cleaner data.", "pages/13 Data Cleaner.py", None, "🧹"),
        ("Bibliometric Overview", "Summarize years, sources, document types, and keywords.", "pages/14 Bibliometric Overview.py", None, "📚"),
        ("Named Entity Extraction", "Extract people, organizations, places, and dates.", "pages/15 Named Entity Extraction.py", None, "🏷️"),
        ("Semantic Search", "Rank records by similarity to a search query.", "pages/16 Semantic Search.py", None, "🔍"),
        ("Term/Keyword Evolution", "Track how selected terms and keywords rise or fade across years.", "pages/17 Term Keyword Evolution.py", None, "📈"),
        ("Ask Your Dataset", "Ask AI questions using a privacy-first dataset profile.", "pages/18 Ask Your Dataset.py", None, "💬"),
        ("AI Report Builder", "Turn notes and aggregate results into a polished report.", "pages/19 AI Report Builder.py", None, "📝"),
        ("AI Method Explainer", "Explain methods, settings, and interpretation caveats.", "pages/20 AI Method Explainer.py", None, "🧠"),
        ("Text Summarization", "Summarize abstracts, articles, notes, or selected text columns.", "pages/21 Text Summarization.py", None, "✂️"),
    ]

    for row_start in range(0, len(tools), 3):
        cols = st.columns(3)
        for col, tool in zip(cols, tools[row_start:row_start + 3]):
            with col:
                ui.render_home_tool_card(*tool)

with mt3:
    st.header("Before you start", anchor=False)
    option = st.selectbox(
        'Please choose....',
        ('Scattertext', 'Topic Modeling', 'Bidirected Network', 'Sunburst', 'Burst Detection', 'Keyword Stem', 'Sentiment Analysis', 'Shifterator', 'WordCloud', 'Histogram', 'Pie Chart',
         'Corpus Overview', 'Data Cleaner', 'Bibliometric Overview', 'Named Entity Extraction', 'Semantic Search', 'Term/Keyword Evolution', 'Ask Your Dataset', 'AI Report Builder', 'AI Method Explainer', 'Text Summarization'))
   
    new_tool_guides = {
        "Corpus Overview": ("Upload a dataset to inspect rows, columns, missing values, text fields, year coverage, and recommended next tools.", "Use this first when you are unsure which analysis page fits your file."),
        "Data Cleaner": ("Upload a dataset, choose cleaning options, preview the audit table, and download a cleaner CSV.", "Use this before bibliometrics, topic modeling, networks, or visualizations."),
        "Bibliometric Overview": ("Upload a bibliographic dataset to summarize publication trends, sources, document types, and keywords.", "Use this for a fast literature-map style overview."),
        "Named Entity Extraction": ("Choose text columns and entity types to extract people, organizations, places, dates, and related entities.", "Use this for humanities, policy, archival, and news-like corpora."),
        "Semantic Search": ("Choose searchable text columns, enter a query, and review ranked records by similarity.", "Use this when exact keyword matching is too narrow."),
        "Term/Keyword Evolution": ("Choose a year column and a keyword/text column to see how selected terms rise, fall, or stay stable over time.", "Use this after Corpus Overview or Bibliometric Overview when year metadata is present."),
        "Ask Your Dataset": ("Upload a file and ask AI questions using a dataset profile, with raw excerpts disabled unless you explicitly allow them.", "Use this for quick interpretation without committing to a specific statistical method."),
        "AI Report Builder": ("Paste findings, methods, and caveats, then generate and download a Markdown report.", "Use this at the end of a project to turn outputs into a readable narrative."),
        "AI Method Explainer": ("Choose a method and ask AI to explain interpretation, limitations, and reporting language.", "Use this when teaching, writing methods sections, or checking your understanding."),
        "Text Summarization": ("Upload or sample text, choose columns, and create extractive summaries, key points, top terms, and optional AI-assisted takeaways.", "Use this when you need a quick digest of abstracts, articles, notes, survey responses, or other text fields."),
    }

    if option in new_tool_guides:
        tab1, tab2, tab3 = st.tabs(["What it does", "Steps", "Privacy"])
        with tab1:
            st.write(new_tool_guides[option][0])
        with tab2:
            st.write(new_tool_guides[option][1])
            st.write("Open the tool from the Menu tab, upload your file if required, adjust settings, and review the generated tables or charts.")
        with tab3:
            st.write("AI features default to aggregate summaries. Tools only include raw text excerpts when the page clearly offers that option and you enable it.")

    elif option == 'Keyword Stem':
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
            
    elif option == 'Topic Modeling':
        tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download"])
        with tab1:
            st.write("Topic modeling has numerous advantages for librarians in different aspects of their work. A crucial benefit is an ability to quickly organize and categorize a huge volume of textual content found in websites, institutional archives, databases, emails, and reference desk questions. Librarians can use topic modeling approaches to automatically identify the primary themes or topics within these documents, making navigating and retrieving relevant information easier. Librarians can identify and understand the prevailing topics of discussion by analyzing text data with topic modeling tools, allowing them to assess user feedback, tailor their services to meet specific needs and make informed decisions about collection development and resource allocation. Making ontologies, automatic subject classification, recommendation services, bibliometrics, altmetrics, and better resource searching and retrieval are a few examples of topic modeling. To do topic modeling on other text like chats and surveys, change the column name to 'Abstract' in your file.")
            st.divider()
            st.write('💡 The idea came from this:')
            st.write('Lamba, M., & Madhusudhan, M. (2021, July 31). Topic Modeling. Text Mining for Information Professionals, 105–137. https://doi.org/10.1007/978-3-030-85085-2_4')
        with tab2:
            st.text("1. Put your file. Choose your preferred column.")
            st.text("2. Choose your preferred method. LDA is the most widely used, whereas Biterm is appropriate for short text, and BERTopic works well for large text data as well as supports more than 50+ languages.")
            st.text("3. Finally, you can visualize your data.")
            st.error("This app includes lemmatization and stopwords for the abstract text. Currently, we only offer English words.", icon="💬")
            
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
            st.subheader(':blue[pyLDA]', anchor=False)
            st.button('Download image.', on_click=None)
            st.text("Click Download Image button.")
            
            st.divider()
            st.subheader(':blue[Biterm]', anchor=False)
            st.text("Click the three dots at the top right then select the desired format.")
            st.markdown("![Downloading visualization](https://raw.githubusercontent.com/faizhalas/library-tools/main/images/download_biterm.jpg)")
            
            st.divider()
            st.subheader(':blue[BERTopic]', anchor=False)
            st.text("Click the camera icon on the top right menu")
            st.markdown("![Downloading visualization](https://raw.githubusercontent.com/faizhalas/library-tools/main/images/download_bertopic.jpg)")
            st.divider()
            st.subheader(':blue[CSV Result]', anchor=False)
            st.text("Click Download button")
            st.button('Download Results.',on_click=None)
                             
    elif option == 'Bidirected Network':
        tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download"])
        with tab1:
            st.write("The use of network text analysis by librarians can be quite beneficial. Finding hidden correlations and connections in textual material is a significant advantage. Using network text analysis tools, librarians can improve knowledge discovery, obtain deeper insights, and support scholars meaningfully, ultimately enhancing the library's services and resources. This menu provides a two-way relationship instead of the general network of relationships to enhance the co-word analysis. Since it is based on ARM, you may obtain transactional data information using this menu. Please name the column in your file 'Keyword' instead.")
            st.divider()
            st.write('💡 The idea came from this:') 
            st.write('Santosa, F. A. (2023). Adding Perspective to the Bibliometric Mapping Using Bidirected Graph. Open Information Science, 7(1), 20220152. https://doi.org/10.1515/opis-2022-0152')

        with tab2:
            st.text("1. Put your file.")
            st.text("2. Choose your preferable method. Picture below may help you to choose wisely.")
            st.markdown("![Source: https://studymachinelearning.com/stemming-and-lemmatization/](https://studymachinelearning.com/wp-content/uploads/2019/09/stemmin_lemm_ex-1.png)")
            st.text('Source: https://studymachinelearning.com/stemming-and-lemmatization/')
            st.text("3. Choose the value of Support and Confidence. If you're not sure how to use it please read the article above or just try it!")
            st.text("4. You can see the table and a simple visualization before making a network visualization.")
            st.text('5. Click "Generate network visualization" to see the network')
            st.error("The more data on your table, the more you'll see on network.", icon="🚨")
            st.error("If the table contains many rows, the network will take more time to process. Please use it efficiently.", icon="⌛")
            
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
            |                |                        | and separate the words with ';' |
            +----------------+------------------------+---------------------------------+
            | Hathitrust     | .json                  | htid (Hathitrust ID)            |
            +----------------+------------------------+---------------------------------+
            """, language=None)    

        with tab4:
            st.subheader(":blue[Download visualization]", anchor=False)
            st.text("Zoom in, zoom out, or shift the nodes as desired, then right-click and select Save image as ...")
            st.markdown("![Downloading graph](https://raw.githubusercontent.com/faizhalas/library-tools/main/images/download_bidirected.jpg)")     
            st.subheader(":blue[Download table as CSV]", anchor=False)
            st.text("Hover cursor over table, and click download arrow")
            st.markdown("![Downloading table](https://raw.githubusercontent.com/faizhalas/library-tools/refs/heads/main/images/tablenetwork.png)")     
            
    elif option == 'Sunburst':
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
            |     Source     |       File Type        |                Column                |
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

    elif option == 'Burst Detection':
        tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download Visualization"])
        with tab1:
            st.write("Burst detection identifies periods when a specific event occurs with unusually high frequency, referred to as 'bursty'. This method can be applied to identify bursts in a continuous stream of events or in discrete groups of events (such as poster title submissions to an annual conference).") 
            st.divider()
            st.write('💡 The idea came from this:') 
            st.write('Kleinberg, J. (2002). Bursty and hierarchical structure in streams. Knowledge Discovery and Data Mining. https://doi.org/10.1145/775047.775061')
                        
        with tab2:
            st.text("1. Put your file. Choose your preferred column to analyze.")
            st.text("2. Choose your preferred method to compare.")
            st.text("3. Finally, you can visualize your data.")
            st.error("This app includes lemmatization and stopwords. Currently, we only offer English words.", icon="💬")
    
        with tab3:
            st.code("""
            +----------------+------------------------+----------------------------------+
            |     Source     |       File Type        |              Column              |
            +----------------+------------------------+----------------------------------+
            | Scopus         | Comma-separated values | Choose your preferred column     |
            |                | (.csv)                 | that you have to analyze and     |
            +----------------+------------------------| and need a column called "Year"  |
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
            st.subheader(':blue[Burst Detection]', anchor=False)
            st.button('📊 Download high resolution image.')
            st.text("Click download button.") 
    
            st.divider()
            st.subheader(':blue[Top words]', anchor=False)
            st.button('👉 Click to download list of top words.')
            st.text("Click download button.")  
    
            st.divider()
            st.subheader(':blue[Burst]', anchor=False)
            st.button('👉 Click to download the list of detected bursts.')
            st.text("Click download button.") 

    elif option == 'Scattertext':
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


    elif option == 'Sentiment Analysis':
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
            | Dimension      | Comma-separated values |                                  |
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

    elif option == 'Shifterator':
        tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download Visualization"])
        with tab1:
            st.write("Shifterator is a tool that helps compare two pieces of text by showing which words make them different, and in what way. It uses clear bar chart visuals, called word shift graphs, to explain these differences. You can use it to compare texts directly, analyze sentiment, or even as a more reliable alternative to word clouds.")
            st.divider()
            st.write('💡 The idea came from this:')
            st.write('Gallagher, R.J., Frank, M.R., Mitchell, L. et al. (2021). Generalized Word Shift Graphs: A Method for Visualizing and Explaining Pairwise Comparisons Between Texts. EPJ Data Science, 10(4). https://doi.org/10.1140/epjds/s13688-021-00260-3')
            
        with tab2:
            st.text("1. Put your file. Choose your preferred column to analyze.")
            st.text("2. Choose your preferred method to count the words and decide how many top words you want to include or remove.")
            st.text("3. Finally, you can visualize your data.")
            st.error("This app includes lemmatization and stopwords. Currently, we only offer English words.", icon="💬")
            
        with tab3:
            st.code("""
            +----------------+------------------------+----------------------------------+
            |     Source     |       File Type        |              Column              |
            +----------------+------------------------+----------------------------------+
            | Scopus         | Comma-separated values | Choose your preferred column     |
            |                | (.csv)                 | that you have to analyze.        |
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
            st.subheader(':blue[Shifterator]', anchor=False)
            st.button('📥 Download Graph.', on_click="ignore")
            st.text("Click Download Graph button.")  
    
            st.divider()
            st.subheader(':blue[Shifterator Dataframe]', anchor=False)
            st.button('📥 Press to download result.', on_click="ignore")
            st.text("Click the Download button to get the CSV result.")


    elif option == 'WordCloud':
        tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download Visualization"])
        with tab1:
            st.write("A word cloud is a simple yet powerful way to see which words appear most often in a collection of text. Words that occur more frequently are shown larger, giving you an at-a-glance view of the key themes and topics. While it doesn’t provide deep analysis, a word cloud is a quick and intuitive tool to spot trends & highlight important terms")
            st.divider()
            st.write('💡 The idea came from this:')
            st.write('Mueller, A. (2012). A Wordcloud in Python. Peekaboo. Available at: https://peekaboo-vision.blogspot.com/2012/11/a-wordcloud-in-python.html.')
            
        with tab2:
            st.text("1. Put your file. Choose your preferred column to analyze (if CSV).")
            st.text("2. Choose your preferred method to count the words and decide how many top words you want to include or remove.")
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
            st.subheader(':blue[Visualization Download]', anchor=False)
            st.write("Right-click image and click \"Save-as\"")

    elif option == 'Histogram':
        tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download Visualization"])
        with tab1:
            st.write("The histogram uses Coconut's fast frequency engine to count words, keyword terms, years, citations, sources, or other category values from your chosen column.")

        with tab2:
            st.text("1. Put your CSV file.")
            st.text("2. Choose a specific column you'd like to focus on.")
            st.text("3. Choose whether to count words, exact values, or delimited keyword terms.")
            st.text("4. Use the histogram to compare the most frequent values.")

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
            st.subheader(':blue[Histogram Download]', anchor=False)
            st.write("Right-click image and click \"Save-as\"")

    elif option == 'Pie Chart':
        tab1, tab2, tab3, tab4 = st.tabs(["Prologue", "Steps", "Requirements", "Download Visualization"])
        with tab1:
            st.write("The pie chart uses Coconut's fast frequency engine to show how frequent words, keyword terms, years, citations, sources, or other category values divide into shares.")

        with tab2:
            st.text("1. Put your CSV file.")
            st.text("2. Choose a specific column you'd like to focus on.")
            st.text("3. Choose whether to count words, exact values, or delimited keyword terms.")
            st.text("4. Use the pie chart to compare each value's share of the total.")

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
            st.subheader(':blue[Pie Chart Download]', anchor=False)
            st.write("Right-click image and click \"Save-as\"")
