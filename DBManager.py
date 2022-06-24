import json
import logging
import os
from base64 import b64encode, b64decode

from tinydb import TinyDB
from tinydb.table import Document

from Model import BookInfo
from common import get_base_path


class DBManager:
    __instance = None

    def __new__(cls):
        if DBManager.__instance is None:
            DBManager.__instance = object.__new__(cls)
        return DBManager.__instance

    def __init__(self):
        if not os.path.exists(get_base_path()):
            os.makedirs(get_base_path())
        __db_path = os.path.join(get_base_path(), 'db.json')
        self.db = TinyDB(__db_path)

    def update(self, record):
        self.db.update(record, doc_id=record['id'])

    def list(self):
        return self.db.all()


class Book():

    def __init__(self, data: Document = None):
        self.manager = DBManager()
        self.__id = 0
        if data is not None:
            self.data = data
        else:
            self.data = {}

    def __str__(self):
        return self.data.__str__()

    def set_name(self, name):
        self.data['name'] = b64encode(name.encode('ascii')).decode('ascii')

    def get_name(self, hide=True):
        if hide:
            return self.data['name']
        return b64decode(self.data['name'].encode('ascii')).decode('ascii')

    def set_server_id(self, server_id):
        self.data['server_id'] = server_id

    def get_server_id(self):
        return self.data['server_id']

    def set_chapters(self, num_chapters):
        self.data['num_chapters'] = num_chapters

    def get_chapters(self):
        return self.data['num_chapters']

    def set_downloaded(self, downloaded):
        self.data['downloaded'] = downloaded

    def get_downloaded(self):
        return self.data['downloaded']

    def save(self):
        if not hasattr(self.data, "doc_id"):
            self.data = Document(self.data, self.manager.db.insert(self.data))
        else:
            self.manager.db.upsert(self.data)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


class ItemsManager(object):
    __instance = None

    def __new__(cls):
        if ItemsManager.__instance is None:
            ItemsManager.__instance = object.__new__(cls)
        return ItemsManager.__instance

    def __init__(self):
        if not os.path.exists(get_base_path()):
            os.makedirs(get_base_path())
        self.books_file = os.path.join(get_base_path(), 'Books.json')
        self.books_list = []
        if not os.path.exists(self.books_file):
            self.save()
        self.__readfile()

    def __readfile(self):
        with open(self.books_file, "r") as fIn:
            self.books_list = json.load(fIn)

    def save(self):
        with open(self.books_file, "w") as fOut:
            json.dump(self.books_list, fOut, indent=4)

    def update_books(self, data: BookInfo):
        exist = False
        for i in range(len(self.books_list)):
            if self.books_list[i]['uuid'] == data.get_uuid():
                self.books_list[i] = data.get_data()
                exist = True
        if not exist:
            self.books_list.append(data.get_data())
        self.save()

    def get_book(self, pos) -> BookInfo:
        return self.books_list[pos]

    def get_all_books(self) -> list[BookInfo]:
        return self.books_list
