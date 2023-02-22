import json
import re
import traceback
# Important: FIRST install more_itertools in Visual Studio's terminal using 'npm install more_itertools'
from more_itertools import map_except
from glob import glob

# Select files in your current directory that begin with 'facebook_message'
fbMesFiles = glob('*fb_mes*')

# Check which files have been selected
print(fbMesFiles)

# Loop over files in list
for each_file in fbMesFiles:

  # Initialize a variable to store cleaned-up messages in
  newmessages = []
 
  print(each_file)

  with open(each_file, encoding='utf-8') as f:
    data = json.load(f)
    print(data)

  try:
    # Extract message content from data file
    messages = map_except(lambda message: message['content'], data['messages'],KeyError)
  except Exception as e:
    traceback.print_exc()
    
  try:  
    # this replaces the offending string with an actual utf-8 curly single quote!
    # https://patrickwu.space/2017/11/09/python-encoding-issue/
    for x in messages:
      output_string = x
      output_string = re.sub(r'[\xc2-\xf4][\x80-\xbf]+',lambda m: m.group(0).encode('latin1').decode('utf8'),x) 
      newmessages.append(output_string)
  except Exception as e:
    traceback.print_exc()
    
  # or this works, but just deletes the characters...
  # might be fine depending on what you're doing with the data!
  #newmessages = [x.encode('ascii', 'ignore') for x in messages]

  # new
  senders = map(lambda sender: sender['sender_name'], data['messages'])

  #fix ASCII-interpretation of what is actually UTF-8 coded text
  senders = [y.encode('utf-8').decode('utf-8') for y in senders]

  # Printing to text file (hopefully), each file's data to a new line
  with open("output_messages.txt", "a", encoding='utf-8') as f:
    print(list(newmessages), file=f)

  with open("output_senders.txt", "a") as f:
    print(list(senders), file=f)

# Having each data file on a new line is good for visual check, 
# but for formatting all data should actually be on one line, 
# which is what we'll do now for both the MESSAGES file and the SENDERS file
# and save to new output files to be used in the next R script

## For Messages file
with open('output_messages.txt','r') as file1:
    with open('output_messages_formatted.txt','w') as file2:
        file2.write(file1.read().replace('\n', ''))
## For Senders file
with open('output_senders.txt','r') as file1:
    with open('output_senders_formatted.txt','w') as file2:
        file2.write(file1.read().replace('\n', ''))

# IMPORTANT: AFTER YOU'VE DONE THIS, THERE IS ONE THING YOU NEED TO DO MANUALLY: 
# GO TO THE VERY END OF THE LINE IN EACH FILE AND HIT ENTER (TO CREATE A NEW EMPTY LINE)