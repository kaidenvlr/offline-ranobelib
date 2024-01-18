import json
import os
import re

import requests
from bs4 import BeautifulSoup
from slugify import slugify

from config import config


def get_novel_title(url: str) -> str:
    reqs = requests.session()
    page_html = reqs.get(url).text
    page = BeautifulSoup(page_html, "lxml")
    return page.find("div", {"class": "media-name__main"}).text.strip()


def get_info(url):
    reqs = requests.session()
    info = {}
    page_html = reqs.get(url).text
    page = BeautifulSoup(page_html, "lxml")
    info["title"] = page.find("div", {"class": "media-name__main"}).text.strip()
    info["description"] = page.find("div", {"class": "media-description__text"}).text.strip()
    info["authors"] = [x.text.strip() for x in page.find("div", string="Автор").parent.find_all("a")]
    info["tags"] = [x.text.strip().title() for x in page.find("div", {"class": "media-tags"}).find_all("a")]
    info["poster_url"] = page.find("div", {"class": "media-sidebar__cover paper"}).find("img")["src"]
    chapters = re.search(config.chapters_json_pattern, page_html).group(1)
    chapters = json.loads(chapters)
    # -------------------
    info["chapters"] = {}
    for c in reversed(chapters["chapters"]["list"]):
        if str(c["chapter_volume"]) not in info["chapters"]:
            info["chapters"][str(c["chapter_volume"])] = []
        info["chapters"][str(c["chapter_volume"])].append(c)
    c = 0
    for _ in info["chapters"].keys():
        c += 1
    info["volumes"] = c
    with open("data.json", "w+") as f:
        f.write(json.dumps(info))
    return info


def verify_book_folder(url: str) -> bool:
    info = get_info(url)
    dir_path = os.path.join(os.path.join(config.project_path, "media"), slugify(info["title"]))
    try:
        count = 0
        for path in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, path)):
                count += 1

        if count == info["volumes"]:
            return True
        return False
    except:
        return False


def get_files(url: str) -> list[str]:
    title = get_novel_title(url)
    dir_path = os.path.join(os.path.join(config.project_path, "media"), slugify(title))
    filepaths = []
    for (_, _, filenames) in os.walk(dir_path):
        for file in filenames:
            filepaths.append(os.path.join(dir_path, file))
        break
    return filepaths
