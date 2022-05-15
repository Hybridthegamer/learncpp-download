import logging
import os
import time
from typing import Optional

import pdfkit
import ray
import requests
import weasyprint
from xhtml2pdf import pisa

from helper import common, constants, scraper


class Render:
    def __init__(self) -> None:
        self.urls = []

    def get_urls(self, cooldown):
        return scraper.get_urls(cooldown)


class WkRender(Render):
    options = {
        "cookie": [("ezCMPCookieConsent", "-1=1|1=1|2=1|3=1|4=1")],
        "disable-javascript": None,
        "page-size": "A4",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0",
    }

    def __init__(self, sequential: Optional[bool] = False) -> None:
        super(WkRender).__init__()
        self.cooldown = 0
        self.sequential = sequential
        self.urls = self.get_urls()
        common.make_download_dir()

    def set_cooldown(self, cooldown: int) -> None:
        self.cooldown = cooldown

    def download(self) -> None:
        if self.sequential:
            self.__download_sequential()
        else:
            self.__download()

    def __download(self) -> None:
        futures = []
        for it, url in enumerate(self.urls):
            logging.info(f"Downloading: {url}")
            futures.append(ray_download.remote(1 + it, url))
            common.progress(it, len(self.urls))
            time.sleep(self.cooldown)

        ray.get(futures)

    def __download_sequential(self) -> None:
        for sno, url in enumerate(self.urls):
            logging.info(f"Downloading: {url}")
            filename = common.get_filename(sno, url)
            pdfkit.from_url(url, filename, options=WkRender.options)
            common.progress(sno, len(self.urls))
            time.sleep(self.cooldown)


class WeasyRender(Render):
    def __init__(
        self, sequential: Optional[bool] = False, cooldown: Optional[int] = 0
    ) -> None:
        super(WeasyRender).__init__()
        self.urls = self.get_urls(cooldown)[:10]
        self.cooldown = cooldown
        common.make_download_dir()

    def download(self) -> None:
        if self.sequential:
            self.__download_sequential()
        else:
            self.__download()

    def __download(self) -> None:
        futures = []
        for it, url in enumerate(self.urls):
            logging.info(f"Downloading: {url}")
            futures.append(ray_download_weasy.remote(1 + it, url))
            common.progress(it, len(self.urls))
            time.sleep(self.cooldown)

        ray.get(futures)


class PisaRender(Render):
    def __init__(self, cooldown: Optional[int] = 0) -> None:
        super(PisaRender, self).__init__()
        self.urls = self.get_urls(cooldown)
        self.cooldown = cooldown
        common.make_download_dir()

    def download(self) -> None:
        for it, url in enumerate(self.urls):
            logging.info(f"Downloading: {url}")
            download_pisa(1 + it, url)
            common.progress(it, len(self.urls))
            time.sleep(self.cooldown)


@ray.remote
def ray_download(sno: int, url: str) -> None:
    filename = common.get_filename(sno, url)

    try:
        pdfkit.from_url(url, filename, options=WkRender.options)
    except Exception as e:
        logging.error(f"unable to download: {url}")
        logging.exception(e)


@ray.remote
def ray_download_weasy(sno: int, url: str) -> None:
    pdf = weasyprint.HTML(url).write_pdf()
    filename = common.get_filename(1 + sno, url)
    open(filename, "wb").write(pdf)


def download_pisa(sno: int, url: str) -> None:
    filename = common.get_filename(1 + sno, url)
    with open(filename, "wb") as result:
        html = requests.get(url).text
        pisa.CreatePDF(html, dest=result)


logging.basicConfig(
    level=logging.WARN, format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"
)
