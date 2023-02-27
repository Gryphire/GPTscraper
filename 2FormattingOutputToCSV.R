
# SCRIPT FOR FORMATTING THE .TXT FILES WITH MESSAGES AND SENDERS INTO A PALATABLE .CSV FILE
# FOR USE IN OPEN AI FINETUNING PROCESS
# compiled by Nastasia Griffioen, 2022/2023

# Libraries
library(dplyr)
library(stringr)
library(tidyverse)
library(tcltk)

# Function for selecting directory with a contingency for some rare Windows use cases
choose_directory = function(caption = 'Please select your Finetuning folder') {
  if (exists('utils::choose.dir')) {
    choose.dir(caption = caption) 
  } else {
    tk_choose.dir(caption = caption)
  }
}

# Asking user to set working directory through dialog prompt
setwd(choose_directory())

# Reading in file with message contents
# WITH TWITTER DATA: FOR SOME REASON THE PARSING DOESN'T WORK ANYMORE AROUND THE ii Type Quiz TWEET! Find out why!
outputdata_messages <- as.data.frame(t(read.table("output_messages_formatted.txt", sep = ",", header=FALSE, encoding="UTF-8")))
colnames(outputdata_messages) <- c("Message")
outputdata_messages$rownum <- c(1:length(outputdata_messages$Message))

# Reading in file with sender names
outputdata_senders <- as.data.frame(t(read.table("output_senders_formatted.txt", sep = ",", header=FALSE, encoding="UTF-8")))
colnames(outputdata_senders) <- c("Sender")
outputdata_senders$rownum <- c(1:length(outputdata_senders$Sender))

# Merge messages and their senders together into one data frame
outputdata <- merge(outputdata_senders, outputdata_messages, by.y="rownum")

# We know that there will be values in the Sender column that contain square brackets. 
# Let's remove the rows corresponding to those cases first.
outputdata <- filter(outputdata, !grepl("\\[",Sender))

## Now we want to remove the rows that do NOT belong to the user. To do this, we first need to establish (again, since variables
## do not transfer between Python and R environments) the user's name from the set of names we have.
# First get an overview of the different Sender variants we have in the data.
senderOverview <- unique(outputdata$Sender)

# Ask user to identify which of these is their name
userName <- tk_select.list(senderOverview, preselect = NULL, multiple = FALSE,
               title = 'Please select your name from the list below:')

# Remove rows in which sender is not Nastasia Griffioen
outputdata_filtered <- outputdata %>% filter(outputdata$Sender==userName)

# Add new empty column
outputdata_filtered$prompt <- ""

# Remove first two columns (rownum and Sender)
outputdata_filtered <- outputdata_filtered[,-c(1:2)]

# Reverse order of the columns so that messages will be under "completion" rather than under "prompt"
outputdata_filtered <- rev(outputdata_filtered)

# Renaming first column to prompts
colnames(outputdata_filtered) <- c("prompt","completion")

# Now that the structure is fine, clean out the data
# Following function created by RDRR on Stackoverflow: 
# https://stackoverflow.com/questions/31348453/how-do-i-clean-twitter-data-in-r
clean_tweets <- function(x) {
  x %>%
    # Remove URLs
    str_remove_all(" ?(f|ht)(tp)(s?)(://)(.*)[.|/](.*)") %>%
    # Remove mentions e.g. "@my_account"
    str_remove_all("@[[:alnum:]_]{4,}") %>%
    # Remove hashtags
    str_remove_all("#[[:alnum:]_]+") %>%
    # Replace "&" character reference with "and"
    str_replace_all("&amp;", "and") %>%
    # Remove "RT: " from beginning of retweets
    str_remove_all("^RT:? ") %>%
    # Replace any newline characters with a space
    str_replace_all("\\\n", " ") %>%
    # Remove any trailing whitespace around the text
    str_trim("both")
}

# Run function on completion column
outputdata_filtered$completion = outputdata_filtered$completion %>% clean_tweets

# Save data frame as csv to your current working directory (to check, use getwd())
write.csv(outputdata_filtered,'trainingdata.csv', row.names = FALSE)
