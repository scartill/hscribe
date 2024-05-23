import sys
import logging as lg

import utils as u
from telegram import Bot


telegram_bot_name = sys.argv[1]
api = sys.argv[2]
lg.info(f'Bot name {telegram_bot_name}')
secret = u.get_sm_secret(f'telegram/{telegram_bot_name}')
token = secret['Token']
bot = Bot(token)


def install_webhook(this):
    response = bot.set_webhook(url=f'{this}?token={token}')

    if not response:
        raise RuntimeError('Unable to set up the webhook')

    lg.info('Webhook: installed')
