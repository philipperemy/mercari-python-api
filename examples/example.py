from mercari import Mercari
from absl import logging

logging.set_verbosity(logging.DEBUG)

mercari_api = Mercari()

print('_' * 80)
print(mercari_api.name)
print(mercari_api.get_item_info('https://www.mercari.com/us/item/m65712116039/'))
print(mercari_api.fetch_all_items(keyword='txt')[0:10])
