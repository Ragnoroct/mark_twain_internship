"""Places module

To extract places and locations in a text file
"""
 
import re
from geotext import GeoText

#Places functions start here**************************************************************


def file_open(filename):
	"""Reads text from a file and coverts it into a geotext object"""
	with open(filename , "r") as a:
        	a.seek(0)
        	w= a.read()
        	p = GeoText(w)
		return p,w
#End file_open

places,words = file_open("abc.txt")
l = places.cities
q = places.countries
str = re.findall(r"[\w']+",words)

def unique(list):
	"""Removes duplicate places""" 
	new_list = []
	for i in list:
        	if i not in new_list:
                	new_list.append(i)
	return new_list
#End unique

city = unique(l)
country = unique(q)

print city
print country

def index(string, list):
	#Prints location of places
	for f in range(0,len(list)):
        	for s in range(0,len(string)):
                	if(list[f]==string[s]):
                        	print string[s],
                        	print "Index in file :",
                        	print s
#End index

index(str,city)
index(str,country)


