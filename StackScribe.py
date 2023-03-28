import feedparser
import pdfkit
from bs4 import BeautifulSoup
from datetime import datetime
import pickle
import time

#point pdfkit to the correct location of wkhtmltopdf.exe on Windows
pdfkitconfig = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

#introduce the application
print("Welcome to StackScribe!")
   
#introduce the substacksite class with arguments sitename and lastupdated
class substacksite:
    def __init__(self, sitename, siteurl, lastupdated):
        self.sitename = sitename
        self.siteurl = siteurl
        self.lastupdated = lastupdated

#build the list of sites being monitored
substacksites = []
with open("sites.bin", "rb") as f:
    substacksites = pickle.load(f)

#Check if currently monitoring any sites, if so, list them
if substacksites:
    print("\nPresently monitoring:")
    for obj in substacksites:
        print("\n" + obj.sitename + " - last updated: " + str(obj.lastupdated))
else:
    print("\nNot currently monitoring any sites...")

#provide initial menu, take options, respond
while (True):
    print("\nTo add a site, enter [1] \nto list and edit existing sites, enter [2] \nto begin scanning, enter [3] \nIf no sites are entered and you choose to scan, the console will close.\n")
    choicetoentersite = input()

    #provide submenu for adding sites to the list of monitored sites
    if choicetoentersite == "1":
        while (True):
            print("\nEnter Site Name:\n")
            newsitename = input()
            print("\nNow enter Site's RSS feed Url (this is the url, with /feed appended):\n")
            newsiteurl = input()
            print("\nSite name: " + newsitename + ", Site URL: " + newsiteurl)
            print("\nApply? [y] for Yes, [n] for No\n")
            choicetoapply = input()
            if choicetoapply == "y":
                substacksites.append(substacksite(newsitename, newsiteurl, datetime.min))
                print("\n" + newsitename + " added to monitored sites!")
                with open("sites.bin", "wb") as f:
                    pickle.dump(substacksites, f)
            elif choicetoapply == "n":
                print("\nSite not added.")
            else:
                print("Choice not recognised")
            print("\nTo add another site, enter [1], otherwise to return to the main menu, enter [return]\n")
            choicetoaddanothersite = input()
            if choicetoaddanothersite == "1":
                print("\nPreparing to add another site... \n")
            elif choicetoaddanothersite == "return":
                break
            else:
                print("\nChoice not recognised, returning to main menu...")
                break

    #provide submenu for listing and deleting monitored sites
    elif choicetoentersite == "2":
        while (True):
            if substacksites:
                print("\nListing sites...\n")
                for obj in substacksites:
                    print("\n" + "[" + str(substacksites.index(obj)) + "]" + obj.sitename)
                print("\nTo remove a site, enter the index of the site, displayed to the left.")
                print("\nTo return to the main menu, enter [return]\n")
                choicetodelete = input()
                if choicetodelete == "return":
                    break
                else:
                    try:
                        substacksites.pop(int(choicetodelete))
                        print("Item deleted!")
                        with open("sites.bin", "wb") as f:
                            pickle.dump(substacksites, f)
                    except:
                        print("\nChoice not recognised, or index number doesn't correspond to item.")
            elif not substacksites:
                print("\nNo sites stored, returning to Main Menu...")
                break

    #initiate scanning if site list is populated, otherwise abort program
    elif choicetoentersite == "3":
        if substacksites:
            break
        elif not substacksites:
            quit()

#iterate through list of sites, identify if a new post has been made
while (True):
    print("\nScanning list for new articles...")
    for obj in substacksites:

        print("\nChecking site " + str(substacksites.index(obj)+1) + " of " + str(len(substacksites)) + " being: " + obj.sitename)
        #parse site through feedparser
        pagefeed = feedparser.parse(obj.siteurl)

        #get the raw date the last entry was posted
        lastpostdatetimeraw = pagefeed['entries'][1]['published'][5:]

        #convert the raw date to a python datetime object so it can be compared
        lastpostdatetime = datetime.strptime(lastpostdatetimeraw, '%d %b %Y %H:%M:%S %Z')
    
        #figure out if the latest article is new, if so, print it and update the lastpostdatetime for the respective site
        if lastpostdatetime > obj.lastupdated:
            print("\nNew article detected from " + obj.sitename + "!")
            urltodownload = pagefeed['entries'][0]['link']
            pdfkit.from_url(urltodownload, 'out.pdf', configuration=pdfkitconfig)
            print("\nArticle printed to PDF!")
            obj.lastupdated = lastpostdatetime
            with open("sites.bin", "wb") as f:
                pickle.dump(substacksites, f)
        else:
            print("\nNo new article detected from " + obj.sitename + "...")
    print("\nAwaiting 60(s) before scanning again...")
    time.sleep(60)





