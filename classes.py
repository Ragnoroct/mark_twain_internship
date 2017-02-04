#Holds python classes used

class TextBlock(object):
    def __init__(self):
        self.text = None
        self.date_range = None


#pylint: disable=w0612
class BookMeta(object):
    """Struct to hold meta data for a Book

    Attributes
        title       The title of book(string)
        creator     The writer of book(string)
        date        Date published(string)
        publisher   Publisher of book(string)
        source      Source of book(string)
        identifier  ID value for book(string)
        type        Type of file ie. text, image(string)
        format      Format of text ie. book, article(string)
        genre       Genre of book(string)
        period      Period/Era(string)
        theme       Theme of book(string)
        gender      Gender of writer(string)
        path        Path to text file(string)
        url         Url to book hosted(string)
        words       Number of words(int)
        searchStrengh   The strength of the search. 0 = No search.
    """
    def __init__(self, aDict=None):
        #Variables
        self.title = None
        self.creator = None
        self.date = None
        self.publisher = None
        self.source = None
        self.identifier = None
        self.type = None
        self.format = None
        self.genre = None
        self.period = None
        self.theme = None
        self.gender = None
        self.path = None
        self.url = None
        self.words = None
        self.searchStrengh = 0

        if aDict is not None:
            for k in aDict:
                if hasattr(self, k):
                    setattr(self, k, aDict[k])

class Struct(object):
    def __init__(self, adict):
        """Convert a dictionary to a class

        @param :adict Dictionary
        """
        self.__dict__.update(adict)
        for k, v in adict.items():
            if isinstance(v, dict):
                self.__dict__[k] = Struct(v)

def get_object(adict):
    """Convert a dictionary to a class

    @param :adict Dictionary
    @return :class:Struct
    """
    return Struct(adict)
