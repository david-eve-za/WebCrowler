import argparse
import json
import os
import shutil

import requests
from PIL import Image
from bs4 import BeautifulSoup

from DBManager import Book, DBManager, ItemsManager
from Model import BookInfo, ChapterInfo
from common import get_base_path, get_base_url, get_wp_url
from utils import compare_two_lists

mngr = DBManager()


def argument_definition():
    parser = argparse.ArgumentParser()
    # Adding the first arguments
    parser.add_argument("-a", "--add", dest="book_name", help="Name of the book")
    parser.add_argument("--tmo", action="store_true")
    parser.add_argument("--djs", action="store_true")
    parser.add_argument("-u", "--update", action="store_true", help="Update book count")
    parser.add_argument("-l", "--list", action="store_true", help="List all Books and chapters")
    parser.add_argument("-d", "--download", action="store_true", help="Download all Books and chapters")

    return parser.parse_args()


def get_page_list(URL_Page) -> []:
    page = requests.get(URL_Page)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(rel="shortlink")
    index = results['href'].split('=')[1]
    data = {"action": "manga_get_chapters", "manga": index}
    url_local = get_wp_url()
    page = requests.post(url_local, data)
    soup = BeautifulSoup(page.content, "html.parser")
    chapter_list = []
    for a in soup.find_all('a', href=True):
        # print("found URL: {}".format(a['href']))
        if a['href'] != '#' and a['href'] != URL_Page + '/':
            chapter_list.append(a['href'])
    return chapter_list


def get_pictures(img_url) -> []:
    page = requests.get(img_url)
    soup = BeautifulSoup(page.content, "html.parser")
    img = []
    for i in soup.find_all(class_='wp-manga-chapter-img'):
        img.append(i['src'].strip())
    return img


def download_picture(pic_url, _chPath):
    response = requests.get(pic_url, stream=True)
    path = os.path.join(_chPath, pic_url.split('/')[-1])
    if not os.path.exists(_chPath):
        os.makedirs(_chPath)
    with open(path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    return path


def add_book(args):
    if not args.tmo or not args.djs:
        print("Debe seleccionar al menos un servidor")
        exit(1)
    elif args.tmo and args.djs:
        print("Debe seleccionar solo un servidor")
        exit(1)
    book = Book()
    book.set_name(args.book_name)
    if args.tmo:
        book.set_server_id("tmo")
    else:
        book.set_server_id("djs")
    book.save()


def show_books():
    for d in mngr.list():
        b = Book(d)
        print(b)


def update_book_count():
    for d in mngr.list():
        b = Book(d)
        pages = get_page_list(f'{get_base_url()}{b.get_name(False)}')
        b.set_chapters(len(pages))
        b.save()


def remove(tbp):
    for f in tbp:
        os.unlink(f)


def create_pdf(tbp, filename):
    images = []
    for f in tbp:
        if os.path.getsize(f) > 0:
            image = Image.open(f)
            image = image.convert('RGB')
            images.append(image)
    images[0].save(filename, save_all=True, append_images=images[1:])
    print(f'Created {filename}')
    remove(tbp)


def download_metadata():
    for b in ItemsManager().get_all_books():
        b = BookInfo(b)
        pages = get_page_list(b.get_title())
        pages.reverse()
        not_in_list = compare_two_lists(b.get_data()['chapters'], pages)
        for i in not_in_list:
            chi = ChapterInfo()
            chi.title(i)
            imgs = get_pictures(i)
            for im in imgs:
                chi.pages(im)
            b.chapters(chi)
        ItemsManager().update_books(b)


def download_books():
    for d in mngr.list():
        b = Book(d)
        tbp = os.path.join(get_base_path(), b.get_name(False))
        pages = get_page_list(f'{get_base_url()}{b.get_name(False)}')
        for p in pages:
            pdf_name = os.path.join(tbp, f'{p.split("/")[-2]}.pdf')
            if not os.path.exists(pdf_name):
                imgs = get_pictures(p)
                if len(imgs) > 0:
                    img_d = []
                    for i in imgs:
                        img_d.append(download_picture(i, tbp))
                    create_pdf(img_d, pdf_name)


def process_args(args):
    if args.book_name:
        add_book(args)
    if args.list:
        show_books()
    if args.update:
        update_book_count()
    if args.download:
        download_books()


if __name__ == '__main__':
    # args = argument_definition()
    # print(args)
    # process_args(args)
    download_metadata()
    for i in mngr.list():
        bk = Book(i)
        bki = BookInfo()
        bki.title(f'{get_base_url()}{bk.get_name(False)}')
        pages = get_page_list(f'{get_base_url()}{bk.get_name(False)}')
        pages.reverse()
        for p in pages:
            chi = ChapterInfo()
            chi.title(p)
            imgs = get_pictures(p)
            for im in imgs:
                chi.pages(im)
            bki.chapters(chi)
        print(json.dumps(bki.get_data(), indent=4))
        ItemsManager().update_books(bki)
