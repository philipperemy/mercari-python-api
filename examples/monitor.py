from time import sleep

import argparse
import json
import logging
import os
import threading
from mailthon import postman, email

import mercari

logger = logging.getLogger(__name__)


def get_script_arguments():
    parser = argparse.ArgumentParser(description='Receive Gmail notifications every time new items matching '
                                                 'your request parameters are available.')
    parser.add_argument('--keywords', required=True, type=str, help='Keywords separated by a comma.')
    parser.add_argument('--max_prices', type=str, help='Maximum price for each item separated by a comma.')
    parser.add_argument('--min_prices', type=str, help='Minimum price for each item separated by a comma.')
    args = parser.parse_args()
    logger.info(args)
    return args


class GMailSender:
    def __init__(self):
        self.lock = threading.Lock()
        gmail_config_filename = 'gmail_conf.json'
        if os.path.isfile(gmail_config_filename):
            with open(gmail_config_filename, 'r') as gmail:
                gmail_constants = json.load(gmail)
                self.gmail_user = gmail_constants['gmail_user']
                self.gmail_password = gmail_constants['gmail_password']
                self.sender_email = gmail_constants['sender_email']
                self.recipients = [x.strip() for x in gmail_constants['recipients'].strip().split(',')]
        else:
            logger.info('Gmail is not configured. If you want to receive email notifications, '
                        'copy gmail_conf.json.example to gmail_conf.json and edit the constants. '
                        'I advise you to create a new Gmail account, just for this purpose.')

    def send_email_notification(self, email_subject, email_content, attachment):
        with self.lock:
            for recipient in self.recipients:
                p = postman(host='smtp.gmail.com', auth=(self.sender_email, self.gmail_password))
                r = p.send(email(content=email_content,
                                 subject=email_subject,
                                 sender='{0} <{0}>'.format(self.sender_email),
                                 receivers=[recipient],
                                 attachments=[attachment]))
                logger.info(f'Email subject is {email_subject}.')
                logger.info(f'Email content is {email_content}.')
                logger.info(f'Attachment located at {attachment}.')
                logger.info(f'Notification sent from {self.sender_email}.')
                logger.info(f'Notification sent to {recipient}.')
                assert r.ok


class MonitorKeyword:
    def __init__(self, keyword: str, price_min: int, price_max: int, gmail_sender: GMailSender):
        self.keyword = keyword
        self.price_min = price_min
        self.price_max = price_max
        self.gmail_sender = gmail_sender
        self.thread = threading.Thread(target=self.task, daemon=True)

    def join(self):
        self.thread.join()

    def start(self):
        self.thread.start()

    def task(self):
        logger.info(f'[{self.keyword}] Starting monitoring with price_max = {self.price_max} '
                    f'and price_min = {self.price_min}.')
        persisted_items = mercari.fetch_all_items(keyword=self.keyword,
                                                  price_min=self.price_min,
                                                  price_max=self.price_max,
                                                  max_items_to_fetch=100)
        for item in persisted_items:
            logger.info(f'[{self.keyword}] CURRENT = {item}.')

        while True:
            logger.info(f'[{self.keyword}] Fetching the first page to check new results.')
            items_on_first_page, _ = mercari.fetch_items_pagination(keyword=self.keyword,
                                                                    page_id=0,
                                                                    price_min=self.price_min,
                                                                    price_max=self.price_max)
            new_items = set(items_on_first_page) - set(persisted_items)
            for new_item in new_items:
                logger.info(f'[{self.keyword}] NEW = {new_item}.')
                persisted_items.append(new_item)
                item = mercari.get_item_info(new_item)
                email_subject = f'{item.name} {item.price}'
                email_content = f'{item.url}<br/><br/>{item.desc}'
                attachment = item.local_url
                if self.gmail_sender is not None:
                    self.gmail_sender.send_email_notification(email_subject, email_content, attachment)
            sleep(30)


def main():
    logging.basicConfig(format='%(asctime)s - monitor - %(levelname)s - %(message)s', level=logging.INFO)
    args = get_script_arguments()
    keywords = args.keywords.strip().split(',')
    max_prices = [int(v) for v in args.max_prices.strip().split(',')]
    min_prices = [int(v) for v in args.min_prices.strip().split(',')]
    gmail = GMailSender()
    monitors = []
    for keyword, min_price, max_price in zip(keywords, min_prices, max_prices):
        monitors.append(MonitorKeyword(keyword.strip(), min_price, max_price, gmail))
    for monitor in monitors:
        monitor.start()
        sleep(5)  # delay the start between them.
    for monitor in monitors:
        monitor.join()


if __name__ == '__main__':
    main()
