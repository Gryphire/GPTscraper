
# Libraries
library(dplyr)
library(stringr)

# Working directory
setwd('/Users/nastasia/Desktop/Python/')

# Reading in file with message contents
outputdata_messages <- as.data.frame(t(read.table("output_messages_formatted.txt", sep = ",", header=FALSE, encoding="UTF-8")))
colnames(outputdata_messages) <- c("Message")
outputdata_messages$rownum <- c(1:length(outputdata_messages$Message))

# Reading in file with sender names
outputdata_senders <- as.data.frame(t(read.table("output_senders_formatted.txt", sep = ",", header=FALSE, encoding="UTF-8")))
colnames(outputdata_senders) <- c("Sender")
outputdata_senders$rownum <- c(1:length(outputdata_senders$Sender))

# Merge messages and their senders together into one data frame
outputdata <- merge(outputdata_senders, outputdata_messages, by.y="rownum")

# Remove rows in which sender is not Nastasia Griffioen
outputdata_filtered <- outputdata %>% filter(outputdata$Sender==" Nastasia Griffioen")

# Add new empty column
outputdata_filtered$prompt <- ""

# Remove first two columns (rownum and Sender)
outputdata_filtered <- outputdata_filtered[,-c(1:2)]

# Reverse order of the columns so that messages will be under "completion" rather than under "prompt"
outputdata_filtered <- rev(outputdata_filtered)

# Renaming first column to prompts
colnames(outputdata_filtered) <- c("prompt","completion")

# Save data frame as csv
write.csv(outputdata_filtered,'/Users/nastasia/Desktop/Python/trainingdata_fbmessages.csv', row.names = FALSE)


