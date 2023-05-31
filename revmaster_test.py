import pandas as pd
import streamlit as st
from io import StringIO, BytesIO
import base64
from st_aggrid import AgGrid, GridOptionsBuilder
import os
import gitpush
from time import sleep
from google.cloud import firestore # see: https://blog.streamlit.io/streamlit-firestore/

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
  
  with st.form("form_1"):
    project_title = st.text_input('Project title', '...')
    project_description = st.text_area('Project description', '...')
    st.divider()
    inclusion_criteria = st.text_area('Inclusion criteria', 'Note them down here to have them in the assessment interface.')
    criteria = st.text_area('Assessment criteria', 'one\nper\nline')
    st.divider()
    firestore_collection = st.text_input('Firestore collection', '')
    ###
    st.divider()
    st.subheader('Here we create a user with read and write rights on your data.')
    new_user = st.text_input('Username')
    new_password = st.text_input('Password')
    st.info('Note down your password as for the time being I did not develop a password recovery tool!')
    st.divider()
    ###
    st.subheader('Upload the CSV file containing your papers to be assessed.')
    st.write('The file should contain at least the following columns to function properly: Key (unique identifier), Publication Year, Author, Title.')
    st.write('The code is tested and optimized for Zotero collection exports.')
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
      papers_df = pd.read_csv(uploaded_file)
      st.write(papers_df)
    ###

    ###
    save_1 = st.form_submit_button("Save")
    if save_1:
      with open('initial_config.py', 'w') as f:
        l1 = 'project_title = \'' + project_title + '\'\n'
        l2 = 'project_description = \'' + project_description + '\'\n'
        l3 = 'inclusion_criteria = \'' + inclusion_criteria + '\'\n'
        criteria = criteria.split('\n')
        critlist = 'criteria = ['
        last_item = criteria[-1]
        for criterion in criteria:
          if criterion != last_item:
            critlist = critlist + '\'' + criterion + '\', '
          if criterion == last_item:
            critlist = critlist + '\'' + criterion + '\']\n'
        l4 = critlist
        l5 = 'firestore_collection = \'' + firestore_collection + '\'\n'
        l6 = 'firestore_collection_users = \'' + firestore_collection + '_users\'\n'
        f.writelines([l1, l2, l3, l4, l5, l6])
      ###
      df_as_dict = papers_df.to_dict('index')
      with st.spinner('Wait for it...'):
        fscu = firestore_collection + '_users'
        user_ref = db.collection(fscu).document(new_user)
        user_data = {'password': new_password, 'permissions': 'rw'}
        user_ref.set(user_data)
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
  ################### with everything configured###################

  #####main#####
  import initial_config
  ###
  st.set_page_config(page_title = 'RevMaster', page_icon = ':books:', layout = 'wide')
  st.header(initial_config.project_title)
  st.write(initial_config.project_description)
  #####authentication#####
  if 'auth_status' not in st.session_state:
    auth_status = 'ro'
    auth_widgets = True
  else:
    auth_status = st.session_state.auth_status
    if auth_status in ['ro', 'rw']:
      if auth_status == 'rw':
        auth_widgets = False
      if auth_status == 'ro':
        auth_widgets = True
  ###
  #####analysis enabled#####
  if 'enable_analysis' not in st.session_state:
    enable_analysis = 'no'
    enable_analysis_widgets = False
    st.info('Analysis not enabled')
  else:
    enable_analysis = st.session_state.enable_analysis
    if enable_analysis == 'no':
      enable_analysis_widgets = False
      st.error('⛔ Analysis not enabled')
    if enable_analysis == 'yes':
      enable_analysis_widgets = True
      st.success('👌 Analysis enabled')
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
    data_df = data_df[['Key', 'Author', 'Publication Year', 'Title', 'Abstract Note', 'Item Type', 'DOI', 'Url', 'Manual Tags']]
    return data_df
  papers_df = load_data(initial_config.firestore_collection)
  
  @st.cache_data
  def load_assessment_data(firestore_collection):
    data = list(db.collection(firestore_collection).stream())
    data_dict = list(map(lambda x: x.to_dict(), data))
    data_df = pd.DataFrame(data_dict)
    return data_df

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
  if enable_analysis_widgets == False:
    # Tabs
    tab1, tab2 = st.tabs(['Assessment', 'Analysis'])
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
        pdf_file = 'dang!'
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
            pdf_file = 'dang!'
          if len(probable_files_title) == 1:
            pdf_file = 'pdfs/' + probable_files_title[0]
          if len(probable_files_title) > 1:
            pdf_file = 'doubledang!'
        st.text(probable_files_title)
      #####################################

      # Display PDF and assessment fields
      ####################################
      st.divider()
      with st.container():
        col1, col2 = st.columns([3, 2])
        with col1:
          if pdf_file not in ['dang!', 'doubledang!']:
            show_pdf(pdf_file)
          else:
            if pdf_file == 'dang!':
              st.error('Dang! Could not find that pdf file. Apologies about that.')
            if pdf_file == 'doubledang!':
              st.error('Double dang! Found more than one file matching that author/title combination. Apologies about that.')
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
            with st.expander('See inclusion criteria'):
              st.write(initial_config.inclusion_criteria)
            include_widget = st.radio('Include?', include_options, index = option_include_index, horizontal = True, disabled = auth_widgets)
          except:
            st.warning('Paper not assessed yet', icon = '⚠️')
            include_widget = st.radio('Include?', include_options, index = 0, horizontal = True, disabled = auth_widgets)
            with st.expander('See inclusion criteria'):
              st.write(initial_config.inclusion_criteria)
          col1_sidebar, col2_sidebar = st.columns(2)
          with col1_sidebar:
            ## Country
            try:
              options_country = doc_asdict['revmaster_country']
              country_widget = st.multiselect('Country', options = country_options, default = options_country, disabled = auth_widgets)
            except:
              country_widget = st.multiselect('Country', options = country_options, default = None, disabled = auth_widgets)
          with col2_sidebar:
          # Year
            try:
              study_year_value = doc_asdict['revmaster_year']            
            except: 
              try:
                study_year_value = int(papers_df[papers_df['Key'] == paper_key]['Publication Year'].values[0])
              except:
                study_year_value = 0
            study_year_widget = st.number_input('Year', format = '%d', step = 1, value = study_year_value, disabled = auth_widgets)
          # Health emergency
          try: 
            health_emergency = doc_asdict['revmaster_health_emergency']
            health_emergency_widget = st.text_input('Health emergency/issue', value = health_emergency, disabled = auth_widgets)
          except:
            health_emergency = ''
            health_emergency_widget = st.text_input('Health emergency/issue', value = health_emergency, disabled = auth_widgets)


          # Study type
          try: 
            option_study_type = doc_asdict['revmaster_study_type']
            option_study_type_index = study_type_options.index(option_study_type)
            study_type_widget = st.radio('Study type', options = study_type_options, index = option_study_type_index, disabled = auth_widgets)
          except:
            option_study_type = study_type_options[0]
            study_type_widget = st.radio('Study type', options = study_type_options, index = 0, disabled = auth_widgets)

          # Methodology
          if study_type_widget == 'Empirical':
            with st.expander('See explanation of options'):
              st.write(methodology_options_empirical_explanation)
            try:
              options_methodology = doc_asdict['revmaster_methodology']
              methodology_widget = st.multiselect('Methodology', options = methodology_options_empirical, default = options_methodology, disabled = auth_widgets)
            except: 
              methodology_widget = st.multiselect('Methodology', options = methodology_options_empirical, default = None, disabled = auth_widgets)
          if study_type_widget == 'Literature review':
            with st.expander('See explanation of options'):
                st.write(methodology_options_litrev_explanation)
            try:
              options_methodology = doc_asdict['revmaster_methodology']
              methodology_widget = st.multiselect('Methodology', options = methodology_options_litrev, default = options_methodology, disabled = auth_widgets)
            except:
              methodology_widget = st.multiselect('Methodology', options = methodology_options_litrev, default = None, disabled = auth_widgets)
          if study_type_widget in ['Theoretical', 'Viewpoint/commentary', 'Other']:
            try:
              options_methodology = doc_asdict['revmaster_methodology']
              methodology_widget = st.text_input('Methodological notes', value = options_methodology, disabled = auth_widgets)
            except:
              methodology_widget = st.text_input('Methodological notes', value = '')

          # Assessment criteria

          for criterion in initial_config.criteria:
            criterion_key = 'revmaster_' + criterion.replace(' ', '_').replace(':', '_')
            try:
              criterion_text = doc_asdict[criterion_key]
              criterion_widget_name = criterion + '_widget'
              st.text_area(criterion, criterion_text, key = criterion_widget_name, disabled = auth_widgets)
            except:
              criterion_text = ''
              criterion_widget_name = criterion + '_widget'
              st.text_area(criterion, criterion_text, key = criterion_widget_name, disabled = auth_widgets)
          save_assessment = st.button("Save", disabled = auth_widgets)

          if save_assessment:
            savedict = {'revmaster_include': include_widget, 
                      'revmaster_country': country_widget, 
                      'revmaster_study_year' : study_year_widget,
                      'revmaster_study_type' : study_type_widget, 
                      'revmaster_methodology' : methodology_widget,
                      'revmaster_health_emergency' : health_emergency_widget}
            for criterion in initial_config.criteria:
              criterion_widget_name = criterion + '_widget'
              criterion_dict_index = 'revmaster_' + criterion.replace(' ', '_').replace(':', '_')
              if st.session_state[criterion_widget_name] == '':
                savedict[criterion_dict_index] = '...'
              else:
                savedict[criterion_dict_index] = st.session_state[criterion_widget_name]
            doc_ref.update(savedict)
            st.success('Saved!')
    ## tab 2 (Analysis)###############################################        
    with tab2:
      st.write('Enable the analysis features to see the advanced analysis (authors, keywords, publications per year, NLP on assessments, ...). \n\nAnalysis is disabled by default to save memory and allow a faster use of the interface during the assessment. It can be enabled using the checkbox in the sidebar.')
      papers_assessed_df = load_assessment_data(initial_config.firestore_collection)
      st.subheader('Documents assessed')
      st.write(str(len(papers_assessed_df[papers_assessed_df['revmaster_include'] == 'Yes'])) + ' / ' + str(len(papers_assessed_df)) + ' included.')
      st.write(str(len(papers_assessed_df[papers_assessed_df['revmaster_include'] == 'No'])) + ' / ' + str(len(papers_assessed_df)) + ' excluded.')
      st.write(str(len(papers_assessed_df[papers_assessed_df['revmaster_include'] == 'Maybe'])) + ' / ' + str(len(papers_assessed_df)) + ' assessed as \'maybe\', -> to be double-checked.')
      
      st.write(str(len(papers_assessed_df.loc[(papers_assessed_df['revmaster_include'] != 'Yes') & (papers_assessed_df['revmaster_include'] != 'No') & (papers_assessed_df['revmaster_include'] != 'maybe')])) + ' / ' + str(len(papers_assessed_df)) + ' NOT assessed yet -> to be assessed.')
      st.subheader('Documents to double-check')
      data = papers_assessed_df[papers_assessed_df['revmaster_include'] == 'Maybe']
      data = data[['Key', 'Author', 'Publication Year', 'Title']]
      st.write(data)
      st.subheader('Documents to assess')
      data = papers_assessed_df.loc[(papers_assessed_df['revmaster_include'] != 'Yes') & (papers_assessed_df['revmaster_include'] != 'No') & (papers_assessed_df['revmaster_include'] != 'maybe')]
      data = data[['Key', 'Author', 'Publication Year', 'Title']]
      st.write(data)
############
  if enable_analysis_widgets == True:
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Assessment", 'Papers per year', 'Authors', 'Manual tags (= keywords)', 'Analysis (assessments)', 'Analysis (document details)'])
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
        pdf_file = 'dang!'
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
            pdf_file = 'dang!'
          if len(probable_files_title) == 1:
            pdf_file = 'pdfs/' + probable_files_title[0]
          if len(probable_files_title) > 1:
            pdf_file = 'doubledang!'
        st.text(probable_files_title)
      #####################################

      # Display PDF and assessment fields
      ####################################
      st.divider()
      with st.container():
        col1, col2 = st.columns([3, 2])
        with col1:
          if pdf_file not in ['dang!', 'doubledang!']:
            show_pdf(pdf_file)
          else:
            if pdf_file == 'dang!':
              st.error('Dang! Could not find that pdf file. Apologies about that.')
            if pdf_file == 'doubledang!':
              st.error('Double dang! Found more than one file matching that author/title combination. Apologies about that.')
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
            with st.expander('See inclusion criteria'):
              st.write(initial_config.inclusion_criteria)
            include_widget = st.radio('Include?', include_options, index = option_include_index, horizontal = True, disabled = auth_widgets)
          except:
            st.warning('Paper not assessed yet', icon = '⚠️')
            include_widget = st.radio('Include?', include_options, index = 0, horizontal = True, disabled = auth_widgets)
            with st.expander('See inclusion criteria'):
              st.write(initial_config.inclusion_criteria)
          col1_sidebar, col2_sidebar = st.columns(2)
          with col1_sidebar:
            ## Country
            try:
              options_country = doc_asdict['revmaster_country']
              country_widget = st.multiselect('Country', options = country_options, default = options_country, disabled = auth_widgets)
            except:
              country_widget = st.multiselect('Country', options = country_options, default = None, disabled = auth_widgets)
          with col2_sidebar:
          # Year
            try:
              study_year_value = doc_asdict['revmaster_year']            
            except: 
              try:
                study_year_value = int(papers_df[papers_df['Key'] == paper_key]['Publication Year'].values[0])
              except:
                study_year_value = 0
            study_year_widget = st.number_input('Year', format = '%d', step = 1, value = study_year_value, disabled = auth_widgets)
          # Health emergency
          try: 
            health_emergency = doc_asdict['revmaster_health_emergency']
            health_emergency_widget = st.text_input('Health emergency/issue', value = health_emergency, disabled = auth_widgets)
          except:
            health_emergency = ''
            health_emergency_widget = st.text_input('Health emergency/issue', value = health_emergency, disabled = auth_widgets)


          # Study type
          try: 
            option_study_type = doc_asdict['revmaster_study_type']
            option_study_type_index = study_type_options.index(option_study_type)
            study_type_widget = st.radio('Study type', options = study_type_options, index = option_study_type_index, disabled = auth_widgets)
          except:
            option_study_type = study_type_options[0]
            study_type_widget = st.radio('Study type', options = study_type_options, index = 0, disabled = auth_widgets)

          # Methodology
          if study_type_widget == 'Empirical':
            with st.expander('See explanation of options'):
              st.write(methodology_options_empirical_explanation)
            try:
              options_methodology = doc_asdict['revmaster_methodology']
              methodology_widget = st.multiselect('Methodology', options = methodology_options_empirical, default = options_methodology, disabled = auth_widgets)
            except: 
              methodology_widget = st.multiselect('Methodology', options = methodology_options_empirical, default = None, disabled = auth_widgets)
          if study_type_widget == 'Literature review':
            with st.expander('See explanation of options'):
                st.write(methodology_options_litrev_explanation)
            try:
              options_methodology = doc_asdict['revmaster_methodology']
              methodology_widget = st.multiselect('Methodology', options = methodology_options_litrev, default = options_methodology, disabled = auth_widgets)
            except:
              methodology_widget = st.multiselect('Methodology', options = methodology_options_litrev, default = None, disabled = auth_widgets)
          if study_type_widget in ['Theoretical', 'Viewpoint/commentary', 'Other']:
            try:
              options_methodology = doc_asdict['revmaster_methodology']
              methodology_widget = st.text_input('Methodological notes', value = options_methodology, disabled = auth_widgets)
            except:
              methodology_widget = st.text_input('Methodological notes', value = '')

          # Assessment criteria

          for criterion in initial_config.criteria:
            criterion_key = 'revmaster_' + criterion.replace(' ', '_').replace(':', '_')
            try:
              criterion_text = doc_asdict[criterion_key]
              criterion_widget_name = criterion + '_widget'
              st.text_area(criterion, criterion_text, key = criterion_widget_name, disabled = auth_widgets)
            except:
              criterion_text = ''
              criterion_widget_name = criterion + '_widget'
              st.text_area(criterion, criterion_text, key = criterion_widget_name, disabled = auth_widgets)
          save_assessment = st.button("Save", disabled = auth_widgets)

          if save_assessment:
            savedict = {'revmaster_include': include_widget, 
                      'revmaster_country': country_widget, 
                      'revmaster_study_year' : study_year_widget,
                      'revmaster_study_type' : study_type_widget, 
                      'revmaster_methodology' : methodology_widget,
                      'revmaster_health_emergency' : health_emergency_widget}
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
        try:
          authors = author_block.split(';')
          for author in authors:
            authorlist.append(author.strip())
        except:
          authorlist.append(author_block)
      data = Counter(authorlist)
      data_df = pd.DataFrame.from_dict(data, orient='index').reset_index()
      data_df.columns = ['Author', 'count']
      data_df = data_df.sort_values(by=['count'], ascending = False)
      wordcloud = WordCloud(background_color="white", width=1600, height=800).generate_from_frequencies(data)
      fig, ax = plt.subplots(figsize = (12, 6))
      ax.imshow(wordcloud, interpolation="bilinear")
      plt.axis("off")
      st.pyplot(fig)
      plt.close(fig)
      st.bar_chart(data_df, x = 'Author', y = 'count')
      st.write(data_df)
    ## tab 4 (manual tags)###############################################
    with tab4:
      st.write('Manual tags include keywords and MeSH terms aggregated in one single column.')
      st.write('A stoplist is hard-coded in the software, it contains the word \'article\' and it can be customized in the code.')
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
      plt.close(fig)
      st.bar_chart(data_df, x = 'Keyword', y = 'count')
      st.write(data_df)
    ## tab 5 (NLP analysis of assessments)###############################################
    with tab5:
      import spacy
      from collections import Counter
      import matplotlib.pyplot as plt
      from wordcloud import WordCloud
      @st.cache_data
      def load_nlp_model(model):
        try:
          nlp = spacy.load(model)
        except OSError:
          print('Downloading language model for the spaCy POS tagger')
          from spacy.cli import download
          download(model)
        nlp = spacy.load(model)
        return nlp
      nlp = load_nlp_model('en_core_web_sm')

      def do_lemma_freq(text):
        doc = nlp(text)
        lemmatized_string = []
        for token in doc:
          if not token.is_stop and not token.is_punct and not token.is_space and not token.is_digit:
            lemmatized_string.append(token.lemma_)
        data = Counter(lemmatized_string)
        data_df = pd.DataFrame.from_dict(data, orient='index').reset_index()
        data_df.columns = ['Keyword', 'count']
        data_df = data_df.sort_values(by=['count'], ascending = False)
        data_df.reset_index(inplace=True)
        data_df.index = data_df.index + 1
        data_df.drop('index', axis='columns', inplace=True)
        return(data_df)

      def do_lemma_wordcloud(df):
        data = {}
        for index, row in df.iterrows():
          data[row['Keyword']] = row['count']
        wordcloud = WordCloud(background_color="white", width=1600, height=800,  max_words=75).generate_from_frequencies(data)
        fig, ax = plt.subplots(figsize = (12, 6))
        ax.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(fig)
        plt.close(fig)
        return(data)


      papers_assessed_df = load_assessment_data(initial_config.firestore_collection)
      n_papers_assessed = len(papers_assessed_df)
      papers_assessed_df_included = papers_assessed_df[papers_assessed_df['revmaster_include'] == 'Yes']
      n_papers_included = len(papers_assessed_df_included)
      papers_assessed_df_excluded = papers_assessed_df[papers_assessed_df['revmaster_include'] == 'No']
      n_papers_excluded = len(papers_assessed_df_excluded)
      papers_assessed_df_maybe = papers_assessed_df[papers_assessed_df['revmaster_include'] == 'Maybe']
      n_papers_maybe = len(papers_assessed_df_maybe)
      st.write('Showing lemma frequencies of the assessments of included papers (' + str(n_papers_included) + ' / ' + str(n_papers_assessed) + ').')
      st.write('Assessed as Maybe: ' + str(n_papers_maybe))
      st.write('Assessed as Exclude: ' + str(n_papers_excluded))
      st.divider()

      revmaster_cols_nlp = initial_config.criteria
      nlp_columns_dict = {}
      for x in revmaster_cols_nlp:
        y = 'revmaster_' + x.replace(' ', '_').replace(':', '_')
        nlp_columns_dict[x] = y
      for key, item in nlp_columns_dict.items():
        st.subheader(key)
        text = papers_assessed_df_included[item].values.tolist()
        text = [x for x in text if str(x) != 'nan']
        text = [x for x in text if str(x) != '...']
        text = ' '.join(text)
        nlp_col1, nlp_col2 = st.columns([1, 3])
        with nlp_col1:
          x = do_lemma_freq(text)
          st.write(x)
        with nlp_col2:
          y = do_lemma_wordcloud(x)
    ## tab 6 (NLP analysis)###############################################
    with tab6:
      import itertools
      from collections import Counter
      papers_assessed_df = load_assessment_data(initial_config.firestore_collection)
      n_papers_assessed = len(papers_assessed_df)
      papers_assessed_df_included = papers_assessed_df[papers_assessed_df['revmaster_include'] == 'Yes']
      n_papers_included = len(papers_assessed_df_included)
      papers_assessed_df_excluded = papers_assessed_df[papers_assessed_df['revmaster_include'] == 'No']
      n_papers_excluded = len(papers_assessed_df_excluded)
      papers_assessed_df_maybe = papers_assessed_df[papers_assessed_df['revmaster_include'] == 'Maybe']
      n_papers_maybe = len(papers_assessed_df_maybe)
      st.write('Showing lemma frequencies of the assessments of included papers (' + str(n_papers_included) + ' / ' + str(n_papers_assessed) + ').')
      st.write('Assessed as Maybe: ' + str(n_papers_maybe))
      st.write('Assessed as Exclude: ' + str(n_papers_excluded))
      st.divider()
      ###Country
      st.subheader('Country')
      country_list = list(itertools.chain(*papers_assessed_df_included.revmaster_country.values.tolist()))
      country_count = Counter(country_list)
      sorted_country_count = dict(sorted(country_count.items(), key=lambda x:x[1], reverse = True))
      st.bar_chart(sorted_country_count)
      ###Year
      st.subheader('Study year')
      study_year_list = papers_assessed_df_included.revmaster_study_year.values.tolist()
      study_year_count = Counter(study_year_list)
      sorted_study_year_count = dict(sorted(study_year_count.items(), key=lambda x:x[1], reverse = True))
      st.bar_chart(sorted_study_year_count)
      ###Study type
      st.subheader('Study Type')
      study_type_list = papers_assessed_df_included.revmaster_study_type.values.tolist()
      study_type_count = Counter(study_type_list)
      sorted_study_type_count = dict(sorted(study_type_count.items(), key=lambda x:x[1], reverse = True))
      st.bar_chart(sorted_study_type_count)
      ###Methodology (of empirical studies)
      st.subheader('Methodology (of empirical studies)')
      data = papers_assessed_df_included[papers_assessed_df_included['revmaster_study_type'] == 'Empirical']
      methodology_list = list(itertools.chain(*data.revmaster_methodology.values.tolist()))
      methodology_count = Counter(methodology_list)
      sorted_methodology_count = dict(sorted(methodology_count.items(), key=lambda x:x[1], reverse = True))
      st.bar_chart(sorted_methodology_count) 
      ###Methodology (of other studies)


## sidebar#######################
  ###sidebar 
  with st.sidebar:
    ## enable analysis functions ##
    st.info('Analysis features use memory and computing power. Keep them disabled while assessing papers for a smoother experience.')
    if 'enable_analysis' not in st.session_state:
      st.session_state['enable_analysis'] = 'no'
    if 'enable_analysis' in st.session_state:
      if st.session_state['enable_analysis'] == 'no':
        analysis_widget = st.checkbox('Enable analysis', value = False)
        if analysis_widget == True:
          st.info('👌 Analysis features enabled')
          st.session_state['enable_analysis'] = 'yes'
          st.experimental_rerun()
      if st.session_state['enable_analysis'] == 'yes':
        analysis_widget = st.checkbox('Enable analysis', value = True)
        if analysis_widget == False:
          st.info('⛔ Analysis features disabled')
          st.session_state['enable_analysis'] = 'no'
          st.experimental_rerun()
    ## login##
    if 'auth_status' not in st.session_state:
      st.session_state['auth_status'] = 'ro'
    if 'auth_status' in st.session_state:
      if st.session_state['auth_status'] == 'ro':
        st.subheader('Login to edit')
        with st.form("Authentication"):
          username = st.text_input('username:')
          password = st.text_input('password:', type="password")
          submit_login = st.form_submit_button("Login")
        if submit_login:
          try:
            user_ref = db.collection(initial_config.firestore_collection_users).document(username)
            user = user_ref.get()
            user_asdict = user.to_dict()
            if user_asdict['password'] == password:
              st.success('All good, logging in...')
              st.session_state['auth_status'] = user_asdict['permissions']
            else:
              st.error('Wrong password!')
          except: 
            st.error('Unknown user!')
          sleep(4)
          st.experimental_rerun()
      if st.session_state['auth_status'] == 'rw':
        st.success('Welcome!')
        if st.button('Logout'):
          st.session_state['auth_status'] = 'ro'
          st.experimental_rerun()

            
        ## export button ##
        import xlsxwriter
        from pyxlsb import open_workbook as open_xlsb
        st.subheader('Export assessment data')
        if st.button('Export'):
          st.info('This function will export the assessment data as an excel file. Wait a sec...')
          with st.spinner('Wait for it...'):
            papers_df_export = export_data(initial_config.firestore_collection)
            papers_df_export.to_excel("RevMaster assessment.xlsx")
            with open('RevMaster assessment.xlsx', 'rb') as template_file:
              template_byte = template_file.read()

            st.download_button(label = 'Download', file_name = 'RevMaster assessment.xlsx', data = template_byte, mime='application/octet-stream')
