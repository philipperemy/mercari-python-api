import logging
import tempfile
from pathlib import Path
from typing import List, Any, Union
from urllib.parse import urlparse

import requests
import wget
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Item:

    def __init__(self,
                 name: str, price: Union[int, str], desc: str,
                 sold_out: bool, url_photo: str, url: str):
        """
        :param name: Name of the item (String).
        :param price: Price (Integer)
        :param desc: Description of the item (String).
        :param sold_out: If the item was sold (Boolean).
        :param url_photo: URL to the photo (String).
        :param url: Local path to the downloaded photo (String).
        """
        self.name = name
        self.price = int(price)
        self.desc = desc
        self.sold_out = sold_out
        self.url_photo = url_photo
        self.url = url
        self.local_url = _download_photo(self.url_photo)

    def __str__(self) -> str:
        return f'(name={self.name}, price={self.price}, desc={self.desc.strip()}, sold_out={self.sold_out},' \
               f'url_photo={self.url_photo}, url={self.url}, local_url={self.local_url})'


class Common:

    def fetch_all_items(
            self,
            keyword: str,
            price_min: Union[None, int],
            price_max: Union[None, int],
            max_items_to_fetch: Union[None, int] = 100
    ) -> List[str]:  # list of URLs.
        """
        :rtype: A list of URL (Strings).
        :param keyword: Keyword for the search (required).
        :param price_min: Minimum price in yen (optional).
        :param price_max: Maximum price in yen (optional).
        :param max_items_to_fetch: Maximum number of items to return (optional).
        """
        pass

    def fetch_items_pagination(
            self,
            keyword: str,
            page_id: int,
            price_min: Union[None, int],
            price_max: Union[None, int]
    ) -> Union[List[str], Any]:  # List of URLS and a HTML marker.
        """
        :param keyword: Keyword for the search (required).
        :param page_id: The page id for the pagination (e.g. 0, 1, 2...)
        :param price_min: Minimum price in yen (optional).
        :param price_max: Maximum price in yen (optional).
        :rtype: List of URLS and a HTML marker.
        """
        pass

    def get_item_info(
            self,
            item_url: str
    ) -> Item:
        """
        :param item_url: The URL of the item to fetch.
        :rtype: Item: The Item object.
        """
        pass

    def _fetch_url(
            self,
            page: int,
            keyword: str,
            price_min: Union[None, int],
            price_max: Union[None, int]
    ) -> str:
        # https://fril.jp/s?max=30000&min=10000&order=desc&page=2&query=clothes&sort=relevance
        # https://www.mercari.com/jp/search/?page=200&keyword=%E9%9F%BF%EF%BC%91%EF%BC%97&sort_order=&price_max=10000
        pass

    @property
    def name(self) -> str:
        return 'common'


def _get_soup(url: str) -> BeautifulSoup:
    logger.info(f'GET: {url}')
    headers = {'User-Agent': "'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36'"}
    response = requests.get(url, headers=headers, timeout=20)
    if response.status_code != 200:
        logger.error(response)
        raise AssertionError()
    soup = BeautifulSoup(response.content, 'lxml')
    return soup


def _download_photo(url_photo: str, temp_dir: Union[None, str] = None):
    if temp_dir is None:
        temp_dir = Path(tempfile.gettempdir()) / 'photos'
    else:
        temp_dir = Path(temp_dir)
    if not temp_dir.exists():
        temp_dir.mkdir(parents=True, exist_ok=True)

    logger.debug(f'Selected tmp folder: {temp_dir}.')
    remote_filename = Path(urlparse(url_photo).path).name
    wget.download(url=url_photo, out=str(temp_dir), bar=None)
    local_url = str(temp_dir / remote_filename)
    return local_url
