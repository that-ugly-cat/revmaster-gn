import pandas as pd
import streamlit as st
from io import StringIO
import base64
from st_aggrid import AgGrid, GridOptionsBuilder
import os
import gitpush
import mysql.connector

# Initial configurations
####################################
st.set_page_config(page_title = 'RevMaster', page_icon = ':books:', layout = 'wide')

config_files = os.listdir('.')

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
        '''with open('initial_config.py', 'w') as f:
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
          f.writelines([l1, l2, l3])'''
        ###
        out = papers_df.to_dict()
        firebase.post("/testupdate", out)
        ###
        '''test_read = open('initial_config.py', 'r')
        lines = test_read.readlines()
        for line in lines:
          st.write(line)
        user = st.secrets['github_user']
        token = st.secrets['github_token']
        repo = st.secrets['github_repo']
        gitpush.git_save('initial_config.py', user, token, repo)'''

else:
  st.text('...')
  test_read = open('initial_config.py', 'r')
  lines = test_read.readlines()
  for line in lines:
    st.write(line)
  from google.cloud import firestore
  # Authenticate to Firestore with the JSON account key.
  db = firestore.Client.from_service_account_json("firestore-key.json")
  # Create a reference to the Google post.
  doc_ref = db.collection("papers").document("a paper")
  doc = doc_ref.get()
  # Let's see what we got!
  st.write("The id is: ", doc.id)
  st.write("The contents are: ", doc.to_dict())

