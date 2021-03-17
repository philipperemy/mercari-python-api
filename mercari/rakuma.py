import logging
from time import sleep
from typing import Union, List, Any
from urllib.parse import urlencode

from mercari.common import Common, Item, _get_soup

logger = logging.getLogger(__name__)


# noinspection SpellCheckingInspection
class Rakuma(Common):

    def fetch_all_items(
            self,
            keyword: str = 'bicycle',
            price_min: Union[None, int] = None,
            price_max: Union[None, int] = None,
            max_items_to_fetch: Union[None, int] = 100
    ) -> List[str]:
        items_list = []
        for page_id in range(1, int(1e9)):  # rakuma starts at page 1.
            items, _ = self.fetch_items_pagination(keyword, page_id, price_min, price_max)
            items_list.extend(items)
            logger.debug(f'Found {len(items_list)} items so far.')
            if max_items_to_fetch is not None and len(items_list) > max_items_to_fetch:
                logger.debug(f'Reached the maximum items to fetch: {max_items_to_fetch}.')
                break
            sleep(2)
        logger.debug('No more items to fetch.')
        return items_list

    def fetch_items_pagination(
            self,
            keyword: str,
            page_id: int = 1,
            price_min: Union[None, int] = None,
            price_max: Union[None, int] = None
    ) -> Union[List[str], Any]:
        soup = _get_soup(self._fetch_url(page_id, keyword, price_min=price_min, price_max=price_max))
        items = [item.a.attrs['href'] for item in soup.find_all('div', {'class': 'item-box__image-wrapper'})]
        return items, None

    def get_item_info(
            self,
            item_url: str
    ) -> Item:
        soup = _get_soup(item_url)

        def fetch_meta(n):
            return soup.find('meta', {'property': n}).attrs['content']

        name = fetch_meta('og:title')
        if '|' in name:
            name = name.split('|')[0]
        item = Item(
            name=name,
            desc=fetch_meta('og:description'),
            price=fetch_meta('product:price:amount'),
            sold_out='out' in fetch_meta('product:availability'),
            url_photo=fetch_meta('og:image'),
            url=item_url,
        )

        return item

    def _fetch_url(
            self,
            page: int = 0,
            keyword: str = 'bicycle',
            price_min: Union[None, int] = None,
            price_max: Union[None, int] = None
    ) -> str:
        # https://fril.jp/s?max=30000&min=10000&order=desc&page=2&query=clothes&sort=relevance
        params = {'query': keyword, 'order': 'desc', 'sort': 'relevance'}
        if price_min is not None:
            params.update({'min': price_min})
        if price_max is not None:
            params.update({'max': price_max})
        if page >= 2:
            params.update({'page': page})
        url = 'https://fril.jp/s?' + urlencode(params)
        return url

    @property
    def name(self) -> str:
        return 'rakuma'


if __name__ == '__main__':
    pass
    # Rakuma().fetch_url(price_min=10000, price_max=30000)
    # Rakuma().get_item_info(item_url='https://item.fril.jp/d5e617f4bc33a979a9d20d19b110852a')
    # Rakuma().fetch_items_pagination(keyword='bicycle', page_id=1, price_min=10000, price_max=30000)
    # Rakuma().fetch_all_items(keyword='bicycle', max_items_to_fetch=100)
