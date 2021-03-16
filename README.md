# The Python Mercari API

A Python interface to the unofficial Mercari API.

<p align="center">
  <img src="https://www-mercari-com.akamaized.net/assets/img/common/common/logo.svg?3119344368" width="500">
</p>

## Documentation

Documentation is as follows.

### Public endpoints

- **```mercari.fetch_all_items(keyword='bike', price_max=None)```**
  - `keyword`: Keyword search.
  - `price_max`: Maximum price in Yen.
  - `returns`: Returns a list of item urls.
  

- **```mercari.get_item_info(item_url='https://item.mercari.com/jp/m72639077322/')```**
  - `item_url`: The URL of the item. Returns from the `fetch_all_items` function.
  - `returns`: `Item` object (name, desc, price, is sold out...)

### Private endpoints

- Not implemented yet.
  
## Installation

Simply run:

```bash
git clone git@github.com:philipperemy/mercari-python-api.git
cd mercari-python-api
virtualenv -p python3 venv && source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Monitoring

```bash
cd examples
cp gmail_conf.json.example gmail_conf.json
vim gmail_conf.json # edit this file.
python -u monitor.py --keywords "road bike, moto bike" --max_prices "43000,43000" --min_prices "0,0"
```

## Important 

Amazon AWS IPs are blacklisted by Mercari. So don't use AWS EC2 to run this script, it will not work.
