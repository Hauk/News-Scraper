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
def checkTableInDB(site, tabledict):
    if site not in tabledict:
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
feedquery = """SELECT * FROM newsbot_feeds;"""

#Execute the query.
cursor.execute(feedquery)
feedlinksdata = cursor.fetchall()

#Drop all tables except the feeds table.
gettables = """SHOW TABLES;"""
cursor.execute(gettables)

tables = cursor.fetchall()

for table in tables:

    if table["Tables_in_newsbot"] != 'newsbot_feeds':
        deletetable = """DROP TABLE """ + table["Tables_in_newsbot"] + """;"""
        cursor.execute(deletetable)
        print "Dropping table: " + table["Tables_in_newsbot"] + "..."


#Extract the feeds data from the database and append it to our lists.
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

    #query checks if a table exists for that site in the database. If not,
    #create a table and insert values into that table.
    for site in sites:

            addsitequery = """CREATE TABLE IF NOT EXISTS """ + site + """ ( site VARCHAR(200), category
            VARCHAR(100), links VARCHAR(200), headlines VARCHAR(200));"""

            cursor.execute(addsitequery)

#Insert the data retrieved into the relevant table.
    for linky, headline in enumerate(headlines):
        try:
            insertquery = """INSERT INTO """ + sites[index] + """ VALUES (%s, %s, %s, %s);"""

            cursor.execute(insertquery, (sites[index], categories[index],
            xmllinks[linky], headline))

        except UnicodeEncodeError:
            print "Error in unicode parsing."
            pass
