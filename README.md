# The Python Mercari API

A Python interface to the unofficial Mercari API.

<p align="center">
  <img src="https://www-mercari-com.akamaized.net/assets/img/common/common/logo.svg?3119344368" width="500">
</p>

## Documentation

Documentation is as follows.

- **```mercari.fetch_all_items(keyword='bike', price_max=None)```**
  - `keyword`: The day on which to execute the query.
  - `price_max`: Maximum price in Yen.
  - `returns`: Returns a list of item urls.
  

- **```mercari.get_item_info(item_url='https://item.mercari.com/jp/m72639077322/')```**
  - `item_url`: The day on which to execute the query.
  - `returns`: `Item` object (name, desc, price, is sold out...)
  
