"""Processor module

Processes text stored in database
"""
import consts
from classes import BookMeta, TextBlock
from tinydb import TinyDB, Query
import os
#import logging
import fnmatch
import logging
import re
import math
import csv
import textwrap

#Processing functions START here. *******************************************************************

def loadText(_path):
    """Loads text in utf-8 encoding"""
    #Read in text from file
    with open(_path, 'r', encoding="utf-8") as f:
        _text = f.read()
    return _text
#End loadText

def searchRange(_stringList, id):
    """Searches string list for the date range of the text
        @param  _stringList (list) List of words of text
        @return _range      (list) The approx. range of the date written
    """  
    _DATE_RE = '*[0-9][0-9][0-9][0-9]*'
    _DATE_RANGE = [1861, 1900]
    _dates = fnmatch.filter(_stringList, _DATE_RE)        #Find all dates
    _dateList = []
    print("id is *********", id, "******************")
    for d in _dates:
        _num = int(re.sub("[^0-9]", "", d))
        #print("test print", _testList)
        if (_num >= _DATE_RANGE[0]) and (_num <= _DATE_RANGE[1]):
            _dateList.append(_num)
    _n = len(_dateList)
    if _n <= 1:
        return None            #Return None for no dataset
    else:
        _sumX = 0
        _sumXS = 0
        _std = 0
        for a in _dateList:
            _sumX += a
        _mean = _sumX / _n
        for a in _dateList:
            _std += math.pow(a - _mean, 2)
        _std = math.sqrt(_std / (_n - 1))
        r1 = math.ceil(_mean - _std)
        r2 = math.ceil(_mean + _std)
        return [r1, r2]         #Return range
#End searchRange

def findIndex(string, list):
	MAX = 100
	WIDTH = 80
	city = ""
	loc = 0
	#Prints location of places
	strLen = len(string)
	
	for row in list:
		city = row[0]
		loc = string.find(city)
		if loc != -1:
			#get start
			counter = 0
			index = 2
			while(counter < MAX and loc - index != -1):
				if(string[loc - index] == " "):
					counter += 1
				index += 1
				#print("counter : ", counter, "Max : ", MAX)
			start = loc - index
			#get end
			counter = 0
			index = len(city) + 2
			while(counter < MAX and loc + index != strLen):
				if(string[loc + index] == " "):
					counter += 1
				index += 1
				#print("counter : ", counter, "Max : ", MAX)
			end = loc + index
			#print("100 words from ", end, " to ", loc)
			text1 = ' '.join(string[start + 2:loc].split())
			lines1 = textwrap.wrap(text1, WIDTH)
			text2 = "*[" + string[loc: loc + len(city)] + "]*" 
			text3 = ' '.join(string[loc + len(city): end].split())
			lines3 = textwrap.wrap(text3, WIDTH)
			
			output = ""
			lineCount = 0
			for line in lines1:			#Add first 100 words
				lineCount += 1
				output += line + "\n"
			output = output[:-1]		#Subtract last \n
			output += " "				#Replace with space
			output += text2				#Add city mention
			for line in lines3:			#Add last 100 words
				lineCount += 1
				output += line + "\n"
			print("\n Block :")
			print(output)
		#print("matched at : ", string.find(city))
#End index

#Processing functions END here. **********************************************************************

def processBook(_bookMeta: BookMeta, _id):
    _block = TextBlock()                #Text block instance
    _text = loadText(_bookMeta.path)    #Get text
    _words = _text.split()              #Get list of words
    findIndex(_text, cities_51)
    #_range = searchRange(_words, _id)        #(list(int))Search for the date range

    #Set TextBlock values
    _block.meta_id = _id                #Set id pointer to meta book table
    #_block.date_range = _range          #Set textblock date range

    #Send textblock to the database
    updateDB(_bookMeta, _block)
#End processBook

def updateDB(_bookMeta: BookMeta, _block: TextBlock):
    if not tBlocks.search(blockQ.meta_id == _block.meta_id):
        tBlocks.insert(_block.__dict__)  

#Main: ****************************************************************
#Variables
cities_51 = []
cities_78 = []

#Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("processor.log", 'w', 'utf-8')
handler.setFormatter = logging.Formatter('%(levelname)s:%(message)s')
logger.addHandler(handler)

#Import the database
if not os.path.isdir(consts.ROOT_DB_DIR):   #Check if it exists
    os.makedirs(consts.ROOT_DB_DIR)         #Make directory for db.json
    os.makedirs(consts.BOOKS_DIR)           #Make directory for text files
db = TinyDB(consts.DB_PATH)                 #Open database 
tBooks = db.table(consts.TABLE_BOOKS)       #Open book table
tBlocks = db.table(consts.TABLE_BLOCKS)     #Open block table
tBlocks.purge()                             #Purge Text Blocks table
blockQ = Query()

#Load both cvs files
#First one 1851
i = 0
with open(consts.CSV_1, newline='') as csvfile:
	reader = csv.reader(csvfile, dialect='excel')
	for row in reader:
		if i != 0:
			cities_51.append(row)
		i += 1
#First second 1878
i = 0
with open(consts.CSV_2, newline='') as csvfile:
	reader = csv.reader(csvfile, dialect='excel')
	for row in reader:
		if i != 0:
			cities_78.append(row)
		i += 1

#Search all texts
bookList = tBooks.all()         #Get list of every object in database
for bookDict in bookList:       #Loop through each bookmeta object
    eid = bookDict.eid          #Get id from       
    book = BookMeta(bookDict)    #Convert dictionary to BookMeta
    processBook(book, eid)       #Processes book


