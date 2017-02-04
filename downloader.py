"""Downloader Python 3.6 Script

Downloads all the text files located on "http://twain.lib.niu.edu"
"""
from bs4 import BeautifulSoup			#pip
from tinydb import TinyDB, Query 		#pip
import urllib.request
import fnmatch
import sys
import consts
import functs
import os
from tqdm import tqdm					#pip
import signal
import logging
import argparse							#pip
from classes import BookMeta
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--clean', action='store_true', help="Removes all text files and purges Books TABLE in database")
args = parser.parse_args()

#pylint: disable=w0201,w0622
class DelayedKeyboardInterrupt(object): 
    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        logging.debug('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)


def my_print(text, newLine=True):
	"""Flushes stdout and prints the text"""
	if newLine:
		sys.stdout.write(str(text) + "\n")
	else:
		sys.stdout.write(str(text))
	sys.stdout.flush()
#End my_print

def prepare_name(text):
	text = text.replace('<', '').replace('>', '').replace(':', '').replace('"', '').replace('/', '').replace('\\', '').replace('|', '').replace('?', '').replace('*', '').replace('\0', '').replace('\'', '').replace('\n', '')
	text = text[0:100]
	return text


def get_urls(queryStr, linksArray):
	#Vars
	pageNum = 0 				#Start at first page
	functs.clear()
	printStr = "Querying " + '"' + urllib.request.unquote(queryStr) + '"'
	
	my_print(printStr)
	while True:			#Start loop
		#Url to get links from		
		urlSearch = "http://twain.lib.niu.edu/islandora/search/%20?page=" + str(pageNum) + "&type=dismax&f[0]=mods_resource_type_ms%3A%22" + queryStr + "%22"
		my_print("Searching : " + urlSearch)					#Print Searching...

		page = urllib.request.urlopen(urlSearch)				#Get page instance
		soup = BeautifulSoup(page.read(), "html5lib")			#Get html page
		results = soup.find('p', attrs={'class' : 'no-results'})#See if there are results
		if results is not None:		#End of query results
			break		#End loop
		#Find all a elements
		for a in soup.findAll('a', href=True):
			linksArray.append(a['href'])		#Get their href value
		pageNum += 1	#Increment page value and loop again
	#print
#End get_urls


def download_book(url, _bookMeta: BookMeta):
	text_bytes = bytes()
	#my_print("Downloading Book " + str(number) + " of " + str(total) + " : " + url)	#Print Downloading...
	page = urllib.request.urlopen(url)				#Get page instance
	content = page.read()
	soup = BeautifulSoup(content, "html5lib")		#Get html page

	#Get meta
	divTag = soup.find_all("div", attrs={"class": "niu-artfl"})
	for tag in divTag:
		tdTags = tag.find_all("meta", {"content":True, "name":True})
		for tag in tdTags:
			name = tag['name'].replace("DC.", "")
			if hasattr(_bookMeta, name):
				title = prepare_name(tag['content'])
				setattr(_bookMeta, name, title)
				#metaDict[name] = title
				#my_print(title)
			else:	
				if getattr(_bookMeta, name) is None:
					setattr(_bookMeta, name, tag['content'])
				else:
					getattr(_bookMeta, name).append(tag['content'])
	#Get Text
	for div in soup.find_all('div', attrs={"class":"niu-artfl"}):	#Get body of text
		#log.write(div.text.encode('utf-8'))
		text_bytes += div.text.encode('utf-8')
	return text_bytes
#End download_book

#Main Code **************************************

#Variables text mixed material
CLEAN = "clean"
DB_NAME = "db.json"
ROOT_DB_NAME = "Mark_Twain_Database/"
APP_DATA_DIR = os.environ['LOCALAPPDATA'].replace('\\', '/') + "/"
ROOT_DB_DIR = APP_DATA_DIR + ROOT_DB_NAME
SAVE_BOOKS_DIR = ROOT_DB_DIR + "books/"
DB_PATH = ROOT_DB_DIR + DB_NAME

BASE_URL = "http://twain.lib.niu.edu"	#Base url used along with book url	
URL_MATCH = "*/islandora/object/*"		#Links matching this are texts
QUERIES = ["text", "mixed%20material"]	#Queries to use in urls to download text
links = []								#Holds links to text webpages
metaDict = {}							#Dictionary to hold meta data

#Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("downloader.log", 'w', 'utf-8')
handler.setFormatter = logging.Formatter('%(levelname)s:%(message)s')
logger.addHandler(handler)

#Check database directory
if not os.path.isdir(ROOT_DB_DIR):
	os.makedirs(ROOT_DB_DIR)	#Make directory for db.json
	os.makedirs(SAVE_BOOKS_DIR)	#Make directory for text files

db = TinyDB(DB_PATH)			#Open database 
bTable = db.table('Books')		#Table to hold downloaded books information
Book = Query()

#Clean database
if args.clean:
	db.purge()
	bTable.purge()
	fileList = os.listdir(SAVE_BOOKS_DIR)
	for fileName in fileList:
		os.remove(SAVE_BOOKS_DIR + fileName)

#Get links	
for query in QUERIES:								
	get_urls(query, links)			
links = fnmatch.filter(links, URL_MATCH)		#Only keep matched urls

#Download books
numBooks = len(links)
count = 1
pbar = tqdm(total=numBooks)
functs.clear()
#print("Downloading books...")
for link in links:
	with DelayedKeyboardInterrupt():
		pbar.update(1)
		link = BASE_URL + link	#Get actual url
		#metaDict = {}			#Init dictionary
		bookMeta = BookMeta()
		#Check if book has been downloaded already
		if bTable.search(Book.url == link):
			logger.info("Book already Downloaded. url=" + link)
			continue
		#Get text
		bookText = download_book(link, bookMeta)				#Get text, and meta dictionary information
		bookText = str(bookText.decode('utf-8'))				#Decode bytes
		bookText = bookText.replace("\n", " ")					#Replace newlines with spaces
		bookText = " ".join(bookText.split())					#Remove extra whitespace
		#Set name and 2 dictionary values
		name = bookMeta.title if bookMeta.title is not None else ""		#Get title of book
		date = bookMeta.date if bookMeta.date is not None else ""		#Get date of book
		logger.info(name + "this is the name")
		logger.info(date + " this is the date")
		bookMeta.path = SAVE_BOOKS_DIR + name + "(" + date +")" + ".txt"	#Set save path for book text
		bookMeta.url = link													#Set url value
		#Skip book if it has no title
		if not name:
			#Create text file of book
			#print metaDict[consts.PATH]
			with open(bookMeta.path, "w", encoding='utf-8') as textFile:		#Write text file, title is name of book
				textFile.write(bookText)		#Write string to file
			#Write to TinyDB
			bTable.insert(bookMeta.__dict__)			#Add value to database
		count += 1						#Increase count
pbar.close()

#Sound beep for progress finished
print("\a")

#Close files and exit
db.close()
sys.exit()
