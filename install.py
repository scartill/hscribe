import sys
import logging as lg
import asyncio

import utils as u
from telegram import Bot


async def main():
    telegram_bot_name = sys.argv[1]
    api = sys.argv[2]
    lg.info(f'Bot name {telegram_bot_name}')
    secret = u.get_sm_secret(f'telegram/{telegram_bot_name}')
    token = secret['Token']
    bot = Bot(token)
    response = await bot.set_webhook(url=f'{api}?token={token}')

    if not response:
        raise RuntimeError('Unable to set up the webhook')

    print('Webhook: installed')


if __name__ == '__main__':
    asyncio.run(main())
