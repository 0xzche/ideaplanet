"""
import requests
#url = "https://api.opensea.io/api/v1/collections?asset_owner=0xE5d4924413ae59AE717358526bbe11BB4A5D76b9&offset=0&limit=300"
#url = "https://opensea.io/collection/azuki"
url = "https://opensea.io/assets/0x2eb6be120ef111553f768fcd509b6368e82d1661/1884"
headers = {"Accept": "application/json"}
response = requests.request("GET", url, headers=headers)
print(response.text)
"""

from argparse import ArgumentParser
from ast import arg
import os
import pathlib
import requests
from selenium import webdriver
import datetime
# the 2 lines below are for printing logging messages 
import logging as log
log.basicConfig(level=log.INFO)
# the 3 lines below make browser invisible
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import utils
from utils import Timer
chrome_options = utils.get_chrome_options()

base_url_map = {
    "azuki": "https://opensea.io/assets/0xed5af388653567af2f388e6224dc7c4b3241c544/",
    "0xzuki": "https://opensea.io/assets/0x2eb6be120ef111553f768fcd509b6368e82d1661/",
}
        

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--slug", default="azuki")
    parser.add_argument("--start", "-s", type=0)
    parser.add_argument("--end", "-e", type=10)
    args = parser.parse_args()
    slug = args.slug
    output_dir = pathlib.Path("/Users/zche/data/0xgenerator/database/") / slug
    root_url = pathlib.Path(base_url_map[slug])
    log.info(f"downloading {slug} {args.start} to {args.end-1}")
    with webdriver.Chrome(options=chrome_options) as driver: # open a browser 
        for num in range(args.start, args.end):
            try:
                with Timer(f"{slug} {num}"):
                    url = f"{root_url}/{num}"
                    log.info(f"opening {url}")
                    driver.get(url)
                    with Timer(f"loading image of {slug} {num}"):
                        elem = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "Property--type")))
                        print(elem.text)
            except Exception as e:
                log.warning(f"noooo!!! failed getting {slug} {num}")
                log.warning(f"error: {e}")