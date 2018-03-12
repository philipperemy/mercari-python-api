import argparse
import json
import logging
import os
import threading
from time import sleep

from mailthon import postman, email

import mercari

logger = logging.getLogger(__name__)


def get_script_arguments():
    parser = argparse.ArgumentParser(description='Receive Gmail notifications every time new items matching '
                                                 'your request parameters are available.')
    parser.add_argument('--keywords', required=True, type=str, help='Keywords separated by a comma (,).')
    parser.add_argument('--price_max', type=str, help='Maximum price for each item.', default=None)
    args = parser.parse_args()
    logger.info(args)
    return args


class GMailSender:
    def __init__(self):
        self.lock = threading.Lock()

    def send_email_notification(self, email_subject, email_content, attachment):
        with self.lock:
            gmail_config_filename = 'gmail_conf.json'
            if os.path.isfile(gmail_config_filename):
                with open(gmail_config_filename, 'r') as gmail:
                    gmail_constants = json.load(gmail)
                    gmail_user = gmail_constants['gmail_user']
                    gmail_password = gmail_constants['gmail_password']
                    target_email = gmail_constants['target_email']
                    user = f'{gmail_user}@gmail.com'
                    p = postman(host='smtp.gmail.com', auth=(user, gmail_password))
                    r = p.send(email(content=email_content,
                                     subject=email_subject,
                                     sender='{0} <{0}>'.format(user),
                                     receivers=[target_email],
                                     attachments=[attachment]))
                    logger.info(f'Email subject is {email_subject}.')
                    logger.info(f'Email content is {email_content}.')
                    logger.info(f'Attachment located at {attachment}.')
                    logger.info(f'Notification sent to {target_email}.')
                    assert r.ok
            else:
                logger.info('Gmail is not configured. If you want to receive email notifications, '
                            'copy gmail_conf.json.example to gmail_conf.json and edit the constants. '
                            'I advise you to create a new Gmail account, just for this purpose.')


class MonitorKeyword:
    def __init__(self, keyword: str, price_max: int, gmail_sender: GMailSender):
        self.keyword = keyword
        self.price_max = price_max
        self.gmail_sender = gmail_sender
        self.thread = threading.Thread(target=self.task)

    def join(self):
        self.thread.join()

    def start(self):
        self.thread.start()

    def task(self):
        logger.info(f'[{self.keyword}] Starting monitoring.')
        persisted_items = mercari.fetch_all_items(keyword=self.keyword,
                                                  price_max=self.price_max,
                                                  max_items_to_fetch=100)
        for item in persisted_items:
            logger.info(f'[{self.keyword}] CURRENT = {item}.')

        while True:
            logger.info(f'[{self.keyword}] Fetching the first page to check new results.')
            items_on_first_page, _ = mercari.fetch_items_pagination(keyword=self.keyword,
                                                                    page_id=0,
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
    price_max = int(args.price_max) if args.price_max is not None else None
    gmail = GMailSender()
    monitors = []
    for keyword in keywords:
        monitors.append(MonitorKeyword(keyword, price_max, gmail))
    for monitor in monitors:
        monitor.start()
        sleep(5)  # delay the start between them.
    for monitor in monitors:
        monitor.join()


if __name__ == '__main__':
    main()
