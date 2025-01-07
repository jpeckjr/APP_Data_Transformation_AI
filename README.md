# APP_Data_Transformation_AI

After cloning the repo from GitHub, you will need to do the following steps to run the APP locally:

1. create 2 folders in the main directory /APP_Data_Transformation_AI, one needs to be named 'download_files' and the other needs to be named 'upload_files'. The names need to be identical, cannot be 'Download_Files' for example. 

2. Make sure you have downloaded Python. The current version I have is Python 3.12.2, so if you can, download that version. 

3. Download the latest version of PIP. I recommend Hombrew for Mac, here is the command:  
            /bin/bash -c “$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)”

4. Install Flask: https://flask.palletsprojects.com/en/stable/installation/

5. Use pip to install the python libraries that will be needed:
   Flask, Pandas, re, openai, os, werkzeug.utils(included in Flask), send2trash

6. Create an OpenAI account and create and API key: https://platform.openai.com/api-keys (API key will go on line 95 of APP.py file)
