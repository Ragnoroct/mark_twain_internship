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

#Processing functions END here. **********************************************************************

def processBook(_bookMeta: BookMeta, _id):
    _block = TextBlock()                #Text block instance
    _text = loadText(_bookMeta.path)    #Get text
    _words = _text.split()              #Get list of words
    _range = searchRange(_words, _id)        #(list(int))Search for the date range

    #Set TextBlock values
    _block.meta_id = _id                #Set id pointer to meta book table
    _block.date_range = _range          #Set textblock date range

    #Send textblock to the database
    updateDB(_bookMeta, _block)
#End processBook

def updateDB(_bookMeta: BookMeta, _block: TextBlock):
    if not tBlocks.search(blockQ.meta_id == _block.meta_id):
        tBlocks.insert(_block.__dict__)  

#Main: ****************************************************************
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

#Search all texts
bookList = tBooks.all()         #Get list of every object in database
for bookDict in bookList:       #Loop through each bookmeta object
    eid = bookDict.eid          #Get id from       
    book = BookMeta(bookDict)    #Convert dictionary to BookMeta
    processBook(book, eid)       #Processes book


