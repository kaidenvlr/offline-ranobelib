import logging
import os
import random
import shutil
import string
import uuid

import requests
from bs4 import BeautifulSoup
from ebooklib import epub
from slugify import slugify
from yarl import URL

from config import config
from utils.info import get_info

logger = logging.getLogger(__name__)


def parse_chapter(url):
    images = {}
    while 1:
        headers = {"user-agent": "".join(random.choices(string.ascii_lowercase, k=12))}
        r = requests.get(url, headers=headers).text
        soup = BeautifulSoup(r, "lxml")
        content = soup.find("div", {"class": "reader-container container container_center"})
        break
    for i in content.find_all(recursive=True):
        a = list(i.attrs.keys())
        for y in a:
            if y not in ["data-src", "src"]:
                del i.attrs[y]
        if "data-src" in i.attrs:
            i.attrs["src"] = i.attrs["data-src"]
            del i.attrs["data-src"]
    for img in content.find_all("img", recursive=True):
        img.parent.attrs["class"] = "image-container"
        uid = uuid.uuid4().hex
        filetype = str(img.attrs["src"]).split(".")[-1]
        images[uid] = {
            "url": img.attrs["src"] if
            str(img.attrs["src"]).startswith("http") else
            config.ranobe_host + str(img.attrs["src"]),
            "filetype": filetype
        }
        img.attrs["src"] = f"{config.project_path}/media/images/{uid}.{filetype}"
    epub_images = []
    for uid, info in images.items():
        r = requests.get(info["url"], headers=headers)
        content_type = r.headers["content-type"]
        img = epub.EpubImage(
            uid=uid,
            file_name=f"{config.project_path}/media/images/{uid}.{info['filetype']}",
            media_type=content_type,
            content=r.content,
        )
        epub_images.append(img)
        # book.add_item(img)
    return content, epub_images


def concat_to_epub(url: str) -> list[str]:
    """
    Concatenate ranobe chapters to one book.
    One tome to one book
    :param url: - ranobe url from ranobelib.me
    :return: - returns filepath to book
    """
    reqs = requests.session()
    reqs.headers = {"user-agent": "".join(random.choices(string.ascii_lowercase, k=12))}
    info = get_info(url)
    url_host = URL(url)
    url_host = URL.build(scheme=url_host.scheme, host=url_host.host, path=url_host.path)
    book_folder = os.path.join(os.path.join(config.project_path, "media"), slugify(info["title"]))
    if os.path.exists(f"{book_folder}"):
        shutil.rmtree(book_folder)
        os.mkdir(book_folder)
    else:
        os.mkdir(book_folder)
    poster_content = reqs.get(info["poster_url"]).content
    filenames = []
    for tom, chapters in info["chapters"].items():
        book_images = []
        book = epub.EpubBook()
        book.set_cover(content=poster_content, file_name=f"cover.{info['poster_url'].split('.')[-1]}")
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(f"{tom} Том | {info['title']}")
        book_filename = slugify(f"{str(tom).rjust(3, '0')} Том | {info['title']}")
        book.set_language("ru")
        for aut in info["authors"]:
            book.add_author(aut)
        book.add_metadata("DC", "description", info["description"])
        st = '''.image-container {display: flex; justify-content: center}'''
        nav_css = epub.EpubItem(uid="style_nav",
                                file_name="style/nav.css",
                                media_type="text/css",
                                content=st)
        book.add_item(nav_css)

        epub_chapters = []
        i = 0
        for chapter in chapters:
            i += 1
            chapter_url = f"{url_host}/v{tom}/c{chapter['chapter_number']}"
            chapter_content, chapters_images = parse_chapter(chapter_url)
            print(f"{i} chapter parse completed")
            book_images += chapters_images
            c = epub.EpubHtml(title=f"Глава {chapter['chapter_number']} {chapter['chapter_name']}",
                              file_name=f"{str(uuid.uuid4())}.xhtml", lang="ru")
            n = chapter['chapter_number']
            m = chapter['chapter_name']
            s = chapter_content
            c.content = f'<h2 align="center" style="text-align:center;">Глава {n} {m}</h2>{s}'
            epub_chapters.append(c)
            book.add_item(c)
        print("chapters parsing completed")
        book.toc = epub_chapters
        book.spine = [*epub_chapters, "nav"]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        for img in book_images:
            book.add_item(img)
        epub.write_epub(f"{book_folder}/{book_filename}.epub", book,
                        {"play_order": {"enabled": True, "start_from": 1}})

        filenames.append(f"{book_folder}/{book_filename}.epub")
    return filenames

