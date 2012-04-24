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

import sites

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

def getSiteSection(website, section):
    #Loop through sites comparing site.
    #if website = this website -  search this dictionary.
        #check dict value against section.
        #if section = oursection.
           # return value from dict.
    return true

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

                #Pull target URL from IRC input.
                targetURL = sites.Site(line[4], line[5])
                    
                #If a URL is found from site and section, parse link for data.
                if(targetURL.retTargetSite() != None):

                    #Get our raw data from from the targetURL XML
                    rawdata = urllib.urlopen(targetURL.retTargetSite(), proxies=dcuproxy)
                    newsoutput = BeautifulStoneSoup(rawdata.read(), fromEncoding='utf-8')

                    headlines = []
                    links = []

                    #Pull down titles and links.
                    for headline in newsoutput.findAll('title'):
        	            headlines.append(headline.string)

                    for link in newsoutput.findAll('link'):
    	                links.append(str(link.string))
    
                    #Split rubbish off.
                    headlines = headlines[3:]
                    links = links[3:] 

                    #make tinyurls
                    links = getTinyURLs(links)

                    for index, headline in enumerate(headlines):
                        try:
                            s.send('PRIVMSG '+line[2]+' :' +'IRISHTIMES.COM: ' + links[index] + ' ' +headline+ '\r\n')
                            time.sleep(0.5)

                        except UnicodeEncodeError:
                            pass

                #If no site found, send error message to channel.
                elif(targetURL.retTargetSite() == None):
                    s.send('PRIVMSG '+line[2]+' :' +'No site or section found. Try another site.\r\n')
                    pass

        except IndexError:
            print 'Index Error in array.'
            pass
