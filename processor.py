"""Processor module

Processes text stored in database
"""
import consts
from classes import BookMeta, TextBlock
from tinydb import TinyDB
import os
#import logging
import fnmatch
import logging
import re
import math


def loadText(_path):
    """Loads text in utf-8 encoding"""
    #NOTE: ".text" addition should be changed. Error in database storage
    with open(_path + ".txt", 'r', encoding="utf-8") as f:
        _text = f.read()
    return _text
#End loadText

def searchRange(_stringList):
    """Searches string list for the date range of the text
        @param  _stringList (list) List of words of text
        @return _range      (list) The approx. range of the date written
    """  
    _DATE_RE = '*[0-9][0-9][0-9][0-9]*'
    _DATE_RANGE = [1861, 1900]
    _dateList = []
    _dates = fnmatch.filter(_stringList, _DATE_RE)		#Find all dates
    for w in _dates:
        _date = int(re.sub("[^0-9]", "", w))
        if _date > _DATE_RANGE[0] and _date < _DATE_RANGE[1]:
            _dateList.append(_date)
    print(_dateList)
    if len(_dateList) == 0:
        return None            #Return None for no dataset
    else:
        _sumX = 0
        _sumXS = 0
        _n = len(_dateList)
        for a in _dateList:
            _sumX += a
            _sumXS += (a * a)
        _std = math.sqrt((_sumXS) - ((_sumX) * (_sumX) / _n) / (_n - 1))
        _avg = _sumX / _n
        return [_avg - _std, _avg + _std]         #Return range
#End searchRange

def processBook(_bookMeta: BookMeta):
	_block = TextBlock()
	_text = loadText(_bookMeta.path)    #Get text
	_words = _text.split()              #Get list of words
	_range = searchRange(_words)		#(list(int))Search for the date range

	#Set TextBlock values
	_block.date_range = _range			#Set textblock date range
#End processBook
#Main: ****************************************************************
#Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("processor.log", 'w', 'utf-8')
handler.setFormatter = logging.Formatter('%(levelname)s:%(message)s')
logger.addHandler(handler)

#Import the database
if not os.path.isdir(consts.ROOT_DB_DIR):   #Check if it exists
	os.makedirs(consts.ROOT_DB_DIR)	    #Make directory for db.json
	os.makedirs(consts.BOOKS_DIR)	    #Make directory for text files
db = TinyDB(consts.DB_PATH)			        #Open database 
tBooks = db.table(consts.TABLE_BOOKS)   #Open book table

#Search all texts
bookList = tBooks.all()         #Get list of every object in database
for book in bookList:           #Loop through each bookmeta object
    processBook(book)           #Processes book

