import pandas as pd
import streamlit as st
from io import StringIO, BytesIO
import base64
import toml
import json
from st_aggrid import AgGrid, GridOptionsBuilder
import os
import gitpush
from google.cloud import firestore

git_user = st.secrets['github_user']
git_token = st.secrets['github_token']
git_repo = st.secrets['github_repo']

# Initial configurations
####################################

db = firestore.Client.from_service_account_json("firestore-key.json")

config_files = os.listdir('.')

if 'initial_config.py' not in config_files:
  st.set_page_config(page_title = 'RevMaster', 
                     page_icon = ':books:', 
                     layout = 'centered', 
                     menu_items={'Get Help': 'https://www.giovannispitale.net',
                                 'Report a bug': "https://www.giovannispitale.net",
                                 'About': "# RevMaster v0.1. This is an *extremely* cool app for conducting literature reviews."})
  st.header('RevMaster setup')
  st.subheader('No configuration found.')
  st.subheader('Let\'s set up a new project')
  with st.expander('Title and description', expanded = True):
    with st.form("form_1"):
      project_title = st.text_input('Project title', '...')
      project_description = st.text_area('Project description', '...')
      st.divider()
      criteria = st.text_area('Assessment criteria', 'one\nper\nline')
      st.divider()
      firestore_collection = st.text_input('Firestore collection', '')
      ###
      st.subheader('Upload the CSV file containing your papers to be assessed.')
      st.write('The file should contain at least the following columns to function properly: Key (unique identifier), Publication Year, Author, Title.')
      st.write('The code is tested and optimized for Zotero collection exports.')
      uploaded_file = st.file_uploader("Choose a file", type = ['csv'], key = 'upload_csv_widget')
      if uploaded_file is not None:
        papers_df = pd.read_csv(uploaded_file)
        st.write(papers_df)
      ###
      st.subheader('Upload your firestore key file')
      st.write('The key file can be generated from your firestore account, see [here for details](https://blog.streamlit.io/streamlit-firestore/).')
      uploaded_key = st.file_uploader("Choose a file", type = ['json'], key = 'upload_key_widget')
      if uploaded_key is not None:
        json_text = str(uploaded_key.read())
        config = {"textkey": json_text}
        toml_config = toml.dumps(config)
        st.subheader('Copy this in your streamlit secrets:')
        st.text(type(config))
        st.text(config)
        #gitpush.git_save(output_file, git_user, git_token, git_repo)
        #key_dict = json.loads(config)
        #st.write(key_dict)
        #creds = st.secrets["textkey"]
        #st.write(key_dict)
        #db = firestore.Client(credentials=creds, project="revmaster_test")

      ###      
      save_1 = st.form_submit_button("Save")
      if save_1:
        with open('initial_config.py', 'w') as f:
          l1 = 'project_title = \'' + project_title + '\'\n'
          l2 = 'project_description = \'' + project_description + '\'\n'
          criteria = criteria.split('\n')
          critlist = 'criteria = ['
          last_item = criteria[-1]
          for criterion in criteria:
            if criterion != last_item:
              critlist = critlist + '\'' + criterion + '\', '
            if criterion == last_item:
              critlist = critlist + '\'' + criterion + '\']\n'
          l3 = critlist
          l4 = 'firestore_collection = \'' + firestore_collection + '\'\n'
          f.writelines([l1, l2, l3, l4])
        ###
        with st.spinner('Wait for it...'):
          gitpush.git_save('initial_config.py', git_user, git_token, git_repo)
          df_as_dict = papers_df.to_dict('index')
          for key, item in df_as_dict.items():
            doc_ref = db.collection(firestore_collection).document(item['Key'])
            doc_ref.set(item)
        st.success('Done!')
        ###
        
        

else:
  ################### with everything configured###################
  import initial_config
  import base64
  from st_aggrid import AgGrid, GridOptionsBuilder
  ###
  st.set_page_config(page_title = 'RevMaster', page_icon = ':books:', layout = 'wide')
  st.header(initial_config.project_title)
  st.write(initial_config.project_description)
  ###
  # load country options
  try:
    f = open("configs/country_options.txt", "r")
    country_options = f.readlines()
    country_options = [s.strip() for s in country_options]
  except:
     st.error("Oops! There is something wrong with your country options file.\nThe file must be called \'country_options.txt\' and contain one country per row.")
  # load include options
  try:
    f = open("configs/include_options.txt", "r")
    include_options = f.readlines()
    include_options = [s.strip() for s in include_options]
  except:
     st.error("Oops! There is something wrong with your include options file.\nThe file must be called \'include_options.txt\' and contain one option per row.")
  # load study type options
  try:
    f = open("configs/study_type_options.txt", "r")
    study_type_options = f.readlines()
    study_type_options = [s.strip() for s in study_type_options]
  except:
     st.error("Oops! There is something wrong with your study type options file.\nThe file must be called \'study_type_options.txt\' and contain one option per row.")
# load methodology options (empirical)
  try:
    f = open("configs/methodology_options_empirical.txt", "r")
    methodology_options_empirical = f.readlines()
    methodology_options_empirical = [s.strip() for s in methodology_options_empirical]
  except:
     st.error("Oops! There is something wrong with your methodology options file (empirical).\nThe file must be called \'methodology_options_empirical.txt\' and contain one option per row.")      
# load explanation of options
  try:
    f = open("configs/methodology_options_empirical_explanation.txt", "r")
    methodology_options_empirical_explanation = f.read()      
  except:
     st.error("Oops! There is something wrong with your explanations file (empirical).\nThe file must be called \'methodology_options_empirical_explanation.txt\'")  
# load methodology options (literature review)
  try:
    f = open("configs/methodology_options_litrev.txt", "r")
    methodology_options_litrev = f.readlines()
    methodology_options_litrev = [s.strip() for s in methodology_options_litrev]
  except:
     st.error("Oops! There is something wrong with your methodology options file (literature review).\nThe file must be called \'methodology_options_litrev.txt\' and contain one option per row.")
# load explanation of options
  try:
    f = open("configs/methodology_options_litrev_explanation.txt", "r")
    methodology_options_litrev_explanation = f.read()
  except:
     st.error("Oops! There is something wrong with your explanations file (literature review).\nThe file must be called \'methodology_options_litrev_explanation.txt\'")    
  ###
  @st.cache_data
  def load_data(firestore_collection):
    data = list(db.collection(firestore_collection).stream())
    data_dict = list(map(lambda x: x.to_dict(), data))
    data_df = pd.DataFrame(data_dict)
    data_df = data_df[['Key', 'Author', 'Publication Year', 'Title', 'Abstract Note', 'DOI', 'Url', 'Manual Tags']]
    return data_df
  papers_df = load_data(initial_config.firestore_collection)
  
  def export_data(firestore_collection):
    data = list(db.collection(firestore_collection).stream())
    data_dict = list(map(lambda x: x.to_dict(), data))
    data_df = pd.DataFrame(data_dict)
    return data_df
  
  ####################################functions
  ## show papers
  def show_pdf(file_path):
    with open(file_path,"rb") as f:
      base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width = 100% height="1500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

  ## aggrid table
  def display_table(df):
    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection('single')
    ag = AgGrid(df,
                height = 500,
                gridOptions=gb.build())
    return ag
  ####################################
  # Tabs
  tab1, tab2, tab3, tab4 = st.tabs(["Assessment", 'Papers per year', 'Authors', 'Manual tags (= keywords)'])
  ## tab 1 (assessment)###############################################
  with tab1:
    # Main area (paper table)
    ####################################
    # see: https://discuss.streamlit.io/t/ag-grid-component-with-input-support/8108/242
    paper = display_table(papers_df)
    st.divider()
    try: 
      paper_key = (paper['selected_rows'][0]['Key'])
      idx = papers_df[papers_df['Key']== paper_key].index.item()
      doc_ref = db.collection(initial_config.firestore_collection).document(paper_key)
      doc = doc_ref.get()
      doc_asdict = doc.to_dict()
    except: 
      paper_key = papers_df.iloc[0]['Key']
      idx = papers_df[papers_df['Key']== paper_key].index.item()

    try:
      # build file name
      ## Author
      authors = papers_df[papers_df['Key'] == paper_key]['Author'].values[0]

      ## Title
      title = papers_df[papers_df['Key'] == paper_key]['Title'].values[0]
      show_title = st.subheader(title)

      ## Year
      year = papers_df[papers_df['Key'] == paper_key]['Publication Year'].values[0]
      year = int(year)

    except:
      st.text('Select a paper to start the assessment')

    names_for_file = []
    authorlist = authors.split(';')
    for x in authorlist:
      surname = x.split(',')
      names_for_file.append(surname[0].strip())
    # Finding pdfs
    ####################################
    ## here I apply a rule to determine how many author surnames are used in the filename.
    names_for_file_parsed = []
    if len(names_for_file) == 1:
      names_for_file_parsed.append(names_for_file[0])
    if len(names_for_file) == 2:
      names_for_file_parsed.append(names_for_file[0])
      names_for_file_parsed.append(', ')
      names_for_file_parsed.append(names_for_file[1])
    if len(names_for_file) > 2:
      names_for_file_parsed.append(names_for_file[0])
      names_for_file_parsed.append(', ')
      names_for_file_parsed.append(names_for_file[1])
      names_for_file_parsed.append(' et al')
    names_for_file_string = ''.join(names_for_file_parsed)
    auth_and_year = names_for_file_string + ', ' + str(year)
    st.text(auth_and_year)

    probable_files = []
    for file in os.listdir('pdfs'):
      if file.find(names_for_file_string)!= -1:
          probable_files.append(file)

    # here we specify which file to serve
    if len(probable_files) == 0:
      pdf_file = 'base_pdfs/dang.pdf'
    if len(probable_files) == 1:
      pdf_file = 'pdfs/' + probable_files[0]
    if len(probable_files) > 1:
      probable_files_title = []
      title_as_list = title.split(' ')
      first_words = title_as_list[0:2]
      first_words= ' '.join(first_words)
      for file in probable_files:
        if file.find(first_words)!= -1:
          probable_files_title.append(file)
        if len(probable_files_title) == 0:
          pdf_file = 'base_pdfs/dang.pdf'
        if len(probable_files_title) == 1:
          pdf_file = 'pdfs/' + probable_files_title[0]
        if len(probable_files_title) > 1:
          pdf_file = 'base_pdfs/doubledang.pdf'
        st.text(probable_files_title)
    #####################################

    # Display PDF and assessment fields
    ####################################
    st.divider()
    with st.container():
      col1, col2 = st.columns([3, 2])
      with col1:
        show_pdf(pdf_file)
      with col2:
        st.subheader("Assessment")
        ## Include?
        try:
          option_include = doc_asdict['revmaster_include']
          option_include_index = include_options.index(option_include)
          if option_include == 'Yes':
            st.success('Paper already assessed as: include', icon = '👌')
          if option_include == 'No':
            st.error('Paper already assessed as: exclude', icon = '⛔')
          if option_include == 'Maybe':
            st.info('Paper already assessed as: maybe', icon = '❔')
          include_widget = st.radio('Include?', include_options, index = option_include_index, horizontal = True)
        except:
          st.warning('Paper not assessed yet', icon = '⚠️')
          include_widget = st.radio('Include?', include_options, index = 0, horizontal = True)
        col1_sidebar, col2_sidebar = st.columns(2)
        with col1_sidebar:
          ## Country
          try:
            options_country = doc_asdict['revmaster_country']
            country_widget = st.multiselect('Country', options = country_options, default = options_country)
          except:
            country_widget = st.multiselect('Country', options = country_options, default = None)
        with col2_sidebar:
        # Year
          try:
            study_year_value = doc_asdict['revmaster_year']            
          except: 
            try:
              study_year_value = int(papers_df[papers_df['Key'] == paper_key]['Publication Year'].values[0])
            except:
              study_year_value = 0
          study_year_widget = st.number_input('Year', format = '%d', step = 1, value = study_year_value)
        # Study type
        try: 
          option_study_type = doc_asdict['revmaster_study_type']
          option_study_type_index = study_type_options.index(option_study_type)
          study_type_widget = st.radio('Study type', options = study_type_options, index = option_study_type_index)
        except:
          option_study_type = study_type_options[0]
          study_type_widget = st.radio('Study type', options = study_type_options, index = 0)

        # Methodology
        if study_type_widget == 'Empirical':
          with st.expander('See explanation of options'):
            st.write(methodology_options_empirical_explanation)
          try:
            options_methodology = doc_asdict['revmaster_methodology']
            methodology_widget = st.multiselect('Methodology', options = methodology_options_empirical, default = options_methodology)
          except: 
            methodology_widget = st.multiselect('Methodology', options = methodology_options_empirical, default = None)
        if study_type_widget == 'Literature review':
          with st.expander('See explanation of options'):
              st.write(methodology_options_litrev_explanation)
          try:
            options_methodology = doc_asdict['revmaster_methodology']
            methodology_widget = st.multiselect('Methodology', options = methodology_options_litrev, default = options_methodology)
          except:
            methodology_widget = st.multiselect('Methodology', options = methodology_options_litrev, default = None)
        if study_type_widget in ['Theoretical', 'Viewpoint/commentary', 'Other']:
          try:
            options_methodology = doc_asdict['revmaster_methodology']
            methodology_widget = st.text_input('Methodological notes', value = options_methodology)
          except:
            methodology_widget = st.text_input('Methodological notes', value = '')

        # Assessment criteria

        for criterion in initial_config.criteria:
          try:
            criterion_text = doc_asdict[criterion]
            criterion_widget_name = criterion + '_widget'
            st.text_area(criterion, criterion_text, key = criterion_widget_name)
          except:
            criterion_text = ''
            criterion_widget_name = criterion + '_widget'
            st.text_area(criterion, criterion_text, key = criterion_widget_name)
        save_assessment = st.button("Save")

        if save_assessment:
          savedict = {'revmaster_include': include_widget, 
                    'revmaster_country': country_widget, 
                    'revmaster_study_year' : study_year_widget,
                    'revmaster_study_type' : study_type_widget, 
                    'revmaster_methodology' : methodology_widget}
          for criterion in initial_config.criteria:
            criterion_widget_name = criterion + '_widget'
            criterion_dict_index = 'revmaster_' + criterion.replace(' ', '_').replace(':', '_')
            if st.session_state[criterion_widget_name] == '':
              savedict[criterion_dict_index] = '...'
            else:
              savedict[criterion_dict_index] = st.session_state[criterion_widget_name]
          doc_ref.update(savedict)
          st.success('Saved!')
  ## tab 2 (papers per year)###############################################
  with tab2:
    data = papers_df['Publication Year'].value_counts().rename_axis('Year').to_frame('counts')
    data = data.sort_values('Year')
    st.line_chart(data)
    st.write(data)
  ## tab 3 (authors)###############################################
  with tab3:
    from collections import Counter
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    authorlist = []
    for author_block in papers_df['Author'].values.tolist():
      authors = author_block.split(';')
      for author in authors:
        authorlist.append(author.strip())
    data = Counter(authorlist)
    data_df = pd.DataFrame.from_dict(data, orient='index').reset_index()
    data_df.columns = ['Author', 'count']
    data_df = data_df.sort_values(by=['count'], ascending = False)
    wordcloud = WordCloud(background_color="white", width=1600, height=800).generate_from_frequencies(data)
    fig, ax = plt.subplots(figsize = (12, 6))
    ax.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(fig)
    st.bar_chart(data_df, x = 'Author', y = 'count')
    st.write(data_df)
  ## tab 4 (manual tags)###############################################
  with tab4:
    st.text('Manual tags include keywords and MeSH terms aggregated in one single column.')
    st.text('A stoplist is hard-coded in the software, it contains the word \'article\' and it can be customized in the code.')
    from collections import Counter
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    kwlist = []
    for kw_block in papers_df['Manual Tags'].values.tolist():
      if isinstance(kw_block, str):
        kws = kw_block.split(';')
        for kw in kws:
          kw_processed = kw.strip().lower().replace('*', '')
          if kw_processed not in ['article', 'other stopwords']: # this is the stoplist
            kwlist.append(kw_processed)
    data = Counter(kwlist)
    data_df = pd.DataFrame.from_dict(data, orient='index').reset_index()
    data_df.columns = ['Keyword', 'count']
    data_df = data_df.sort_values(by=['count'], ascending = False)
    wordcloud = WordCloud(background_color="white", width=1600, height=800).generate_from_frequencies(data)
    fig, ax = plt.subplots(figsize = (12, 6))
    ax.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(fig)
    st.bar_chart(data_df, x = 'Keyword', y = 'count')
    st.write(data_df)
  
  ###sidebar 
  with st.sidebar:
    import xlsxwriter
    from pyxlsb import open_workbook as open_xlsb
    st.subheader('Export data')
    if st.button('Export'):
      st.info('This function will export the assessment data as an excel file. Wait a sec...')
      with st.spinner('Wait for it...'):
        papers_df_export = export_data(initial_config.firestore_collection)
        papers_df_export.to_excel("RevMaster assessment.xlsx")
        with open('RevMaster assessment.xlsx', 'rb') as template_file:
          template_byte = template_file.read()
        
        st.download_button(label = 'Download', file_name = 'RevMaster assessment.xlsx', data = template_byte, mime='application/octet-stream')
