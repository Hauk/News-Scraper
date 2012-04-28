#! /usr/local/bin/python

SCRIPT_NAME = "DB_Updater"
SCRIPT_AUTHOR = "Eoghan Lappin <hauk@redbrick.dcu.ie>"
SCRIPT_VERSION = "0.1-DEV"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Script to run an hourly update of headlines/links in newsbot database on Titan."

from BeautifulSoup import BeautifulStoneSoup
import re
import sys
import urllib
import urllib2
from mechanize import Browser

#Database imports
import MySQLdb as mdb
import dbconfig

#function to convert rawlinks to TinyURLs
def getTinyURLs(rawlinks):
    tinyurls = []

    #loop links, create TinyURL and append to tinyurls list
    for item in rawlinks:
            tinyurlhttp = "http://tinyurl.com/api-create.php?url="
            turesult = urllib.urlopen(tinyurlhttp + item, proxies=dcuproxy).read()
            tinyurls.append(turesult)

    return tinyurls

#function checks if site exists as a table in the DB.
def checkTableInDB(sites, tabledict):
    
    for index, item in enumerate(tabledict):        
        if sites[index] not in tabledict:
            return False

    return True

#Set the DCU proxy for downloading the RSS feeds.
dcuproxy = {'http': 'http://proxy.dcu.ie:8080'}

#Connect to the MySQL database on Titan.
titanconn = mdb.connect('136.206.16.140', dbconfig.user, dbconfig.dbpass, 'newsbot')
cursor = titanconn.cursor(mdb.cursors.DictCursor)

#Setup headlines and links lists for storing extracted data.
sites = []
categories = []
rsslinks = []

#This query pulls all the data from the news_links db and adds them to the
#lists below.
feedquery = """SELECT * FROM newsbot_feeds WHERE category='technology';"""

#Execute the query.
cursor.execute(feedquery)
feedlinksdata = cursor.fetchall()

#Extract the row data and append it to our lists.
for row in feedlinksdata:

    site = row["site"]
    category = row["category"]
    link = row["feed_link"]

    sites.append(site)
    categories.append(category)
    rsslinks.append(link)

#Parse <link> and <title> from XML feed.
for index, rssindex in enumerate(rsslinks):
    
    headlines = []
    xmllinks = []

    #Get our raw data from from the targetURL XML.                     
    rawdata = urllib.urlopen(rssindex, proxies=dcuproxy)
    newsoutput = BeautifulStoneSoup(rawdata.read(), fromEncoding='utf-8')

    #Pull down titles and links.
    for headline in newsoutput.findAll('title'):
        headlines.append(headline.string)

    for link in newsoutput.findAll('link'):
        xmllinks.append(link.string)

    #Split rubbish off.
    headlines = headlines[3:]
    
    xmllinks = xmllinks[3:]

    #make tinyurls
    xmllinks = getTinyURLs(xmllinks)
        
    for test, testIndex in enumerate(xmllinks):
        print sites[index] + " " + categories[index] + " " + testIndex + " " + headlines[test]

    #query checks if a table exists for that site in the database. If not,
    #create a table and insert values into that table.
    siteintable = """SHOW TABLES;"""
    cursor.execute(siteintable)

    tablelist = cursor.fetchall()

    tnames = []

    for row in tablelist:
        tnames.append(row["Tables_in_newsbot"])

    #Check if the site table exists or not.
    if not checkTableInDB(sites, tnames):
        print "table does not exist"

        #Create the table for the site.


