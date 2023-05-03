import pandas as pd
import streamlit as st
from io import StringIO
import base64
from st_aggrid import AgGrid, GridOptionsBuilder
import os
import gitpush
from google.cloud import firestore

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
      st.text('The file should contain at least the following columns to function properly: Key (unique identifier), Publication Year, Author, Title.')
      st.text('The code is tested and optimized for Zotero collection exports.')
      uploaded_file = st.file_uploader("Choose a file")
      if uploaded_file is not None:
        papers_df = pd.read_csv(uploaded_file)
        st.write(papers_df)
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
        df_as_dict = papers_df.to_dict('index')
        with st.spinner('Wait for it...'):
          for key, item in df_as_dict.items():
            doc_ref = db.collection(firestore_collection).document(item['Key'])
            doc_ref.set(item)
        st.success('Done!')
        ###
        user = st.secrets['github_user']
        token = st.secrets['github_token']
        repo = st.secrets['github_repo']
        gitpush.git_save('initial_config.py', user, token, repo)

else:
  import initial_config
  st.set_page_config(page_title = 'RevMaster', page_icon = ':books:', layout = 'wide')
  st.header(initial_config.project_title)
  st.text(initial_config.project_description)
  ###
  import base64
  from st_aggrid import AgGrid, GridOptionsBuilder
  ###
  # load country options
  try:
    f = open("configs/country_options.txt", "r")
    country_options = f.readlines()
  except:
     st.error("Oops! There is something wrong with your country options file.\nThe file must be called \'country_options.txt\' and contain one country per row.")
  # load include options
  try:
    f = open("configs/include_options.txt", "r")
    include_options = f.readlines()
  except:
     st.error("Oops! There is something wrong with your include options file.\nThe file must be called \'include_options.txt\' and contain one option per row.")
  
  ###
  papers = list(db.collection(initial_config.firestore_collection).stream())
  papers_dict = list(map(lambda x: x.to_dict(), papers))
  papers_df = pd.DataFrame(papers_dict)
  papers_df = papers_df[['Key', 'Author', 'Publication Year', 'Title', 'Abstract Note', 'DOI', 'Url', 'Manual Tags']]
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
  tab1, tab2, tab3, tab4 = st.tabs(["Assessment", 'Papers per year', 'Authors', 'Lemmas'])
  ## tab 1 (assessment)
  with tab1:
    # Main area (paper table)
    ####################################
    # see: https://discuss.streamlit.io/t/ag-grid-component-with-input-support/8108/242
    paper = display_table(papers_df)
    try: 
      paper_key = (paper['selected_rows'][0]['Key'])
      idx = papers_df[papers_df['Key']== paper_key].index.item()
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
    with st.container():
      col1, col2 = st.columns([3, 1])
      with col1:
        st.subheader("Paper")
        show_pdf(pdf_file)
      with col2:
        with st.form("assessment_form"):
          doc_ref = db.collection(initial_config.firestore_collection).document(paper_key)
          doc = doc_ref.get()
          st.subheader("Assessment")
          ## Include?
          try:
            option = include_options.index(doc.include)
            include_widget = st.radio('Include?', include_options, index = option)
          except:
            include_widget = st.radio('Include?', include_options)
          ## Country
          try:
            study_country = st.multiselect('Country', country_options)
          except:
            study_country = st.multiselect('Country', country_options)
          # Year
          try:
            study_year_value = int(papers_df[papers_df['Key'] == paper_key]['Year'].values[0])
          except: 
            study_year_value = 0
            study_year = st.number_input('Year', format = '%d', step = 1, value = study_year_value)
          # Study type
          
          # Methodology
          
          # Assessment criteria
          
          for criterion in initial_config.criteria:
            try:
              criterion_text = include_options.index(doc.criterion)
              criterion_widget = st.text_area(criterion, criterion_text)
            except:
              criterion_text = ''
              criterion_widget = st.text_area(criterion, criterion_text)
          save_assessment = st.form_submit_button("Save")
        if save_assessment:
          doc.update({include: include_widget})
          st.success('Saved!')
  ## tab 2 (papers per year)
  with tab2:
    data = papers_df['Publication Year'].value_counts().rename_axis('Year').to_frame('counts')
    data = data.sort_values('Year')
    st.line_chart(data)
    st.write(data)
  ## tab 3 (authors)
  with tab3:
    authorlist = []
    for x in papers_df['Author'].values.tolist():
      authorlist.append(x)
      st.text(authorlist)
