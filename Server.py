import os
import socket
import threading
import time
#import cryptography
from time import sleep
from collections import OrderedDict


#---------------GLOBAL VARIABLES---------------#

userList = { "DUMMY" : "NEITHER"}
clientIP = '', ''
splitMessage = '' , ''
chatList = {0:"192.168.1.101"}
userNames={"IP":"Name"}
#----------------------------------------------#





#---------------METHODS---------------#


# Handles all messages received from clients
    # Calls various other messages based on the tag of the message 
def receiveMessages():
    
    global userList
    global clientIP
    global splitMessage
    
    while True:
        
        messagefromClient, clientIP = serverSocket.recvfrom(1024)
        message = messagefromClient.decode()
        splitMessage = message.split("#")
                
        if splitMessage[0] == "PING":
            print("Received ping from client at IP " + clientIP[0] + "\n")
            
        elif splitMessage[0] == "CONNECT_USER":
            connectUser()
            Create_User_Name(splitMessage[2])
           
        elif splitMessage[0] == "FORWARD_MESSAGE":
          #  print("in hre")
            forwardMessage()
            
        elif splitMessage[0] == "RETURN_USERS":
            returnUsers()
            
        elif splitMessage[0] == "CREATE_CONVERSATION":
            createConversation()
            
        elif splitMessage[0] == "RETURN_CONVERSATIONS":
            returnConversations()
    

# Sends back a list of conversations that the client who sent the request is in
def returnConversations():
    
    global userList
    global clientIP
    global splitMessage    
    
    listToSendBack = ""
    
    for x in chatList:
        
        chatClients = chatList[x].split(",")
        print(chatClients)
        
        if clientIP[0] in chatClients:
            #Add dict key + value to listToSendBack + "|" 
            listToSendBack = listToSendBack + str(x) + "=" + chatList[x] + "|"
            
    print(listToSendBack)     
    socketSendFromServer.sendto(listToSendBack.encode(), (clientIP[0],50000))


# Creates a new conversation between the source client and the other specified participants (may include the source client itself in list)
def createConversation():
    
    global userList
    global clientIP
    global splitMessage
    
    usersToStartChatWith = splitMessage[1]
    print(usersToStartChatWith)
        
    # find last key in dict
    # add 1 to it, then create new conversation with that as the ID
    try:
        lastKey = list(chatList)[-1]
        lastKey +=1
        chatList[lastKey] = usersToStartChatWith
      #  print(chatList)
    except:
        
        lastKey = 0
        chatList[lastKey] = usersToStartChatWith
        #print(chatList)
        
       
        
def returnUsers():
    
    global userList
    global clientIP 
    global splitMessage
    
    # create string of users sperated by commas
    messageToSend = ''
    for x in userList:
        messageToSend = messageToSend + x + ","
        
    socketSendFromServer.sendto(messageToSend.encode(), (clientIP[0],50000))
   # print("Well we got this far")
    

# Sends back a list of users connected to the server   
def connectUser():

    global userList
    global clientIP
    
    listOfKeys = userList.keys()
    
    if clientIP[0] not in listOfKeys:
        userList[clientIP[0]] = "ONLINE" # Add user to userList and set status to ONLINE
        print("User at IP " + clientIP[0] + " has connected for the first time.\n")
    else:
        userList.update({clientIP[0]: "ONLINE"}) # Set status OF user to ONLINE    
        print("User at IP " + clientIP[0] + " has come online.\n")
        
# Send messages received by the server onto their desination clients               
def forwardMessage():
    
    global userList
    global clientIP
    global splitMessage
    
    messageToSend = splitMessage[2]+"-"+"Message from -" + clientIP[0] + "- in chat ID: " + splitMessage[1] + ": '" + splitMessage[3] + "'"
    
    xx = chatList
    print(xx)
    
    
    forwardingList = chatList[int(splitMessage[1])]
    print(forwardingList)
    
    splitForwardingList = forwardingList.split(',')
    
    for x in splitForwardingList:  
        print(x)
        socketForwardMessage.sendto(messageToSend.encode(),(x,10000))
    

def pingClients():
    
    socketPing = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    global userList
    
    while True: 
        
        for x in userList.copy():
            if userList[x] == "ONLINE":
                  
                    pingFromClient, clientIP = socketRecievePing.recvfrom(1024)
                    message = pingFromClient.decode()
                    
                    #if message == "ONLINE":
                    #   print("The user at " + clientIP[0] + " is still online")
                   
                    if message == "OFFLINE":
                        userList[x] = "OFFLINE"
                        print("User " + x + " has gone offline.\n")                    
                    
                    
def Create_User_Name(User_Name):
    listOfKeys = userNames.keys()
    if clientIP[0] not in listOfKeys:
         userNames[clientIP[0]] = User_Name
    else:
        {}
        #userNames[clientIP[0]].update(User_Name)

def get_UserName(IP_Address):
    for ip in userNames.keys(): 
        if(ip==IP_Address):
            name=userNames[ip] 
            return name
            
#----------------------------------------#          



#-------------------MAIN-----------------#          

# serverSocket is a socket for recieving messages on
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Created a UDP socket\n")
 
port = 4040 # port for receiving messages at the server
 
# create socket to find private IP of HostServer
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 17000))
serverIP = s.getsockname()[0]
s.close 
serverSocket.bind((serverIP, port))
print("Server has been hosted at IP: " + serverIP + " - Port: 4040\n")        

# Socket to handle general receiving of messages        
recieving = threading.Thread(target=receiveMessages)
recieving.start()

# Socket to handle sending of messages directly from the server
socketSendFromServer =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Socket to handle forwarding of messages from clients
socketForwardMessage =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Socket to handle receiving of pings
socketRecievePing = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketRecievePing.bind((serverIP, 12121))
pinging = threading.Thread(target=pingClients)
pinging.start()




