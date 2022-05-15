import os
import sys
from typing import Optional

from helper import constants


def get_filename(sno: int, url: str):
    return (
        constants.DOWNLOAD_PATH
        + "/"
        + str(sno).zfill(3)
        + "-"
        + url.split("/")[-2]
        + ".pdf"
    )


def progress(count: int, total: int, status: Optional[str] = "") -> None:
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)

    sys.stdout.write("[%s] %s%s ...%s\r" % (bar, percents, "%", status))
    sys.stdout.flush()


def make_download_dir() -> None:
    if not os.path.exists(constants.DOWNLOAD_PATH):
        os.makedirs(constants.DOWNLOAD_PATH)
