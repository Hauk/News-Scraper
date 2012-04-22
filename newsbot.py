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
from mechanize import Browser

import socket
import string
import random

#Set the dcu proxy for downloading the XML file.
dcuproxy = {'http': 'http://proxy.dcu.ie:8080'}

#Store various links to different news subsections.
sub_categ = ["http://www.irishtimes.com/feeds/rss/newspaper/index.rss","http://www.irishtimes.com/feeds/rss/newspaper/ireland.rss","http://www.rte.ie/rss/news.xml"]

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

#function to convert rawlinks to TinyURLs
def getTinyURLs(rawlinks):
	tinyurls = []

	#loop links, create TinyURL and append to tinyurls list
        for item in rawlinks:
		tinyurlhttp = "http://tinyurl.com/api-create.php?url="				
		turesult = urllib.urlopen(tinyurlhttp + item, proxies=dcuproxy).read()
		tinyurls.append(turesult)

	return tinyurls

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

            if(line[3]==':!headlines'):

                #Create function to pull down correct subcategory.
                #line[4] = sport | tech | etc, call function(return link).

                #Get our raw data from from the IT RSS XML.
                rawdata = urllib.urlopen(sub_categ[2], proxies=dcuproxy)
                newsoutput = BeautifulStoneSoup(rawdata.read(), fromEncoding='utf-8')

                headlines = []
                links= []

                for headline in newsoutput.findAll('title'):
	            headlines.append(headline.string)

                for link in newsoutput.findAll('link'):
	            links.append(str(link.string))

                headlines = headlines[3:]
                links = links[3:] 

                #make tinyurls
                links = getTinyURLs(links)

                for index, headline in enumerate(headlines):
                        try:
                            s.send('PRIVMSG '+line[2]+' :' +'IRISHTIMES.COM: ' + links[index] + ' ' +headline+ '\r\n')

                            time.sleep(0.5)
                        except UnicodeEncodeError:
                            print 'Error in coding/encoding Unicode from link/description'
                            pass

        except IndexError:
            print 'Index Error in array.'
            pass
