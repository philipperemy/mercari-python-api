from mercari import Mercari
from mercari import Rakuma

mercari_api = Mercari()
rakuma_api = Rakuma()

print('_' * 80)
print(mercari_api.name)
print(mercari_api.fetch_all_items(keyword='CHANEL')[0:10])
print(mercari_api.get_item_info('https://www.mercari.com/jp/items/m88046246209/'))

print('_' * 80)
print(rakuma_api.name)
print(rakuma_api.fetch_all_items(keyword='CHANEL')[0:10])
print(rakuma_api.get_item_info('https://item.fril.jp/e0c79971ed2b15e083428d93803e78f0'))
