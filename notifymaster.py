#! /usr/bin/env python3

import os
import re
import ssl
import sys
#import bs4 # apt-get install python3-bs4
import time
import json
import socket
import string
import threading
import subprocess

# Setup the IRC connection
irc = socket.socket()
irc = ssl.wrap_socket(irc)

# List of currently active threads
threadlist = []

# Edit these values for your server
ircServer = "irc.blackcatz.org"
ircSSLPort = 6697
ircNick = "[Z]NotifyMaster"
ircPass = "bob"
# What the bot uses as a command character
ircCKey = ircNick
# List of channels to connect to
channelList = ['#howtohack']
owner = "eve"
# Radio link
radioLink = "https://radio.zempirians.com"
# Bot help command
botList = ['+[Z]NotifyMaster','Contains basic help command and notifies bot owners when their bot is down','help'
,'+[Z]Citadel','Searches for the databases in which your string is found','!email string'
,'+[Z]Googler','Searches google with the given string, gives you the top result','[Z]Googler: help'
,'+[Z]MEGABOT','Contains multiple helpful commands that didn\'t require their own bot','[Z]MEGABOT: help'
,'+[Z]RadioBot','Manages the radio on '+radioLink+'!','[Z]RadioBot: help'
,'+[Z]RssFeeder','Automatically posts new articles from websites we are subscribed to','[RssFeeder]: help'
,'+[Z]Titler','Automatically pulls the title of links posted in the chat','[Z]Titler: help'
,'&Zempire','Administrative bot for the operators','[Z]Zempire: help'
]
rules = ['[Z] represents a bot, +[Z] represents an official bot and & represents an administrative bot.'
,'The command \"[Z]BotName: help\" allows you to get the commands of a bot.'
,'Don\'t make mom jokes. Only Bulwark\'s mom can get those.'
,'No doxing. No DDoS. No Drama. No Swatting.'
,'Have fun and learn.'
]
helpList = ['help','Displays the help command of bot and the other general bot commands.'
,'radio','Returns the radio link.'
,'die','Kills the bot, if your the owner.'
]

def rawSend(data):
		print(str(data+"\r\n").encode())
		irc.send(str(data+"\r\n").encode())

def ircConnect():
		irc.connect((ircServer, ircSSLPort))

def ircMessage(msg, channel):
		rawSend("PRIVMSG " + channel + " :" + msg + "\r\n")

def ircRegister():
		rawSend("USER " + ircNick + " 0 * " + ":" + ircNick + "\r\n")

def ircSendNick():
		rawSend("NICK " + ircNick + "\r\n")

def ircJoin(channel):
		rawSend("JOIN " + channel + "\r\n")

def ircPassword():
		rawSend("PASS " + ircPass + "\r\n")

def ircDisconnect(msg):
		rawSend("QUIT " + msg + "\r\n")

def msgFind(msg, data):
		return bytes(msg,"utf-8") in data

def msgAnalyze(msg, data):
		return (msgFind(msg, data) and msgFind(ircNick,data))

def Initialize():
		time.sleep(5)
		ircConnect()
		ircRegister()
		ircSendNick()

def channelRequests(channel, data):
		user = str(data).split('!')[0].split(':')[1]
		if msgAnalyze("help", data):
			#if bytes("help","utf-8") not in data.split()[len(data.split())-1]:
				#user = re.match(r"\w+",str(str(data).split()[len(data.split())-1])).group()
			ircMessage(user+": look at your private messages!", channel)
			ircMessage("General rules:", user)
			for z in range(len(rules)):
				ircMessage("Rule "+str(int(z)+1)+": "+rules[z], user)
			ircMessage("General bots:", user)
			for z in range(0,len(botList)-1,3):
				ircMessage("Bot: "+str(botList[z])+", description: "+str(botList[z+1])+", main command: "+str(botList[z+2]), user)
			ircMessage(ircNick+"'s commands:", user)
			for z in range(0,len(helpList),2):
				ircMessage("Command: "+helpList[z]+", Function: "+helpList[z+1], user)
		elif msgAnalyze("radio", data):
			ircMessage("Tune in here: "+radioLink+"!", user)
		#elif user == owner:
			#finalArgument = re.match(r"\w+",str(str(data).split()[len(data.split())-1])).group()
			#if finalArgument == "die":
				#ircDisconnect("Good night!")
				#irc.close()
				#sys.exit()
			#elif finalArgument == "rainbow":
				#for z in range(9):
					#for i in range(9):
						#ircMessage(chr(3)+str(z)+","+str(i)+"RAINBOW", channel)
		# Per RFC 1149.5
		#if msgFind(ircCKey + "random", data):
				#ircMessage("4", channel)

Initialize()
print("Connected.")
while True:
		data = irc.recv(512)
		if len(str(data)) is not 3:
			try:
				print(data.decode('utf-8'))
			except UnicodeDecodeError:
				print("Unicode error on: "+str(data))
		else:
			irc.close()
			irc = socket.socket()
			irc = ssl.wrap_socket(irc)
			Initialize()
		if str(data)[2:8] == "PING :":
				rawSend("PONG {0}".format(data.decode('utf-8').split()[1]))
				continue
		if msgFind("MODE "+ircNick, data) and msgFind("PRIVMSG", data) is False and msgFind("SSL", data):
				#Nick confirmed
				time.sleep(1)
				ircMessage("IDENTIFY "+ircPass, "NickServ")
				for channel in channelList:
					ircJoin(channel)
				continue
		for channel in channelList: # If you put 2 channels it dies...
			try:
				if data.decode('utf-8') and msgFind("PRIVMSG " + channel, data) and str(data).split('!')[0].split(':')[1] == "git" and msgFind("JUST KIDDING LOL", data):
					ircMessage("Death to all humans!", channel)
					#:git!zBot@blackcatz-4df.558.0j4iql.IP PRIVMSG #howtohack :JUST KIDDING LOL
				if msgFind("PRIVMSG " + channel, data) or msgFind("PRIVMSG " + ircNick, data): #Should be fixed!
					if msgFind("PRIVMSG" + ircNick, data):
						t = threading.Thread(target=channelRequests, args=(ircNick, data))
					else:
						t = threading.Thread(target=channelRequests, args=(channel, data))
					t.daemon = True
					t.start()
					continue #Break?
			except UnicodeDecodeError:
				print("Unicode error on: "+str(data))
