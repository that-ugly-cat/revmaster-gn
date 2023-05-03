# Import the requests module for send a PUT request
import requests
# Import the base64 module for encoding a file to base64
import base64

def git_save(thisfile, user, token, repo):
  # base url:
  githubAPIURL = 'https://api.github.com/repos/' + user + '/' + repo + '/contents/' + thisfile


  with open(thisfile, "rb") as f:
      # Encoding to base64
      encodedData = base64.b64encode(f.read())

      headers = {
          "Authorization": f'''Bearer {token}''',
          "Content-type": "application/vnd.github+json"
      }
      data = {
          "message": "Data saved from app", # Put your commit message here.
          "content": encodedData.decode("utf-8")
      }

      r = requests.put(githubAPIURL, headers=headers, json=data)
      return(r.text) # Printing the response
