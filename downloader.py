from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
import urllib2
import re
import fnmatch
import sys
import time


def my_print(text):
    sys.stdout.write(str(text) + "\n")
    sys.stdout.flush()
#End my_print
	
	
def get_urls(queryStr, linksArray, matcherStr):
	#Vars
	pageNum = 0					#Start at first page
	my_print("\nNew Query for urls")		#Display on newline
	while (True):			#Start loop
		#Url to get links from												#Page number												   Query value		
		urlSearch = "http://twain.lib.niu.edu/islandora/search/%20?page=" + str(pageNum) + "&type=dismax&f[0]=mods_resource_type_ms%3A%22" + queryStr + "%22"
		my_print("Searching : " + urlSearch)					#Print Searching...
		page = urllib2.urlopen(urlSearch)						#Get page instance
		soup = BeautifulSoup(page.read())						#Get html page
		results = soup.find('p', attrs={'class' : 'no-results'})#See if there are results
		if results is not None:		#End of query results
			break		#End loop
		#Find all a elements
		for a in soup.findAll('a', href=True):
			linksArray.append(a['href'])		#Get their href value
		pageNum += 1	#Increment page value and loop again
	linksArray = fnmatch.filter(linksArray, matcherStr)		#Only store matched urls
#End get_urls


def download_book(url, baseUrl, number, total, textOut, metaDict):
	urlSearch = baseUrl + url				#Get actual url
	my_print("Downloading Book " + str(number) + " of " + str(total) + " : " + urlSearch)	#Print Downloading...
	page = urllib2.urlopen(urlSearch)							#Get page instance
	content = page.read()
	#log.write("\n\nNew html\n")
	#log.write(content)
	soup = BeautifulSoup(content)					#Get html page
	#Get Text
	for div in soup.find_all('div', attrs={"id":"block-system-main"}):	#Get body of text
		#log.write(div.text.encode('utf-8'))
		textOut += div.text.encode('utf-8')
	#Get meta
	divTag = soup.find_all("div", attrs={"class": "niu-artfl"})
	for tag in divTag:
		tdTags = tag.find_all("meta")
		for tag in tdTags:
			metaDict[tag['name'].replace("DC.", "")] = tag['content']
#End download_book

#Main Code

#Variables text mixed material
testBook = "http://twain.lib.niu.edu/islandora/object/niu-twain%3A10949"
baseUrl = "http://twain.lib.niu.edu"	#Base url used along with book url	
urlMatch = "/islandora/object/*"		#Links matching this are texts
queries = ["text", "mixed%20material"]	#Queries to use in urls to download text
links = []								#Holds links to text webpages
bookText = ""							#String to hold book text
metaDict = {}							#Dictionary to hold meta data

log = open('log_downloader.txt', 'w')	#Open up a logfile
db = TinyDB('database/db.json')

db.insert({'type': 'apple', 'count': 7})
table = db.table('Books')

#Get links	
#for query in queries:					#Get every url from each query
#	get_urls(query, links, urlMatch)

#Download books
numBooks = len(links)

text = ""
download_book(testBook, "", 1, 1, text, metaDict)

for i in metaDict:
    print i, metaDict[i]
	
#print("\n".join(links))
#print(len(links))

log.close()
sys.exit()