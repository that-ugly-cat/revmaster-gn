import pandas as pd
import streamlit as st
from io import StringIO
import base64
from st_aggrid import AgGrid, GridOptionsBuilder
import os
import gitpush

# Initial configurations
####################################
st.set_page_config(page_title = 'RevMaster', page_icon = ':books:', layout = 'wide')

config_files = os.listdir('configs')

st.text(config_files)
if 'initial_config.py' not in config_files:
  st.header('No configuration found.')
  st.subheader('Let\'s set up a new project')
  with st.expander('Title and description', expanded = True):
    with st.form("form_1"):
      project_title = st.text_input('Project title', '...')
      project_description = st.text_area('Project description', '...')
      st.divider()
      criteria = st.text_area('Assessment criteria', 'one\nper\nline')
      st.divider()
      st.text('Upload the CSV file containing your papers to be assessed.\nThe file should contain the following columns: ...')
      uploaded_file = st.file_uploader("Choose a file")
      if uploaded_file is not None:
        papers_df = pd.read_csv(uploaded_file)
        st.write(len(papers_df))
        st.write(type(papers_df))
        st.write(papers_df.columns.values.tolist())
      save_1 = st.form_submit_button("Save")

      if save_1:
        with open('configs/initial_config.py', 'w') as f:
          l1 = 'project_title = \'' + project_title + '\'\n'
          l2 = 'project_description = \'' + project_description + '\'\n'
          criteria = criteria.split('\n')
          critlist = 'criteria = ['
          last_item = criteria[-1]
          for criterion in criteria:
            if criterion != last_item:
              critlist = critlist + '\'' + criterion + '\', '
            if criterion == last_item:
              critlist = critlist + '\'' + criterion + '\']'
          l3 = critlist
          f.writelines([l1, l2, l3])
        test_read = open('configs/initial_config.py', 'r')
        lines = test_read.readlines()
        for line in lines:
          st.write(line)
      user = st.secrets['github_user']
      token = st.secrets['github_token']
      repo = st.secrets['github_repo']
      gitpush.git_save('configs/initial_config.py', user, token, repo)

else:
  st.text('...')
  test_read = open('configs/initial_config.py', 'r')
  lines = test_read.readlines()
  for line in lines:
    st.write(line)

