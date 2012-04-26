NewsBot v0.1

NewsBot is an IRC bot program, written in Python, that runs as a user on
RedBrick's(www.redbrick.dcu.ie) IRC server.

The purpose of this bot is provide an all in one news source where users can get
a list of current headlines and links to the latest news stories from various
news sources.

Users can trigger the program to print news headlines based on site(e.g. www.irishtimes.com), and section(e.g. Sport, Business, etc.).

An example of this trigger in the channel would be:

!headlines irishtimes sport

Where:  !headlines is the trigger for the program.
        irishtimes is the site to query.
        sport is the section on the site to pull the headlines from.

Files:

dbupdater.py -  DB updater does exactly what it says on the tin. It pulls all rss
feed sources from the database, downloads all headlines and links, and inserts
them into the databaseIt runs on the hour as a task in cron. The purpose of this
is to keep the data in the database as up-to-date as possible and to provide
faster IRC response times(TinyURL links already exist, so no need to generate on
the fly).

newsbot.py -    The main NewsBot program. newsbot.py uses pythons socket(thanks to
        maK@RedBrick for the code) to connect to the IRC server and monitor the
channel for the !headlines trigger. It then queries the database and prints the
data returned to the channel.

dbconfig.py -   This is imported in the newsbot.py program. This file contains
username/password information for the database to prevent the details being sent
to GitHub.
