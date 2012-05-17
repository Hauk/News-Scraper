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

        try:
            if(line[3]==':!news' and line[4] is not None and line[5]!='categories'):
                    
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
                            time.sleep(2)

                except mdb.Error:
                    name = line[0]
                    user = getName(name)
                    s.send('PRIVMSG '+line[2]+' :'+user+':' + ' No feeds found for: ' + line[4] + '. Try another site or request it be added.'+ '\r\n')

                except IndexError:
                    name = line[0]
                    user = getName(name)
                    s.send('PRIVMSG '+line[2]+' :'+user+':' + ' Usage is !headlines site category.'+ '\r\n')

        except IndexError:
            pass

        #This piece of code allows users to return a list of categories based on
        #a site they submit.
        try:
            if(line[3]==':!news' and line[4] is not None and line[5]=='categories'):
                
                sitecategs = """SELECT category FROM newsbot_feeds WHERE site=%s;"""
                sitesquery = """SELECT site from newsbot_feeds;"""

                categories = []
                sites = []

                cursor.execute(sitecategs, line[4])

                categs = cursor.fetchall()

                cursor.execute(sitesquery)

                getsites = cursor.fetchall()

                for row in getsites:
                    sites.append(row["site"])

                #Get all categories
                for row in categs:
                    categories.append(row["category"])
                
                if line[4] in sites:

                    appendcat = ', '.join(categories)

                    name = line[0]
                    user = getName(name)

                    s.send('PRIVMSG ' + line[2]+' :' +user+': ' + 'Categories for ' +line[4]+ ' are: ' + appendcat + '\r\n')

                else:
                    name = line[0]
                    user = getName(name)
                    s.send('PRIVMSG ' + line[2]+' :' +user+': ' + 'No categories found for site: ' +line[4]+ '.' + '\r\n')

        except (mdb.Error, IndexError):
            pass

        #Basic one word search functionality.
        #Could do with a re-think for code efficiency.
        try:
            if(line[3]==':!newssearch' and line[4] is not None):
            
                sites = []
                links = []
                headlines = []

                tablesquery = """SHOW TABLES;"""

                cursor.execute(tablesquery)
                
                tables = cursor.fetchall()                           

                #Empty list to store sites.
                valsites = []

                #Get all sites from query results.
                for row in tables:
                    valsites.append(row["Tables_in_newsbot"])

                #Loop through all sites and find search key.
                for tabs in valsites:

                    if tabs != 'newsbot_feeds':

                        #Create query to pull headlines from database
                        searchresults = """SELECT site, links, headlines FROM """ + tabs  + """;"""
                        cursor.execute(searchresults)

                        searchdata = cursor.fetchall()

                        #Pull headlind and split() for searching.
                        for row in searchdata:
                            headlinetokens = row["headlines"]
                            headlinetokens = headlinetokens.split()

                            #If search token in headline, append news item.
                            if line[4] in headlinetokens:
                                sites.append(row["site"])
                                links.append(row["links"])
                                headlines.append(row["headlines"])

                #Send all results to the channel.
                for index, headline in enumerate(headlines):
                    s.send('PRIVMSG '+line[2]+' :' + sites[index] + ': ' + links[index] + ' ' +headline + ' \r\n')
                    time.sleep(2)
            
            elif(line[3]==':!newssearch' and line[4] is None):
                print "aww"
                name = line[0]
                user = getName(name)
                s.send('PRIVMSG '+line[2]+' :'+user+':' + ' Usage is !newssaerch mysearchitem ' + '\r\n')
            
            else:
               print "error" + line[4]
        except:
            pass
