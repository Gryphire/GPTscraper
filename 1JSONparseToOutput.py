
#-----------------------------------------#
## IMPORTING THE NECESSARY LIBRARIES

import json
import re
import traceback
import os
import pandas as pd
import sys

# Important: FIRST install more_itertools in Visual Studio's terminal using 'npm install more_itertools'
from more_itertools import map_except
from glob import glob
from difflib import get_close_matches

# Prior to running, make sure snscrape is installed via VSCode terminal using pip3 install snscrape
import snscrape.modules.twitter as snt

#-----------------------------------------#
## GENERAL VARIABLE SETUP
# Select files in your current directory that begin with 'data_'
dataFiles = glob('data_*')

#-----------------------------------------#
## PROCESS FOR DATA THAT NEEDS TO BE RETRIEVED FROM LOCAL DATA LOG FILES

# DATA INCLUSION CHECK
# Ask user if they want to use Facebook Messenger data files or now (if not, skip to next data type)
FBMesDecision = input("Would you like to scrape data from your local Facebook Messenger data files? Y/N ")

# INITIALIZE COUNTERS
# Set a counter for Facebook Messenger file looping (will be used later to make sure name check is done only once, for first file)
fbmescounter = 0

# Loop over files in list
for each_file in dataFiles:

  # Initialize a variable to store cleaned-up messages in
  newdata = []
  messages = []

  # Pring to the console which data file is being processed now
  #print(each_file)

  if (FBMesDecision == 'Y') or (FBMesDecision == 'y'):
    
    #-----------------------------------------# 
    
    ## FACEBOOK MESSENGER DATA
    
    with open(each_file, encoding='utf-8') as f:
      textdata = json.load(f)

    if each_file.find("fb_mes") != -1:

      # Update file counter (because we want to run a name check later, but only once)
      fbmescounter += 1
      print('Currently working on Facebook Messenger data file number ' + str(fbmescounter))
      
      try:
        # Extract message content from data file
        messages = map_except(lambda message: message['content'], textdata['messages'],KeyError)
      except Exception as e:
        #traceback.print_exc()
        print('Working on it...')

      try:  
        # this replaces the offending string with an actual utf-8 curly single quote!
        # https://patrickwu.space/2017/11/09/python-encoding-issue/
        for x in messages:
          output_string = x
          output_string = re.sub(r'[\xc2-\xf4][\x80-\xbf]+',lambda m: m.group(0).decode('unicode-escape').encode('latin1').decode('utf8'),x) 
          newdata.append(output_string)
      except Exception as e:
        #traceback.print_exc()
        print('Still working on it...')

      # new senders variable
      senders = map(lambda sender: sender['sender_name'], textdata['messages'])
      # fix ASCII-interpretation of what is actually UTF-8 coded text
      senders = [y.encode('utf-8').decode('utf-8') for y in senders]

      if fbmescounter == 1:
        # For the very first Facebook Messenger file, we want to check which name in the senders file is the user's, 
        # so we know what name to use in the future
        # So first we need to check the different values present in the list, 
        # we do this by turning the list into a set
        setOfSenders = set(senders)
        # Next we turn the set back into a list so we can access the items mentioned within (this is not possible with a set)
        listOfSenders = list(setOfSenders)
        # Present these options to the user so they can select their own name
        usersNameIndex = int(input('The following participants have been detected in your first Facebook Messenger file: '+ str(listOfSenders) +'. Please tell us which of these is you by typing in the number associated with the name position in the list (e.g., 1 if the first name is yours): '))
        # Now we can save the user's  name from the list of senders. 
        # Since Python is zero-indexed, we need to correct the input number to 
        # match the positions as Python counts them (i.e., first position is indexed as 0)
        # Note: it may very well be that this is not close to the person's actual name since this is based on the
        # Facebook username. If you have NassieBal as your username on Facebook, then this is what will be used as the 
        # userIdentifier. The actual name used is not of great importance, it is simply important to make sure that 
        userIdentifier = listOfSenders[usersNameIndex-1]

      # Printing to text file (hopefully), each file's data to a new line
      with open("output_messages.txt", "a", encoding='utf-8') as f:
        print(list(newdata), file=f)

      with open("output_senders.txt", "a") as f:
        print(list(senders), file=f)

# Let the user know where we are in the process
if FBMesDecision == 'y' or FBMesDecision == 'Y':
  print('Facebook Messenger data have been extracted from local files.')
else:
  print('No Facebook Messenger data will be collected, moving on!')

#-----------------------------------------#
## TWITTER DATA

# Ask user if they want to use Twitter data
TwitDecision = input("Would you like to scrape data from your Twitter account? This will collect your Tweets. Y/N ")

# Make sure that code is NOT run if user entered N
if (TwitDecision == 'Y') or (TwitDecision == 'y'):

  # Query user for the Twitter user name, if not provided skip the rest of the Twitter code
  TwitName = input("Please enter your Twitter username and hit Enter: ")

  # Prepare variable
  tweet_collection = pd.DataFrame()

  for tweet in snt.TwitterSearchScraper(f'from:{TwitName}').get_items():
    tweet_collection = tweet_collection.append({
        "name":tweet.user.username,
        "completion":tweet.rawContent,},ignore_index=True)

  # Printing to text file (hopefully), each file's data to a new line
  with open("output_messages.txt", "a", encoding='utf-8') as f:
    print(list(tweet_collection.completion), file=f)

  if FBMesDecision == "N" or FBMesDecision == "n":
    userIdentifier = TwitName

  # Need to adapt this to have a matching amount of names (or maybe fix in R?)
  # Determine how many 'senders' there need to be fabricated
  TwitSenderList = [userIdentifier]*len(tweet_collection.completion)
  # Save to the senders file
  with open("output_senders.txt", "a") as f:
    print(TwitSenderList, file=f)
  
  # Let the user know which Twitter username has been scraped 
  print('Based on your input, we have scraped the data for the user "' + str(tweet_collection.name[1]) + '". If this is NOT your Twitter username, please rerun this script and ensure you enter the right Twitter username.')

  # Clear variable so it doesn't keep stacking due to the append option
  del tweet_collection

  print('Twitter scraping completed!')

# MOVING ON TO THE REST OF THE SCRIPT, IF APPLICABLE
else:

  print("No Twitter data will be collected, moving on!")


  """ ## FACEBOOK POSTS DATA
  if each_file.find("fb_posts") != -1:

    # Iterate over each post entry in the data file
    for post in textdata:

      try:
        post_data = post['data'][0]
        # Check if this post instance has a data key, if not = ignore
        if 'post' in post_data:
          try:
            # Convert list to string
            post_text = str(post_data)
            # Select only needed part of post text
            post_text_new = post_text.split("post': ",1)[1]
            print(post_text_new)
            # Save to messages variable
            messages += [post_text_new]
          except:
            pass
      except:
        pass

    try:  
      # this replaces the offending string with an actual utf-8 curly single quote!
      # https://patrickwu.space/2017/11/09/python-encoding-issue/
      for x in messages:
        output_string = x
        # FOR SOME REASON THIS DOESN'T WORK!!
        output_string = re.sub(r'[\xc2-\xf4][\x80-\xbf]+',lambda m: m.group(0).encode('latin1').decode('utf8'),x)
        newdata.append(output_string)
    except Exception as e:
      traceback.print_exc() 
      
    # or this works, but just deletes the characters...
    # might be fine depending on what you're doing with the data!
    #newdata = [x.encode('ascii', 'ignore') for x in messages]

    # new
    senders = map(lambda sender: sender['sender_name'], textdata['messages'])
    # fix ASCII-interpretation of what is actually UTF-8 coded text
    senders = [y.encode('utf-8').decode('utf-8') for y in senders]

    # check?
    print(newdata)

    # Printing to text file (hopefully), each file's data to a new line
    with open("output_messages.txt", "a", encoding='utf-8') as f:
      print(list(newdata), file=f)
    
    print('saving to file successful?')

    with open("output_senders.txt", "a") as f:
      print(list(senders), file=f) """

#-----------------------------------------#

## FINAL TOUCH!

# Having each data file on a new line is good for visual check, 
# but for formatting all data should actually be on one line, 
# which is what we'll do now for both the MESSAGES file and the SENDERS file
# and save to new output files to be used in the next R script

if (FBMesDecision == "Y") or (FBMesDecision == "y") or (TwitDecision == "Y") or (TwitDecision == "y"):

  ## For Messages file
  with open('output_messages.txt','r') as file1:
      with open('output_messages_formatted.txt','w') as file2:
          file2.write(file1.read().replace('\n', ''))
  ## For Senders file
  with open('output_senders.txt','r') as file1:
      with open('output_senders_formatted.txt','w') as file2:
          file2.write(file1.read().replace('\n', ''))

  # Print that everything is done.
  print('The scraping script is now done running and data was collected. Smiley day to ya!')

else:
  print('The end of the scrqping script has been reached. No data were scraped. Smiley day to ya!')

# IMPORTANT: AFTER YOU'VE DONE THIS, THERE IS ONE THING YOU NEED TO DO MANUALLY: 
# GO TO THE VERY END OF THE LINE IN EACH FILE AND HIT ENTER (TO CREATE A NEW EMPTY LINE)
# IF YOU DO NOT DO THIS, THE R SCRIPT WILL STILL RUN BUT IT WILL THROW AN END OF LINE ERROR