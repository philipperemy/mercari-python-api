import logging
from time import sleep

import mercari

logger = logging.getLogger(__name__)


def monitor(keyword='bike'):
    persisted_items = mercari.fetch_all_items(keyword=keyword, max_items_to_fetch=100)
    for item in persisted_items:
        logger.info(f'CURRENT = {item}.')

    while True:
        sleep(60 * 10)  # 10 minutes.
        items_on_first_page, _ = mercari.fetch_items_pagination(keyword=keyword, page_id=0)
        new_items = set(items_on_first_page) - set(persisted_items)
        for new_item in new_items:
            logger.info(f'NEW = {new_item}.')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - monitor - %(levelname)s - %(message)s', level=logging.INFO)
    monitor()
