# Welcome the user to the script (:
print('*------------------------------*')
print('Welcome to this social media data scraper script!')
print('*------------------------------*')

#-----------------------------------------#
## IMPORTING THE NECESSARY LIBRARIES
import sys
import json
import re
import traceback
import os
import subprocess
from glob import glob
from difflib import get_close_matches
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askdirectory

# Check if more_itertools package is already present, if not then first install then import
try:
  from more_itertools import map_except
except:
   subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'more_itertools'])
   from more_itertools import map_except

# Check if snscrape package is already present, if not then first install then import
try:
  # Sometimes snscrape gets updated which may break the tweet retrieval
  #os.system("python -m pip install --upgrade snscrape")
  import snscrape.modules.twitter as snt
except:
   subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'snscrape'])
   import snscrape.modules.twitter as snt

# Check if snscrape package is already present, if not then first install then import
try:
  import pandas as pd
except:
  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas'])
  import pandas as pd

# HERE, we also already install OpenAI's API if it's not on people's machine yet, 
# so users son't have to do this manually
# This package will NOT be used within this script, but hopefully this way it still gets recognised
try:
  'openai' in sys.modules
except:
  os.system("python -m pip install --upgrade openai")

#-----------------------------------------#
## GENERAL VARIABLE SETUP
# The warnings of chained assignment are disabled here because 
# cleaning the dataset further down the script gives a false positive warning
pd.options.mode.chained_assignment = None  # default='warn'


#-----------------------------------------#
## PROCESS FOR DATA THAT NEEDS TO BE RETRIEVED FROM LOCAL DATA LOG FILES

# DATA INCLUSION CHECK
# Create a variable so we can keep track of whether or not people gave a valid response
FBMesDecisionMade = 0
# Check for valid response
while FBMesDecisionMade == 0:
  # Ask user if they want to use Facebook Messenger data files or now (if not, skip to next data type)
  FBMesDecision = input("Would you like to scrape data from your local Facebook Messenger data files? [Y/N] ")
  print('*------------------------------*')
  if (FBMesDecision == 'Y') or (FBMesDecision == 'y') or(FBMesDecision == 'N') or (FBMesDecision == 'n'):
    FBMesDecisionMade = 1
  else:
    print('Sorry, that is not considered valid input. Please answer with either Y or N.')

# INITIALIZE COUNTERS
# Set a counter for Facebook Messenger file looping (will be used later to make sure name check is done only once, for first file)
fbmescounter = 0

#Preparing an empty dataset to fill based out of temporary storage
outputdf = pd.DataFrame(columns=["sender", "message"])

# Initialize a variable to store cleaned-up messages in
newdata = []
messages = []

# If the user indicated to want to use FB Messenger data, do the following:
if (FBMesDecision == 'Y') or (FBMesDecision == 'y'):
  
  #-----------------------------------------# 
  ## FACEBOOK MESSENGER DATA
  #-----------------------------------------# 

  # Prepare an empty list for the data file paths to be stored in
  dataFiles = []
  # Create an empty list to be filled with small dataframes
  outputdflist = []
  # First define the search directory (that is ./messages/inbox/)
  currentdir = os.getcwd()
  searchdir = currentdir + '/messages/inbox/'

  # # Ask user whether they want to run through all files or whether they
  # ownSelection = input('You can either (A) let the script collect info from all of the message data files that it can find, or (B) you can point it to a specific folder in which you have placed selected message data files. What do you choose? [A/B] ')
  # print('*------------------------------*')
  # # Act on the user's input; ask to specify folder if they've chosen that they want to choose themselves
  # if (ownSelection == 'B') or (ownSelection == 'b'):
  #   searchdir = askdirectory(title='Select the subfolder in which you have placed your selected messages_1.json files')
  #   print(searchdir)
  # else:
  #   # First define the search directory (that is ./messages/inbox/)
  #   currentdir = os.getcwd()
  #   searchdir = currentdir + '/messages/inbox/'

  ## SCANNING FOR MESSAGES_1.HTML FILES
  # Now that we've defined the search directory, scan it for .html files
  for dirpath, dirnames, filenames in os.walk(searchdir):
    for filename in [f for f in filenames if f.endswith(".json")]:
        dataFiles.append(os.path.join(dirpath, filename))

  # Ask user how many Facebook Messenger data files they want to scrape
  print(str({len(dataFiles)}) + ' Facebook Messenger files have been found.')
  print('*------------------------------*')
  N = input('How many data files do you want to scrape?\nIf you want to scrape all the files, choose the total number indicated above.\nIf you choose a number lower than the total, the first x files will be retrieved.\nPlease enter the number and hit Enter. ')
  print('*------------------------------*')

  # Loop over files in list
  for each_file in dataFiles[0:int(N)]:

    with open(each_file, 'r') as f:
      textdata = json.load(f)
  
    # Work through each Facebook Messenger file:
    if each_file.find("messages") != -1:
      
      # Update file counter (because we want to run a name check later, but only once)
      fbmescounter += 1
      
      print('Currently working on Facebook Messenger data file number ' + str(fbmescounter))
      print(each_file)
      print('*------------------------------*')

      # Extract sender data from data file
      senders = map(lambda sender: sender['sender_name'], textdata['messages'])
      # fix ASCII-interpretation of what is actually UTF-8 coded text
      senders = [y.encode('utf-8').decode('utf-8') for y in senders]

      # Ask user to indicate their own name
      if fbmescounter == 1:
        # For the very first Facebook Messenger file, we want to check which name in the senders file is the user's, 
        # so we know what name to use in the future
        # So first we need to check the different values present in the list, 
        # we do this by turning the list into a set
        setOfSenders = set(senders)
        # Next we turn the set back into a list so we can access the items mentioned within (this is not possible with a set)
        listOfSenders = list(setOfSenders)
        # Present these options to the user so they can select their own name
        usersNameIndex = int(input('The following participants have been detected in your first Facebook Messenger file:\n'+ str(listOfSenders) +'\nPlease tell us which of these is you by typing in the number associated\nwith the name position in the list (e.g., 1 if the first name is yours): '))
        print('*------------------------------*')
        # Now we can save the user's  name from the list of senders. 
        # Since Python is zero-indexed, we need to correct the input number to 
        # match the positions as Python counts them (i.e., first position is indexed as 0)
        # Note: it may very well be that this is not close to the person's actual name since this is based on the
        # Facebook username. If you have NassieBal as your username on Facebook, then this is what will be used as the 
        # userIdentifier. The actual name used is not of great importance, it is simply important to make sure that 
        userIdentifier = listOfSenders[usersNameIndex-1]

      #Function to load the Messenger data
      with open(each_file, 'r',encoding="utf-8") as f:
        full_dict = json.load(f)
        part = full_dict["participants"]
        msg = full_dict["messages"]
      
      #Temporarily storing the data
      dictdf = pd.DataFrame(full_dict["messages"])

      #Filling the dataset with sender name and message per row
      # Go through all rows
      for index, row in dictdf.iterrows():
        tempoutputdf = pd.DataFrame({"sender": [dictdf.iloc[index]['sender_name']],
                                    "message": [dictdf.iloc[index]['content']]})
        outputdflist.append(tempoutputdf)
      # Turn this into the master output dataframe
      outputdf = pd.concat(outputdflist, ignore_index=True)

      #User check
      #print(outputdf)
      
      try:
        for index, s in outputdf['message'].items():
          try:
              string_tobefiltered = re.sub(r'[\xc2-\xf4][\x80-\xbf]+',lambda m: m.group(0).decode('unicode-escape').encode('latin1').decode('utf-8'),str(s))
              outputdf[index]['message'] = string_tobefiltered 
          except (AttributeError, KeyError): 
            pass
      except Exception as e:
        pass
        traceback.print_exc()

# Let the user know where we are in the process
if FBMesDecision == 'y' or FBMesDecision == 'Y':
  print('Facebook Messenger data have been extracted from local files.')
  print('*------------------------------*')
else:
  print('No Facebook Messenger data will be collected, moving on!')
  print('*------------------------------*')

#-----------------------------------------#
## TWITTER DATA
#-----------------------------------------# 

TwitDecisionMade = 0
# Check for valid response
while TwitDecisionMade == 0:
  # Ask user if they want to use Twitter data
  TwitDecision = input("Would you like to scrape data from your Twitter account? This will collect your Tweets. [Y/N] ")
  print('*------------------------------*')
  if (TwitDecision == 'Y') or (TwitDecision == 'y') or(TwitDecision == 'N') or (TwitDecision == 'n'):
    TwitDecisionMade = 1
  else:
    print('Sorry, that is not considered valid input. Please answer with either Y or N.')

# Make sure that code is NOT run if user entered N
if (TwitDecision == 'Y') or (TwitDecision == 'y'):

  TwitNameCorrect = 0
  while TwitNameCorrect == 0:
      # Query user for the Twitter user name, if not provided skip the rest of the Twitter code
      TwitName = input("Please enter your Twitter username and hit Enter: ")
      print('*------------------------------*')
      TwitNameCheck = input("You entered '" + TwitName +"' as your Twitter username. Is this correct? [Y/N] ")
      if (TwitNameCheck == 'Y') or (TwitNameCheck == 'y'):
        print('Wonderful, we will proceed with scraping your Twitter posts now.\nPlease stand by, this may take a while.')
        print('*------------------------------*')
        TwitNameCorrect = 1
      elif (TwitNameCheck == 'N') or (TwitNameCheck == 'n'):
        print('Ok, give it another try!')
      else:
        print('Sorry, but that is not considered valid input. Please respond with Y or N.')

  # Prepare variable
  #tweet_collection = pd.DataFrame(columns=["sender", "message"])

  # Get the data and append do frame depending on whether FB Mes data is already present or not
  # IF THERE'S NO FACEBOOK MESSENGER DATA:
  if FBMesDecision == "N" or FBMesDecision == "n":
    userIdentifier = TwitName
    for tweet in snt.TwitterSearchScraper(f'from:{TwitName}').get_items():
      outputdf = outputdf.append({
        "sender": tweet.user.username,
        "message": tweet.rawContent,},ignore_index=True)
  # IF THERE IS ALREADY FACEBOOK MESSENGER DATA
  else:
    for tweet in snt.TwitterSearchScraper(f'from:{TwitName}').get_items():
      outputdf = outputdf.append({
        "sender": userIdentifier,
        "message": tweet.rawContent,},ignore_index=True)

  #with open("output.txt","a",encoding='utf-8') as f:
  #  dfTwitAsString = outputdf.to_string(header=False, index=False)
  #  f.write(dfTwitAsString)
  
  print('Twitter scraping completed!')
  print('*------------------------------*')

# MOVING ON TO THE REST OF THE SCRIPT, IF APPLICABLE
else:

  print("No Twitter data will be collected, moving on!")
  print('*------------------------------*')

#-----------------------------------------#

## SCRAPING COMPLETE!

print('The end of the scraping script has been reached. Smiley day to ya!')
print('*------------------------------*')

# DATA CLEANUP IS ONLY NEEDED IF AT LEAST SOME DATA HAVE BEEN GATHERED
# Since it is technically possible that a user answers 'no' to both gathering FB Messenger data and Twitter data,
# we need to check wither any data has been gathered before running the cleanup.

if (FBMesDecision == "Y") or (FBMesDecision == "y") or (TwitDecision == "Y") or (TwitDecision == "y"):

  # MOVING ON TO DATAFRAME CLEANUP
  # We now thus have a data frame (dfoutput) which contains all senders and all messages
  # The steps needing to be taken are now as follows:
  # 1. all rows that do NOT pertain to the user need to be taken out
  # 2. data need to be cleaned up; removing emotji's, weird strings, URLs etc.
  # 3. the resulting dataframe shoul be saved to a CSV with two columns: an empty 'prompt' column, and 'completion' filled with the messages

  #--------------------------#
  # 1 REMOVING NON-USER ROWS

  # Note that this is ONLY necessary if Facebook Messenger data have also been scraped (not if there's only Twitter data)
  # Check that Facebook Messenger data were indeed used
  usernameList = userIdentifier.split(maxsplit=0)
  # Filter out non-user if FB MES was gathered
  if (FBMesDecision == "Y") or (FBMesDecision == "y"):
    outputdf_onlyUser = outputdf[outputdf['sender'].isin(usernameList)]
  # If only Twitter data was used, then we can use the outputdf as is
  else:
    outputdf_onlyUser = outputdf

  #-------------------------#
  # 2 CLEANING UP TEXT DATA

  # Removing NaNs (induced by some instances of 'senders' not having 'content')
  outputdf_onlyUser = outputdf_onlyUser.dropna(subset=['message'])
  # Removing URLs
  outputdf_onlyUser['message'] = outputdf_onlyUser['message'].str.replace(r'\s*https?://\S+(\s+|$)', '', regex=True).str.strip()
  # Removing @'s
  outputdf_onlyUser['message'] = outputdf_onlyUser['message'].str.replace(r'@[^\s]+', '', regex=True).str.strip()
  # Removing hashtags (but not the string that follows the # to maintain meaning of text)
  outputdf_onlyUser['message'] = outputdf_onlyUser['message'].str.replace(r'#', '', regex=True).str.strip()
  # Removing emoji/emoticons and all other special characters
  emoji_pattern = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    u"\U0001f926-\U0001f937"
    u'\U00010000-\U0010ffff'
    u"\u200d"
    u"\u2640-\u2642"
    u"\u2600-\u2B55"
    u"\u23cf"
    u"\u23e9"
    u"\u231a"
    u"\u3030"
    u"\ufe0f"
    "]+", flags=re.UNICODE)
  outputdf_onlyUser['message'] = outputdf_onlyUser['message'].str.replace(emoji_pattern, '', regex=True).str.strip()

  #---------------------------------------------#
  # 3 SAVING TO APPROPRIATELY FORMATTED CSV FILE

  # So now we have a data frame which we can transform into one we want to save as CSV
  # This means getting rid of the sender column (no longer necessary), and renaming the columns to 'prompt' and 'completion
  # Create our empty target dataframe
  outputdf_toCSV = pd.DataFrame(columns=["prompt","completion"])
  # Copy the message column from outputdf_onlyUser into the completion column of the new target df
  outputdf_toCSV["completion"] = outputdf_onlyUser["message"]
  # Replace the NaNs in the empty prompt column with simply an empty string/blank space
  outputdf_toCSV = outputdf_toCSV.replace(np.nan,'',regex=True)

  # Save this target dataframe to a csv file
  outputdf_toCSV.to_csv('trainingdata.csv',index=False)