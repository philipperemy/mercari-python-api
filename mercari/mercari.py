import logging
import re
from time import sleep
from typing import List, Any, Union

# noinspection PyProtectedMember
from bs4 import NavigableString

from mercari.common import Item, Common, _get_soup

logger = logging.getLogger(__name__)


class Mercari(Common):

    def fetch_all_items(
            self,
            keyword: str = 'clothes',
            price_min: Union[None, int] = None,
            price_max: Union[None, int] = None,
            max_items_to_fetch: Union[None, int] = 100
    ) -> List[str]:  # list of URLs.
        items_list = []
        for page_id in range(int(1e9)):
            items, search_res_head_tag = self.fetch_items_pagination(keyword, page_id, price_min, price_max)
            items_list.extend(items)
            logger.debug(f'Found {len(items_list)} items so far.')

            if max_items_to_fetch is not None and len(items_list) > max_items_to_fetch:
                logger.debug(f'Reached the maximum items to fetch: {max_items_to_fetch}.')
                break

            if search_res_head_tag is None:
                break
            else:
                search_res_head = str(search_res_head_tag.contents[0]).strip()
                num_items = re.findall('\d+', search_res_head)
                if len(num_items) == 1 and num_items[0] == '0':
                    break
            sleep(2)
        logger.debug('No more items to fetch.')
        return items_list

    def fetch_items_pagination(
            self,
            keyword: str,
            page_id: int = 0,
            price_min: Union[None, int] = None,
            price_max: Union[None, int] = None
    ) -> Union[List[str], Any]:  # List of URLS and a HTML marker.
        soup = _get_soup(self._fetch_url(page_id, keyword, price_min=price_min, price_max=price_max))
        search_res_head_tag = soup.find('h2', {'class': 'search-result-head'})
        items = [s.find('a').attrs['href'] for s in soup.find_all('section', {'class': 'items-box'})]
        items = [it if it.startswith('http') else 'https://www.mercari.com' + it for it in items]
        return items, search_res_head_tag

    def get_item_info(
            self,
            item_url: str = 'https://www.mercari.com/jp/items/m53585037017/'
    ) -> Item:
        soup = _get_soup(item_url)
        soup = soup.find('section', {'class': 'item-box-container'})
        price = str(soup.find('span', {'class': 'item-price bold'}).contents[0]).replace('¥', '').replace(',', '')
        name = str(soup.find('h1', {'class': 'item-name'}).contents[0])

        def filter_html_br(x):
            return isinstance(x, NavigableString)

        desc = list(filter(filter_html_br, soup.find('div', {'class': 'item-description f14'})))
        desc = list(map(str, desc))
        desc = ''.join(desc)

        sold_out = soup.find('div', {'class': 'item-sold-out-badge'})
        sold_out = sold_out is not None

        photo = soup.find('div', {'class': 'item-photo'})
        photo = photo.find('img').attrs['data-src']

        item = Item(name=name, price=price, desc=desc, sold_out=sold_out, url_photo=photo, url=item_url)
        return item

    def _fetch_url(
            self,
            page: int = 0,
            keyword: str = 'bicycle',
            price_min: Union[None, int] = None,
            price_max: Union[None, int] = None
    ):
        url = f'https://www.mercari.com/jp/search/?page={page}'
        url += f'&keyword={keyword}'
        url += '&sort_order='
        if price_max is not None:
            url += f'&price_max={price_max}'
        if price_min is not None:
            url += f'&price_min={price_min}'
        return url

    @property
    def name(self) -> str:
        return 'mercari'
