import os
import sys
import socket
import threading
import time
from time import sleep
from datetime import datetime
import hashlib

#---------------METHODS---------------#


messages_Sent = {}
messageID = 0

# creates list of messages sent to server.
# to be checked when returned for loss and too acknowledge

# find current time
# loop through messages_sent
# get the time that those messages were sent
# if current time = timeOfMessage_sent:
# resend message
def check_If_message_has_timed_out():
    # time.sleep(3)
    currentTime = int(datetime.now().strftime("%Y%m%d%H%M%S"))
    copyOfMessages_Sent = messages_Sent

    for key in copyOfMessages_Sent:
        message_Sent_Time = (copyOfMessages_Sent[key][0])
        # print(messages_Sent[key][1])
        timeOfSent = int(message_Sent_Time.strftime("%Y%m%d%H%M%S"))
        time_Elapsed = currentTime-timeOfSent
        # print(time_Elapsed)

        if time_Elapsed > 2:
            messageSendingAgain = (str)(copyOfMessages_Sent[key][1])
            socketSend.sendto(messageSendingAgain.encode(), (serverIP, 4040))

        # timeOfSent is now equal to the time that the message was sent (as an integer)



# Clears terminal
# makes terminal look 'clean' and neat
def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

#pings server to show it is still connected
def pingServer():
    global serverIP
    while True:
        sleep(1)
        messageToSend = "ONLINE"
        socketSendPings.sendto(messageToSend.encode(), (serverIP, 12121))

# Sends ping to server to ensure that there is a server hosted at the IP specified
def testConnection():

    global serverIP

    serverIP = input("Enter the IP of the server you wish to connect to:\n")

    try:
        messageToSend = "PING" + "#" + clientIP + "#" + ""
        socketSend.sendto(messageToSend.encode(), (serverIP, 4040))

    except:
        print("Connection failed\n")
        testConnection()

# Sends a request to the server to connect the client to the server
def connectToServer():
    User_Name = input("Enter your Name \n")
    try:
        messageToSend = "CONNECT_USER" + "#" + clientIP + "#" + User_Name
        socketSend.sendto(messageToSend.encode(), (serverIP, 4040))
        print(messageToSend)

    except:
        print("failed")

# A simple UI that allows for navigation of the programs functionality
def homeUI():

    global serverIP
    global clientIP

    clearConsole()

    print("IP of Client is: " + constantClientIP + "\n")

    print("\nCHATBOT\n")

    print("1. Create new conversation.")
    print("2. View all conversations.")
    print("3. Quit program.\n")

    userInput = input()
    # if statment to handle response

    if userInput == '1':
       # print("Calling createConversation()\n")
        print("\nList of available users to start a conversatoin with:\n")
        createConversation()

    elif userInput == '2':
      #  print("Calling viewConversations")
        print("Open Conversations:\n")
        viewConversations()

    elif userInput == '3':
        messageToSend = "OFFLINE"
        socketSendPings.sendto(messageToSend.encode(), (serverIP, 12121))
        print("Disconnecting User")
        os._exit(0)
    else:
        homeUI()

# Gets a list of conversations that the client is part of and prints them with unique IDs
def viewConversations():

    global serverIP
    global clientIP
    global conversationPartners

    messageToSend = "RETURN_CONVERSATIONS" + "#" + constantClientIP + "#" + ""
    socketSendRequests.sendto(messageToSend.encode(), (serverIP, 4040))

    chats, throw = socketReceiveInfastructure.recvfrom(1024)

    allChats = chats.decode()

    allTheChats = allChats.split("|")

    chatListID = []

    if len(allTheChats) == 0:
        print("There are no available conversations to enter.\n")
        temp = input("Press enter to continue.\n")
        homeUI()

    for i in range(0, len(allTheChats)-1):

        x = allTheChats[i]

        tempSplit = x.split("=")

        chatListID.append(tempSplit[0])

        print(tempSplit[0] + ": " + tempSplit[1])

    userInput = input(
        "\nType the number of the conversation you wish to enter.\nType 'BACK' to go back to the home menu.\n\n")

    # validate that userInput is a number from the convo IDs
    if (userInput) in chatListID:
        enterConversation(userInput)
    elif userInput == "BACK":
        homeUI()
    else:
        clearConsole()
        print("Conversation does not exist / access denied ._.\n")
        viewConversations()


#Send messages to clients on network
def enterConversation(convoID):

    clearConsole()
    print("You are now broadcasting messages to conversation (" +
          convoID + ").\nType DISCONNECT to exit the chat.\n")

    while True:

        userInput = ''
        userInput = input()

        if userInput == "DISCONNECT":

            homeUI()

        else:
            messageToSend = "FORWARD_MESSAGE" + "#" + convoID + \
                "#" + (str)(messageID) + "#" + userInput

            text = messageToSend
            messages_to_Validate(messageToSend)

            socketSendMessages.sendto(text.encode(), (serverIP, 4040))

# Recieves messages from server (runs in a thread)
def messageReciever():
    global clientIP
    while True:

        messagefromClient, clientIP = socketRecieveMessages.recvfrom(1024)
        Temp_Message = messagefromClient.decode()
        message = Temp_Message.split('-')
        messageID_TO_Compare = message[0]
        ipAddress_To_Compare = message[2]

        if (clientIP[0] == ipAddress_To_Compare):
            confirm_Message_Delivered(messageID_TO_Compare)
            check_If_message_has_timed_out()
        print(ipAddress_To_Compare + " "+message[3])


# Creates conversations wiith specified users who have joined the network
def createConversation():

    global serverIP
    global clientIP

    messageToSend = "RETURN_USERS" + "#" + clientIP[0] + "#" + ""
    socketSendRequests.sendto(messageToSend.encode(), (serverIP, 4040))

    users, throw = socketReceiveInfastructure.recvfrom(1024)
    usersX = users.decode()
    userList = usersX.split("#")
    finalUserList = userList[0].split(",")

    for i in (range(1, len(finalUserList)-1)):

        print(str(i) + ". " + finalUserList[i])

    print("\nType the IP Address of the user you wish to create a conversation with.")
    print("To start a chat with multiple users, seperate IP Addresses with a ','.\n")

    makeChat = input()
    print()

    messageToSend = "CREATE_CONVERSATION" + "#"
    messageToSend = messageToSend + constantClientIP

    makeChatList = makeChat.split(",")
    j = 0
    for x in makeChatList:
        # validates that IPs entered are valid
        if makeChatList[j] in finalUserList:
            messageToSend = messageToSend + "," + makeChatList[j]
            j += 1
        else:
            print(
                makeChatList[j] + " is not a valid IP address and has not been added to the group chat.\n")
            j += 1

    socketSend.sendto(messageToSend.encode(), (serverIP, 4040))

    print("Conversation created, press enter to continue.")
    throwAwayVar = input()
    homeUI()


# Function used to create a list of sent messages to be verified later that they were received correctly
def messages_to_Validate(message):
    global messageID
    time_of_Sending = datetime.now()
    messages_Sent[messageID] = (time_of_Sending, message)
    messageID += 1

# Function used to confirm message sent was recieved back correctly
def confirm_Message_Delivered(Message_ID):
    del (messages_Sent[(int)(Message_ID)])


#------------------MAIN-------------------#
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 16000))
print("UDP Socket Created")
clientIP = s.getsockname()[0]
constantClientIP = clientIP
print("IP of Client is: " + clientIP + "\n")
s.close

# Socket for receiving messages from the server
socketRecieveMessages = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketRecieveMessages.bind((clientIP, 10000))
# Socket for sending messages to other users
socketSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Socket for receiving other METHODS
socketReceiveInfastructure = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketReceiveInfastructure.bind((clientIP, 50000))
# Socket for sending requests to the server
socketSendRequests = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)




conversationPartners = ''

serverIP = ''

testConnection()
connectToServer()

# Port for sending pings to the server constantly
socketSendPings = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

pinging = threading.Thread(target=pingServer)
pinging.start()

socketSendMessages = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Receive messages thread
messageReceivingThread = threading.Thread(target=messageReciever)
messageReceivingThread.start()
homeUI()
