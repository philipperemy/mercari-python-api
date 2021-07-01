from time import sleep
from typing import List, Any, Union

from absl import logging

from mercari.common import Item, Common, _get_soup


# noinspection PyProtectedMember


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
            items = self.fetch_items_pagination(keyword, page_id, price_min, price_max)
            items_list.extend(items)
            logging.debug(f'Found {len(items_list)} items so far.')

            if max_items_to_fetch is not None and len(items_list) > max_items_to_fetch:
                logging.debug(f'Reached the maximum items to fetch: {max_items_to_fetch}.')
                break
            sleep(2)

        logging.debug('No more items to fetch.')
        return items_list

    def fetch_items_pagination(
            self,
            keyword: str,
            page_id: int = 0,
            price_min: Union[None, int] = None,
            price_max: Union[None, int] = None
    ) -> Union[List[str], Any]:  # List of URLS and a HTML marker.
        soup = _get_soup(self._fetch_url(page_id, keyword, price_min=price_min, price_max=price_max))
        links = soup.find_all(href=lambda x: x and "/us/item/" in x)

        items = [s['href'].replace("/?ref=search_results", "") for s in links]
        items = [it if it.startswith('http') else 'https://www.mercari.com' + it for it in items]
        return items

    def get_item_info(
            self,
            item_url: str = 'https://www.mercari.com/jp/items/m53585037017/'
    ) -> Item:
        soup = _get_soup(item_url)
        price = float(soup.find('meta', {'property': 'product:price:amount'})["content"])
        name = str(soup.find('meta', {'property': 'og:title'})["content"])
        desc = soup.find('meta', {'property': 'og:description'})["content"]
        condition = soup.find('meta', {'itemprop': 'itemCondition'})["content"]  # TODO: Filter to Like new
        new_label =soup.find('span', class_=lambda t: t and "Blue" in t, text='New')
        recently_edited = soup.find('p', class_=lambda c: c and "Text__T4" in c,
                                    text=lambda t: 'minute' in t)
        is_new = True if new_label and recently_edited else False
        # TODO Add Tags: Tags__TagLink
        in_stock = True if soup.find('meta', {'property': 'og:availability'}, content='instock') else False

        photo = str(soup.find('meta', {'property': 'og:image'})["content"])

        item = Item(name=name, price=price, desc=desc, condition=condition, is_new=is_new, in_stock=in_stock,
                    url_photo=photo, url=item_url)
        return item

    def _fetch_url(
            self,
            page: int = 0,
            keyword: str = 'txt',
            price_min: Union[None, int] = None,
            price_max: Union[None, int] = None
    ):
        url = f'https://www.mercari.com/search/?page={page}'
        url += f'&keyword={keyword}'
        url += '&sort_order='
        if price_max is not None:
            url += f'&price_max={price_max}'
        if price_min is not None:
            url += f'&price_min={price_min}'
        # logging.debug(url)
        return url

    @property
    def name(self) -> str:
        return 'mercari'
