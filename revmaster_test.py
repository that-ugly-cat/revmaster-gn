Skip to content
Search or jump to…
Pull requests
Issues
Codespaces
Marketplace
Explore
 
@that-ugly-cat 
that-ugly-cat
/
streamlit-example
Public
forked from streamlit/streamlit-example
Cannot fork because you own this repository and are not a member of any organizations.
Code
Pull requests
Actions
Projects
Wiki
Security
Insights
Settings
streamlit-example
/
streamlit_app.py
in
master
 

Spaces

4

No wrap
1
import pandas as pd
2
import streamlit as st
3
import base64
4
from st_aggrid import AgGrid, GridOptionsBuilder
5
import os
6
import gitpush
7
import supabase_revmaster
8
​
9
# Initial configurations
10
####################################
11
st.set_page_config(page_title = 'RevMaster', page_icon = ':books:', layout = 'wide')
12
pdf_file = 'start.pdf'
13
​
14
### supabase configuration
15
##secrets
16
supa_url = st.secrets['supabase_url']
17
supa_key = st.secrets['supabase_key']
18
​
19
# load methodology options
20
supa_table = 'methodology_options'
21
message = supabase_revmaster.get_table(supa_url, supa_key, supa_table)
22
methodology_options = []
23
try:
24
    for row in message.data: 
25
        methodology_options.append(row['methodology'])
26
except:
27
    st.error("Oops! There is something wrong with your methodology options table.\nThe table must be called \'methodology_options\' and contain one methodology option per row in the column \'methodology\'.")
28
        
29
# load study type options
30
supa_table = 'study_type_options'
31
message = supabase_revmaster.get_table(supa_url, supa_key, supa_table)
32
studytype_options = []
33
try:
34
    for row in message.data: 
35
        studytype_options.append(row['study type'])
36
except:
37
    st.error("Oops! There is something wrong with your study type options table.\nThe table must be called \'study_type_options\' and contain one study type option per row in the column \'study type\'.")
38
        
39
# load include options
40
supa_table = 'include_options'
41
message = supabase_revmaster.get_table(supa_url, supa_key, supa_table)
42
include_options = []
43
try:
44
    for row in message.data: 
45
            include_options.append(row['include'])
@that-ugly-cat
Commit changes
Commit summary
Create streamlit_app.py
Optional extended description
Add an optional extended description…
 Commit directly to the master branch.
 Create a new branch for this commit and start a pull request. Learn more about pull requests.
 
Footer
© 2023 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Docs
Contact GitHub
Pricing
API
Training
Blog
About
