#! /usr/local/bin/python
#-*- coding: iso-8859-15 -*-

SCRIPT_NAME = "News_Bot"
SCRIPT_AUTHOR = "Eoghan Lappin <hauk@redbrick.dcu.ie>"
SCRIPT_VERSION = "0.1-DEV"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Pull down news links and descriptions from various news sites"

#Import libraries
from BeautifulSoup import BeautifulStoneSoup
import time
import re
import sys
import urllib
import urllib2
import MySQLdb as mdb
from mechanize import Browser

import socket
import string
import random

import dbconfig

#Set the dcu proxy for downloading the XML file.
dcuproxy = {'http': 'http://proxy.dcu.ie:8080'}

#NewsBot Networking setup (Thanks to maK for the code)
net = 'irc.redbrick.dcu.ie'
port = 6667
nick = 'NewsBot'
channel = '#bots1'
owner = 'hauk'
ident = 'hauK'
readbuffer = ''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((net,port))
s.send('USER '+ident+' '+net+' bla :'+owner+'\r\n')
s.send('NICK '+nick+'\r\n')
s.send('JOIN '+channel+'\r\n')
s.send('PRIVMSG hauK : Good evening sir! Loading all modules...\r\n')
print s.recv(4096)

#strip starting : and following !redbrick.dcu.ie
def getName(x):
        nix = string.split(x,"!")
        x = nix[0]
        y = x[1:]
        return y

#Connect to the MySQL database on Titan.
titanconn = mdb.connect('136.206.16.140', dbconfig.user, dbconfig.dbpass, 'newsbot')
cursor = titanconn.cursor(mdb.cursors.DictCursor)

#main loop
while True:

        #multiple words according to maK
        sentence = ' '
        readbuffer = readbuffer+s.recv(2048)
        temp = string.split(readbuffer, "\n")
        readbuffer=temp.pop()

        for line in temp:

               line=string.rstrip(line)
               line=string.split(line)

        if(line[0]=='PING'):
            s.send('PONG ' +line[1]+'\r\n')

        if(line[1]=='PRIVMSG'):
                #necessary to get full sentence
                for n in range(4, len(line)):
                        sentence += line[n]+' '

        if(line[3]==':!headlines'):
                
            try:
                #Pull down headlines and links from database
                newsquery = """SELECT * FROM  """ + line[4] + """ WHERE """ + line[4] + """.category=%s;"""
                cursor.execute(newsquery, line[5])
                newslinks = cursor.fetchall()
    
                #Select all sites for error checking.
                sitesquery = """SELECT site FROM newsbot_feeds;"""
                site = cursor.execute(sitesquery)
                validsites = cursor.fetchall()
                valsites = []

                for row in validsites:
                    valsites.append(row["site"])
        
                if line[4] in valsites: 
   
                    for link in newslinks:
                        site = link["site"]
                        linky = link["links"]
                        headline = link["headlines"]
    
                        s.send('PRIVMSG '+line[2]+' :' + site + ': ' + linky + ' ' + headline + ' \r\n')
                        time.sleep(1.4)

            except (IndexError, mdb.Error):
                name = line[0]
                user = getName(name)
                s.send('PRIVMSG '+line[2]+' :'+user+':' + ' No feeds found for: ' + line[4] + '. Try another site or request it be added.'+ '\r\n')
