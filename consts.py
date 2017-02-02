import os

_DB_NAME = "db.json"
_ROOT_DB_NAME = "Mark_Twain_Database/"
_APP_DATA_DIR = os.environ['LOCALAPPDATA'].replace('\\', '/') + "/"
_ROOT_DB_DIR = _APP_DATA_DIR + _ROOT_DB_NAME
BOOKS_DIR = _ROOT_DB_DIR + "books/"
DB_PATH = _ROOT_DB_DIR + _DB_NAME


TITLE = "title"
CREATOR = "creator"
DATE = "date"
PUBLISHER = "publisher"
SOURCE = "source"
IDENTIFIER = "identifier"
TYPE = "type"
FORMAT = "format"
GENRE = "genre"
PERIOD = "period"
THEME = "theme"
GENDER = "gender"
PATH = "path"
URL = "url"

