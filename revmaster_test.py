import pandas as pd
import streamlit as st
import base64
from st_aggrid import AgGrid, GridOptionsBuilder
import os
#import gitpush

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
      project_description = st.text_area('Text to analyze', '...')
      criteria = st.text_area('Assessment criteria', 'one\nper\nline')
      save_1 = st.form_submit_button("Save")
    if save_1:
      st.write(project_title, project_description)
      with open('configs/initial_config.py', 'w') as f:
        l1 = 'project_title = ' + project_title + '\n'
        l2 = 'project_description = ' + project_description + '\n'
        l3 = 'criteria = ' + criteria + '\n'
        f.writelines([l1, l2, l3])
      test_read = open('configs/initial_config.py', 'r')
      lines = test_read.readlines()
      for line in lines:
        st.write(line)
      
      

else:
  st.text('...')

