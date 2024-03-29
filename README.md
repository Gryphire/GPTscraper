# GPT Social Media Scraper Instruction Document
How to Generate a CSV File for Finetuning from Facebook Messenger & Twitter Data + Running Finetuning
compiled by Nastasia Griffioen on February 22nd 2023, updated on March 24th 2023.

### IMPORTANT
Currently only supports Facebook Messenger and/or Twitter data. You can use either Facebook Messenger files if you have those locally saved in your folder (see below) and/or Twitter data (no local data log files needed for that). 

### Instruction Steps
#### DATA DOWNLOAD 
Note: Do this well in advance before scraping, since the Facebook Data Download may take a while to be ready for downloading.

1.	Log in to your Facebook account and download your data file on your laptop/desktop.
    * Click on your profile image in the top right
    * Click on Settings & Privacy
    * Click on Settings
    * Click on Privacy
    * Click on Your Facebook Information
    * Click on View next to Download Profile Information
    * Under Select File Options, choose Format JSON and Date Range All Time
    * Under Select Information to Download, click Deselect All
    * Once all data types are deselected, reselect Messages
    * Scroll to the very bottom and hit Request a Download. Note: it may take some time for the download to be ready, so do this in advance of the workshop. 
2.	On your Desktop, create a folder called Finetuning (or any other name you desire, just make sure you adapt future steps accordingly).
3.	Go to Github and download the required script. https://github.com/Gryphire/GPTscraper Save them to your Finetuning folder.
4.	Once you have downloaded your data package, which will be in the form of a .zip file, open it up.
    * Select the Messages folder, and copy-paste it into your Finetuning folder. 

#### SOFTWARE PREP
1.	Set up OpenAI (for both Mac and Windows users):
    * Create an OpenAI account on https://beta.openai.com/signup 
2.	Installing Xcode and Homebrew (for Mac users only!):
    * For Xcode:
      * Check if you have Xcode installed. In your Terminal, type ‘xcode-select -p’. If a path is returned, you have Xcode already installed.
      * If you still need to get Xcode, go to the App Store on your Mac, search for Xcode and download+install from the App Store.
      * Final step is to ensure you have the command line tools associated with Xcode installed as well. Head to your Terminal and type in: Xcode-select --install
      * Once you do this, you should have all necessary Xcode tools installed!
    * For Homebrew: 
      * Follow the instructions in this video: https://drive.google.com/file/d/19fApnIlCoWIKPVIP7EbpgHH6HNorXSCb/view?usp=share_link Note: The Homebrew installation might take some time (e.g., 10 minutes or more), so keep that in mind.  
3. Installing Python 3 (for both Mac and Windows users):
    * For Mac users:
      * Checking if Python 3 is already installed on your machine. To check this, go to the Terminal and type: ‘python3 --version’. If it returns a Python version as response, you know you have Python 3 installed already.
      * If you find that you need to install Python 3, do this through the Terminal once more: ‘brew install python3. Please note: the installation of Python 3 may take up to 30 minutes, so keep this in mind. 
    * For Windows users:
      * Checking is Python 3 is already installed on your machine.
      * If you find that you need to install Python 3, first go to the Python website (www.python.org.downloads). 
      * Hit ‘Download the Latest Version for Windows’. 
      * Once the download is complete, run the .exe file. 
      * Make sure that you check ‘Add Python to PATH’ on the first installation screen. 
      * On the final installation screen, make sure to click ‘Disable path limit length’.
      * Once installation is complete, open your Command Prompt (NOTE: NOT your Python prompt, but the Command Prompt!) and run the following command (but remember to insert your own username first): cd C:\Users\<username>\AppData\Local\Programs\Python. 
      * Now that you are located in the installation folder, check that the installation has gone well by typing in: python.exe. If this command returns a Python version that matches the one you download from the Python website, the installation has gone to plan. 
      * Make sure you exit the command prompt because now you are in the python interpreter. Exit and restart the Command Prompt.

#### RUNNING THE SCRAPER SCRIPTS
1.	Time to run the first script, which is 1JSONParseToOutput.py. Open Terminal (or Command Prompt) and ensure you’re in the Finetuning folder. On Mac, use ‘cd Desktop/Finetuning’ to do this. On Windows, you can try the same command. If it doesn’t work, you might have to specify the full path (more like ‘cd C:\Users\<username>\Desktop\Finetuning’). Remember to change this command based on your chosen name for your folder. Fun fact to help you remember this command: ‘cd’ stands for ‘change directory’. (:
    * You can see that you’ve succeeded in changing the directory if the path before > changed.
2.	Still in the Terminal, now type in ‘python 1JSONParseToOutput.py’ and hit Enter to run.  If this does not work for you, try ‘python3 1JSONparseToOutput.py’ instead. 
    * When the script is running, you will see messages and questions be printed to the Terminal/Command Prompt console. Please answer these as required to help the script perform its tasks.
3.	Check that the script has succeeded by taking a look in your Finetuning folder. You should see a new file there, called ‘trainingdata.csv’. Open it up, and you will see two columns: the first column being called ‘prompt’ and being empty, and the second column being called ‘completion’, with all of your messages in that column. Now you’re ready to start finetuning!


#### FINETUNING
1.	Open your Terminal/Command Prompt again if necessary, and make sure you are in your Finetuning folder (for Terminal, use the pwd command if needed to check). 
2.	We now first need to ensure your .csv trainingdata file is formatted before we can ask OpenAI to finetune a model on it. Luckily OpenAI has a tool for this, which we will run from the Terminal. Type in: ‘openai tools fine_tunes.prepare_data -f trainingdata.csv’. You will see that as a result of this operation a .JSONL file will be added to your Finetuning folder.
    * OpenAI might ask you to respond to some questions. It might highlight some duplicate rows, and other formatting requests (of which it will take care itself if you agree). 
    * When the generation of your formatted file is complete, you should be able to see that OpenAI also gives an indication of how long the actual finetuning of a model with this training data file might take.
3.	Before we can finetune, OpenAI needs to know your API key. Get this from your profile on https://platform.openai.com/overview, click on your Profile picture on the top right and click on View API Keys. If you do not have one yet, click on Create New Secret Key. Copy the API key. 
4.	Setting the OpenAI API Key:
    * On Mac: In your Terminal, type in export OPENAI_API_KEY="<OPENAI_API_KEY>”, and substitute <OPENAI_API_KEY> with the key you just copied from the OpenAI website. Hit Enter. 
    * On Windows: In the Command prompt, type in setx OPENAI_API_KEY “<KEY>”, and substitute <KEY> with the key you just copied from the OpenAI website (make sure you leave the “ in the command). Hit Enter. 
      * For Windows users there is then one more step necessary to process this key setup: close the Command Prompt window and restart the Command Prompt. Remember to re-navigate into your Finetuning folder. For some reason, restarting the Command Prompt is necessary on Windows in order to Windows to process the change. Please note: when you do restart the Command Prompt, you will not see anything to indicate that the change has been processed. You have to trust the process. (:
5.	Finally, time to initiate finetuning! In your Terminal, type: openai api fine_tunes.create -t trainingdata_prepared.jsonl -m davinci. No need to specify the whole path, as long as your current directory within the Terminal is still your Finetuning folder.
6.	You shall see that the OpenAI API will start finetuning. Finetuning may take a long time.  Using the commands offered in the Terminal you will be able to check back in every once in a while to track the progress of your finetuning job.
7.	When you see that the finetuning job is complete, log back in to OpenAI at https://platform.openai.com/overview and head to the Playground. In the Playground, you will see that you can select a Model in the right hand toolbar. Scroll down to find a model with the date of when you finetuned your model (the model’s name will look something like davinci:ft-personal-yyyy-mm-dd-etc.)
