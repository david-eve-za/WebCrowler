import json
import logging
import os

from typing import List

from Model import BookInfo
from common import get_base_path

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

    def get_all_books(self) -> List[BookInfo]:
        tmp = []
        for i in self.books_list:
            tmp.append(BookInfo(i))
        return tmp
