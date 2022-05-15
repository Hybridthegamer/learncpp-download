import logging
import time
from typing import Optional

import weasyprint
from helper import common, scraper


class WeasySequential:
    def download(self, cooldown: Optional[int] = 0) -> None:
        urls = scraper.get_urls()
        for sno, url in enumerate(urls):
            logging.info(f"Downloading: {url}")
            filename = common.get_filename(sno, url)
            pdf = weasyprint.HTML(url).write_pdf()
            open(filename, "wb").write(pdf)
            common.progress(sno, len(urls))
            time.sleep(cooldown)
