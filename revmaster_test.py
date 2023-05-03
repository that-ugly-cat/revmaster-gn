import pandas as pd
import streamlit as st
import base64
from st_aggrid import AgGrid, GridOptionsBuilder
import os
import gitpush

# Initial configurations
####################################
st.set_page_config(page_title = 'RevMaster', page_icon = ':books:', layout = 'wide')

config_files = os.listdir('configs')
st.text(config_files)
