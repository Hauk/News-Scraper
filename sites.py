class Site:

    #init parameters: self, users site + section from IRC.
    def __init__(self, siteInput, sectionInput):
        self.siteInput = siteInput
        self.sectionInput = sectionInput
        self.retTargetSite()

    #Function to return target RSS/XML file for parsing.
    def retTargetSite(self):

        #Define a list of current available feeds.
        sites = ['irishtimes', 'rte', 'bbc']

        #Dictionaries for site sections.
        irishtimes = { 'main' :'http://www.irishtimes.com/feeds/rss/newspaper/index.rss', 'ireland' : 'http://www.irishtimes.com/feeds/rss/breaking/irish.rss', 'world' : 'http://www.irishtimes.com/feeds/rss/breaking/world.rss', 'business' : 'http://www.irishtimes.com/feeds/rss/breaking/business.rss', 'sport' : 'http://www.irishtimes.com/feeds/rss/breaking/sports.rss', 'technology' :'http://www.irishtimes.com/feeds/rss/breaking/technology.rss'}

        rte = { 'main' : 'http://www.rte.ie/rss/news.xml', 'sports' :
                'http://www.rte.ie/rss/sport.xml', 'business' :
                'http://www.rte.ie/rss/business.xml', 'entertainment' :
                'http://www.rte.ie/rss/entertainment.xml' }

        bbc = {'headlines' : 'http://feeds.bbci.co.uk/news/rss.xml', 'world' : 'http://feeds.bbci.co.uk/news/world/rss.xml', 'uk' : 'http://feeds.bbci.co.uk/news/uk/rss.xml', 'business' :  'http://feeds.bbci.co.uk/news/business/rss.xml', 'politics' : 'http://feeds.bbci.co.uk/news/politics/rss.xml', 'health' : 'http://feeds.bbci.co.uk/news/health/rss.xml', 'education' : 'http://feeds.bbci.co.uk/news/education/rss.xml', 'science' : 'http://feeds.bbci.co.uk/news/science_and_environment/rss.xml', 'technology' : 'http://feeds.bbci.co.uk/news/technology/rss.xml', 'arts' : 'http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml'}

        #If the site is in the sites list, search the dictionaries for the
        #users section from IRC and return the corresponding XML/RSS link.
        if(self.siteInput in sites):

            if(self.siteInput == 'irishtimes'):

                for section in irishtimes.iterkeys():
                    if(self.sectionInput == section):
                        return irishtimes[section]

            elif(self.siteInput == 'rte'):                
                
                for section in rte.iterkeys():
                    if(self.sectionInput==section):
                        return rte[section]

            elif(self.siteInput == 'bbc'):                
                
                for section in bbc.iterkeys():
                    if(self.sectionInput==section):
                        return bbc[section]



        #If not, return None.
        elif(self.siteInput not in sites):
            return None
