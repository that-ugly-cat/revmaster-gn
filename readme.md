# RevMaster documentation
Reviews of academic literature are often conducted with a rather medieval approach: we basically record annotations on a big excel spreadsheet. Every row is a paper, and every column is either a known or an unknown information. 

You open up your excel file, you open your paper's PDF, read, and annotate. Boring and clumsy. And extremely single-user. And not amazing for ongoing assessments. 

So I've put together this piece of code to speed up and systematize the process a little bit. 
![streamlit-revmaster-2023-05-31-17-05-06.webm](https://github.com/that-ugly-cat/revmaster/assets/98877284/78f0dabc-e45f-4d53-9c8d-96edfc1fea54)

The software lets you analyse the data in real time, as you are assessing your documents. Which can come in handy when you need to present intermediate results.
![streamlit-revmaster-2023-05-31-17-05-21.webm](https://github.com/that-ugly-cat/revmaster/assets/98877284/9ccb2821-9474-4b0a-a436-6fa01f87e09d)

I plan to introduce more functions as soon as I have time - ideally automate the retrieval of the full text files, and potentially integrate the iterative search pipeline (see: [TopicTracker](https://zenodo.org/record/7023618))
## Installation
- fork this git repo
- Generate a new [personal access token (classic)](https://github.com/settings/tokens) - more info [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- note down your username, repo name and access token 
- create a new streamlit app and connect it to the newly forked repo
- paste the following info in the streamlit app's [secrets](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management):
  - github_user = 'your username'
  - github_repo = 'your repo'
  - github_token = 'your token'
- launch the app and go through the setup process
  - upload the [json file containing the information to connect to your firestore account](https://blog.streamlit.io/streamlit-firestore/#tl-dr)
  - copy/paste the parsed code in your [app's secrets](https://share.streamlit.io/) in streamlit. Wait approximately 30 seconds and reload the page.
  - fill in the details about your project
    - project title: displayed on the top of the page.
    - projectdescription: displayed on the top of the page, below the title. Ideally no more than 2-3 lines of text.
    - inclusion criteria: displayed in an accordeon on the top of the assessment column.
    - assessment criteria: one per line (IMPORTANT!). Each criterion will become a text box in the assessment column.
    - firestore collection: no spaces, no special characters. The collection in which these assessments will be saved (it will create a new collection in your firebase account).
    - username and password: (IMPORTANT) note them down because else you will have to recover this information manually via firestore. This user has read and write rights on the data.
    - the CSV file containing your papers to be assessed: the file should contain at least the following columns to function properly: Key (used as unique identifier), Publication Year, Author, Title. I use an export from Zotero, works amazingly well.
    - save: this will record all the details and set up the environment. 
  - upload the PDF files in your github repository, in the folder '/pdfs'. The software uses the author names and the publication title to find the PDF files based on the database entry, so make sure your files are named as follows: Surname - title.pdf, or Surname1, Surname2 - title.pdf, or Surname1, Surname2 et al - title.pdf (this is the default file name for files exported from Citavi.

## Use
### Assessment mode

By default the software runs in 'assessment mode'. This means that all the stuff pertaining the analysis is not loaded to keep things light and fast. In this scenario you have:
- a sidebar: where you can enable'analysis mode', log in with your username/password to switch from read only to read/write mode, and export the entire assessment as an excel file;
- an 'assessment' tab: where you can assess the papers;
- an 'analysis' tab: where you can see some minimal info (number of included/excluded/maybe included / not assessed documents).
### Analysis mode
When you activate the 'analysis mode' you will get more tabs, all of them quite self-explanatory:
- assessment (same as in 'assessment mode');
- papers per year (based on the publication year, not on the year of the study, which might differ)
- authors: frequency analysis of the authors
- manual tags: frequency analysis of the keywords and mesh terms 
- analysis(assessments): NLP analysis (lemma frequency) of the content of the included assessments
- analysis(document details): country, study year, study type, methodology.
