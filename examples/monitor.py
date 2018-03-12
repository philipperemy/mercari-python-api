import json
import logging
import os
from time import sleep

from mailthon import postman, email

import mercari

logger = logging.getLogger(__name__)


class GMailSender:
    @staticmethod
    def send_email_notification(email_subject, email_content, attachment):
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


def monitor(keyword='bike'):
    persisted_items = mercari.fetch_all_items(keyword=keyword, max_items_to_fetch=100)
    for item in persisted_items:
        logger.info(f'CURRENT = {item}.')

    while True:
        logger.info('Fetching the first page to check new results.')
        items_on_first_page, _ = mercari.fetch_items_pagination(keyword=keyword, page_id=0)
        new_items = set(items_on_first_page) - set(persisted_items)
        for new_item in new_items:
            logger.info(f'NEW = {new_item}.')
            persisted_items.append(new_item)
            item = mercari.get_item_info(new_item)
            email_subject = f'{item.name} {item.price}'
            email_content = f'{item.url}\n\n{item.desc}'
            attachment = item.local_url
            GMailSender.send_email_notification(email_subject, email_content, attachment)
        sleep(30)  # 30 seconds.


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - monitor - %(levelname)s - %(message)s', level=logging.INFO)
    monitor()
