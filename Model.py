import uuid
from typing import List


class ChapterInfo:

    def __init__(self, data=None):
        if data is not None:
            self.data = data
        else:
            self.data = {'title': '', 'pages': []}

    def title(self, title):
        self.data['title'] = title

    def pages(self, page):
        self.data['pages'].append(page)

    def pages_list(self):
        return self.data['pages']

    def get_data(self):
        return self.data


class BookInfo:

    def __init__(self, data=None):
        if data is not None:
            self.data = data
        else:
            self.data = {'uuid': str(uuid.uuid1()), 'title': '', 'chapters': []}

    def title(self, title):
        self.data['title'] = title

    def get_title(self):
        return self.data['title']

    def chapters(self, chapter: ChapterInfo):
        self.data['chapters'].append(chapter.get_data())

    def chapters_count(self):
        return len(self.data['chapters'])

    def chapter_list(self) -> List[ChapterInfo]:
        tmp = []
        for i in self.data['chapters']:
            tmp.append(ChapterInfo(i))
        return tmp

    def get_data(self):
        return self.data

    def get_uuid(self):
        return self.data['uuid']
