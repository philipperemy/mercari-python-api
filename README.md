## The Python Mercari API

A Python interface to the unofficial Mercari API.

<p align="center">
  <img src="https://www-mercari-com.akamaized.net/assets/img/common/common/logo.svg?3119344368" width="500">&nbsp&nbsp&nbsp
  <img src="https://asset.fril.jp/assets/v3/popup/logo-5ee09819ceb0cb939c01302150e2c253888ead06c741e7af86c5636fa62e851f.png">
</p>

### Example

```python
from mercari import Mercari

mercari_api = Mercari()

print('_' * 80)
print(mercari_api.name)
print(mercari_api.fetch_all_items(keyword='CHANEL')[0:10])
print(mercari_api.get_item_info('https://www.mercari.com/jp/items/m88046246209/'))
```
  
## Installation

From PyPI

```bash
pip install mercari_python
```

From the sources

```bash
pip install git+ssh://git.github.com/philipperemy/mercari-python-api
```

## Monitoring

```bash
cd examples
# edit one of those two files to receive notifications.
cp gmail_conf.json.example gmail_conf.json # edit this file.
cp alertzy_conf.json.example alertzy_conf.json # edit this file.
python monitor.py --keywords "road bike,moto bike" --min_prices "0,0" --max_prices "43000,43000"
```

Note: Amazon AWS IPs are blacklisted by Mercari. So don't use AWS EC2 to run this script, it will not work.
