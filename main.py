#!/c/Users/jlane/AppData/Local/Programs/Python/Python38-32/python

'''
This script creates a CSV file which consists of the total number of messages you have for every Facebook conversation, 
everyday, over time. From here, a bar chart race can be created to visualize your conversations. For more information, 
see the guide at https://towardsdatascience.com/step-by-step-tutorial-create-a-bar-chart-race-animation-da7d5fcd7079. 
Flourish is a program which can create bar chart races, given a CSV file.

To use this script, you must first download your messenger information from Facebook. This script does not make any network calls.
'''

import os, json, csv
from datetime import datetime, timedelta

folders = os.listdir("C://Users/jlane/Desktop/Untracked Files/Facebook Downloads/messages/inbox")

groupByWeek = True # Whether to have a column for each week, vs everyday
isMovingAverage = False # Whether to implement a moving average
movingAveCount = 104 # How many columns to include in calculating the moving average
withGroupChats = False # Whether to include group chats

globalStartDate = None # The date of the earliest message out of every conversation
nowDate = datetime.now().date() # The current date
datesAndTotals = [] # A list of json objects, containing the name, startDate, and messageTotals of each convo
csvData = [[]] # 2D array to be sent to the final CSV

# Get date from timestamp
def getDayFromTime(time):
    day = datetime.fromtimestamp(int(time/1000))
    return day.date() - (timedelta(days=day.weekday() if groupByWeek else 0)) # Return day of the beginning of the week if groupByWeek

# Parse conversation to produce a relevant json object
def parseConvo(data):

    rawMessages = data['messages']
    messageCount = len(rawMessages)
    # Facebook only contains 10000 messages in each message_#.json file
    # If messageCount is 10000, there will be another message_#.json file
    messageFileNum = 2 # The number of the next message_#.json file, if it is read
    while messageCount >= 10000:
        with open(f'C://Users/jlane/Desktop/Untracked Files/Facebook Downloads/messages/inbox/{folder}/message_{messageFileNum}.json') as json_file:
            newData = json.load(json_file) # Load the data
            rawMessages = rawMessages + newData['messages'] # Put the data all together
            messageCount = len(newData['messages']) # Prepare to check if there's another message_#.json file
            messageFileNum += 1
            
    messages = rawMessages[::-1] # Reverse list of messages so they're ordered by increasing date

    startTime = messages[0]['timestamp_ms']
    startDate = getDayFromTime(startTime)
    global globalStartDate
    if not globalStartDate or startDate < globalStartDate:
        globalStartDate = startDate # Set globalStartDate if this conversation has the earliest message ( so far)

    iterDate = startDate # Iterate through everyday until the final message has been read, or we reach the current day
    messageTotalsByDate = [] # Array showing number of total messages at each day
    messageCounter = 0 # Increments each time we read another message
    movAgeMessageCounter = 0 # Increments each time we read another message which is "expired" given a moving average
    while (iterDate <= nowDate and messageCounter < len(messages)):
        while (messageCounter < len(messages) and getDayFromTime(messages[messageCounter]['timestamp_ms']) == iterDate):
            messageCounter += 1
        while (isMovingAverage and 
            getDayFromTime(messages[movAgeMessageCounter]['timestamp_ms']) == 
            iterDate - timedelta(days=(7 if groupByWeek else 1)*movingAveCount)):
            movAgeMessageCounter += 1
        messageTotalsByDate.append(messageCounter-movAgeMessageCounter)
        iterDate += timedelta(days=(7 if groupByWeek else 1)) # Increment date by 1 or 7
    return {
        "name": data['title'],
        "startDate": startDate,
        "messageTotals": messageTotalsByDate
    }

# For each conversation
for folder in folders:
    with open(f'C://Users/jlane/Desktop/Untracked Files/Facebook Downloads/messages/inbox/{folder}/message_1.json') as json_file:
        data = json.load(json_file) # Load the data
        if (len(data['participants']) == 2) or withGroupChats: # Logic for including group chats or not
            datesAndTotals.append(parseConvo(data))

# Make first row of CSV which is just dates
iterDate = globalStartDate
csvData[0].append("") # Set csvData[0][0] to be empty
while (iterDate <= nowDate): # For each date from the globalStartDate until now
    csvData[0].append(iterDate) # Append date
    iterDate += timedelta(days=(7 if groupByWeek else 1)) # Increment date by 1 or 7

# Make rows for each conversation
for convoData in datesAndTotals:
    # Shift conversations so that they all align correctly
    shift = (convoData['startDate'] - globalStartDate).days/(7 if groupByWeek else 1) + 1 # Shift all days by at least one so the first column is 0
    csvRow = [0] * int(shift) + convoData['messageTotals'] # Insert 0s initally, followed by the actual message totals
    csvRow.insert(0, convoData["name"]) # Insert name of person in conversation
    csvData.append(csvRow)

# Write to CSV
with open("messengerRace.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(csvData)

print("Complete!")
