import argparse
import os
import shutil

import requests
from PIL import Image
from bs4 import BeautifulSoup

from DBManager import ItemsManager
from Model import ChapterInfo
from common import get_base_path, get_wp_url
from utils import compare_two_lists


def argument_definition():
    parser = argparse.ArgumentParser()
    # Adding the first arguments
    parser.add_argument("-a", "--add", dest="book_name", help="Name of the book")
    parser.add_argument("--tmo", action="store_true")
    parser.add_argument("--djs", action="store_true")
    parser.add_argument("-u", "--update", action="store_true", help="Download book metadata")
    parser.add_argument("-l", "--list", action="store_true", help="List all Books and chapters")
    parser.add_argument("-d", "--download", action="store_true", help="Download all Books and chapters")

    return parser.parse_args()


def get_page_list(page_url) -> []:
    page = requests.get(page_url)
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
        if a['href'] != '#' and a['href'] != page_url + '/':
            chapter_list.append(a['href'])
    return chapter_list


def get_pictures(img_url) -> []:
    page = requests.get(img_url)
    soup = BeautifulSoup(page.content, "html.parser")
    images = []
    for image in soup.find_all(class_='wp-manga-chapter-img'):
        images.append(image['src'].strip())
    return images


def download_picture(picture_url, chapter_path):
    response = requests.get(picture_url, stream=True)
    path = os.path.join(chapter_path, picture_url.split('/')[-1])
    if not os.path.exists(chapter_path):
        os.makedirs(chapter_path)
    with open(path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    return path


def add_book(args):
    # TODO Implement this function for add new books
    pass


def remove_file(tbp):
    for f in tbp:
        os.unlink(f)


def create_pdf(to_be_process, pdf_name):
    images = []
    for file_name in to_be_process:
        if os.path.getsize(file_name) > 0:
            image = Image.open(file_name)
            image = image.convert('RGB')
            images.append(image)
    images[0].save(pdf_name, save_all=True, append_images=images[1:])
    print(f'Created {pdf_name}')
    remove_file(to_be_process)


def download_metadata():
    for book in ItemsManager().get_all_books():
        chapters = get_page_list(book.get_title())
        chapters.reverse()
        not_in_list = compare_two_lists(book.get_data()['chapters'], chapters)
        for i in not_in_list:
            chapter_info = ChapterInfo()
            chapter_info.title(i)
            images = get_pictures(i)
            for image in images:
                chapter_info.pages(image)
            book.chapters(chapter_info)
        ItemsManager().update_books(book)


def download_books():
    for book in ItemsManager().get_all_books():
        to_be_processed = os.path.join(get_base_path(), book.get_title().split("/")[-1])
        pages = get_page_list(book.get_title())
        for page in pages:
            pdf_name = os.path.join(to_be_processed, f'{page.split("/")[-2]}.pdf')
            if not os.path.exists(pdf_name):
                images = get_pictures(page)
                if len(images) > 0:
                    images_downloaded = []
                    for image in images:
                        images_downloaded.append(download_picture(image, to_be_processed))
                    create_pdf(images_downloaded, pdf_name)


def show_books():
    for book in ItemsManager().get_all_books():
        print(book.get_title())


def process_args(args):
    if args.book_name:
        add_book(args)
    if args.list:
        show_books()
    if args.update:
        download_metadata()
    if args.download:
        download_books()


if __name__ == '__main__':
    args = argument_definition()
    print(args)
    process_args(args)
