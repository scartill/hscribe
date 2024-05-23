import os
import traceback
import asyncio

from telegram import Bot

import utils as u
import hscribe


telegram_bot_name = os.getenv('TELEGRAM_BOT_NAME')
secret = u.get_sm_secret(f'telegram/{telegram_bot_name}')
token = secret['Token']
bot = Bot(token)


async def fetch_audio_file(file_id):
    file = await bot.get_file(file_id)
    array = await file.download_as_bytearray()
    return array


def try_process_update(params):
    try:
        message = params['message']
        print('MESSAGE', message)
        chat_id = message['chat']['id']

        if audio := message.get('audio'):
            array = asyncio.run(fetch_audio_file(audio['file_id']))
            translation = hscribe.process_blob(array)
            print('TRANSLATION', translation)
            asyncio.run(bot.send_message(chat_id=chat_id, text=translation))

        else:
            print('No audio file found')

    except Exception as exc:
        raise UserWarning(f'Unable to process the update ({exc})')


def lambda_handler(event, context):
    try:
        method, params = u.request_params(event)
        passed_token = params.get('token')

        if not passed_token:
            raise UserWarning('No authentication token')

        if token != passed_token:
            raise UserWarning('Access denied: invalid token')

        if method == 'POST':
            try_process_update(params)
            return

        raise UserWarning(f'Unknown call with {method}')

    except Exception:
        traceback.print_exc()
        print('OFFENDING EVENT', event)
    finally:
        return u.response()
