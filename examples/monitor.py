import argparse
import json
import logging
import os
import threading
from time import sleep
from typing import Union

import requests
from mailthon import postman, email

import mercari

logger = logging.getLogger(__name__)


def get_script_arguments():
    parser = argparse.ArgumentParser(description='Receive notifications every time new items matching '
                                                 'your request parameters are available.')
    parser.add_argument('--keywords', required=True, type=str, help='Keywords separated by a comma.')
    parser.add_argument('--max_prices', required=True, type=str,
                        help='Maximum price for each item separated by a comma.')
    parser.add_argument('--min_prices', required=True, type=str,
                        help='Minimum price for each item separated by a comma.')
    args = parser.parse_args()
    logger.info(args)
    return args


class Alertzy:

    def __init__(self):
        self.use_module = True
        self.lock = threading.Lock()
        config_filename = 'alertzy_conf.json'
        if os.path.isfile(config_filename):
            with open(config_filename, 'r') as r:
                self.alertzy_key = json.load(r)['alertzy_key']
            self.send_notification('Monitoring has started.', title='Mercari')
        else:
            self.use_module = False
            logger.warning('Alertzy was not configured. Notifications will not be sent to your '
                           'iPhone through the Alertzy app.')

    def send_notification(self, message, title):
        # https://alertzy.app/
        if self.use_module:
            with self.lock:
                assert self.alertzy_key is not None
                try:
                    requests.post('https://alertzy.app/send', data={
                        'accountKey': self.alertzy_key,
                        'title': title,
                        'message': message
                    })
                except Exception:
                    return False
                return True


class GMailSender:
    def __init__(self):
        self.use_module = True
        self.lock = threading.Lock()
        gmail_config_filename = 'gmail_conf.json'
        if os.path.isfile(gmail_config_filename):
            with open(gmail_config_filename, 'r') as gmail:
                gmail_constants = json.load(gmail)
                self.gmail_password = gmail_constants['gmail_password']
                self.gmail_user = gmail_constants['gmail_user']
                if '@' not in self.gmail_user:
                    logger.error('Gmail user should be a GMAIL address.')
                    exit(1)
                self.recipients = [x.strip() for x in gmail_constants['recipients'].strip().split(',')]
        else:
            self.use_module = False
            logger.warning('Gmail is not configured. If you want to receive email notifications, '
                           'copy gmail_conf.json.example to gmail_conf.json and edit the constants. '
                           'I advise you to create a new Gmail account, just for this purpose.')

    def send_email_notification(self, email_subject, email_content, attachment=None):
        if self.use_module:
            with self.lock:
                if attachment is not None:
                    attachment = [attachment]
                else:
                    attachment = ()
                for recipient in self.recipients:
                    p = postman(host='smtp.gmail.com', auth=(self.gmail_user, self.gmail_password))
                    r = p.send(email(content=email_content,
                                     subject=email_subject,
                                     sender='{0} <{0}>'.format(self.gmail_user),
                                     receivers=[recipient],
                                     attachments=attachment))
                    logger.info(f'Email subject is {email_subject}.')
                    logger.info(f'Email content is {email_content}.')
                    logger.info(f'Attachment located at {attachment}.')
                    logger.info(f'Notification sent from {self.gmail_user}.')
                    logger.info(f'Notification sent to {recipient}.')
                    assert r.ok


class MonitorKeyword:
    def __init__(self, keyword: str, price_min: int, price_max: int,
                 gmail_sender: Union[None, GMailSender],
                 alertzy: Union[None, Alertzy]):
        self.keyword = keyword
        self.price_min = price_min
        self.price_max = price_max
        self.gmail_sender = gmail_sender
        self.alertzy = alertzy
        self.thread = threading.Thread(target=self.task, daemon=True)

    def join(self):
        self.thread.join()

    def start(self):
        self.thread.start()

    def task(self):
        logger.info(f'[{self.keyword}] Starting monitoring with price_max = {self.price_max} '
                    f'and price_min = {self.price_min}.')
        persisted_items = mercari.fetch_all_items(
            keyword=self.keyword,
            price_min=self.price_min,
            price_max=self.price_max,
            max_items_to_fetch=100
        )
        logger.info(f'We found {len(persisted_items)} items.')
        time_between_two_requests = 30
        logger.info(f'We will check the first page every {time_between_two_requests} seconds and look for new items.')
        logger.info('The program has started to monitor for new items...')

        while True:
            sleep(time_between_two_requests)
            items_on_first_page, _ = mercari.fetch_items_pagination(
                keyword=self.keyword,
                page_id=0,
                price_min=self.price_min,
                price_max=self.price_max
            )
            new_items = set(items_on_first_page) - set(persisted_items)
            for new_item in new_items:
                logger.info(f'[{self.keyword}] New item detected: {new_item}.')
                persisted_items.append(new_item)
                item = mercari.get_item_info(new_item)
                email_subject = f'{item.name} {item.price}'
                email_subject_with_url = f'{email_subject} {item.url}'
                email_content = f'{item.url}<br/><br/>{item.desc}'
                attachment = item.local_url
                if self.alertzy is not None:
                    logger.info('Will send an Alertzy notification.')
                    self.alertzy.send_notification(email_subject_with_url, title=self.keyword)
                else:
                    logger.info('Will skip Alertzy.')
                if self.gmail_sender is not None:
                    logger.info('Will send a GMAIL notification.')
                    self.gmail_sender.send_email_notification(email_subject, email_content, attachment)
                else:
                    logger.info('Will skip GMAIL.')


def init_logging():
    format_str = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format_str)
    log_filename = 'monitor.log'
    print(f'Logging to [{log_filename}].')
    logging.basicConfig(
        format=format_str,
        filename=log_filename,
        level=logging.INFO
    )
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def main():
    init_logging()
    args = get_script_arguments()
    keywords = args.keywords.strip().split(',')
    max_prices = [int(v) for v in args.max_prices.strip().split(',')]
    min_prices = [int(v) for v in args.min_prices.strip().split(',')]
    gmail = GMailSender()
    alertzy = Alertzy()
    monitors = []
    for keyword, min_price, max_price in zip(keywords, min_prices, max_prices):
        monitors.append(MonitorKeyword(keyword.strip(), min_price, max_price, gmail, alertzy))
    for monitor in monitors:
        monitor.start()
        sleep(5)  # delay the start between them.
    for monitor in monitors:
        monitor.join()


if __name__ == '__main__':
    main()
