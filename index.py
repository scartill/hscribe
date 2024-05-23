import os
import traceback

import boto3
from telegram import Bot

import utils as u


telegram_bot_name = os.getenv('TELEGRAM_BOT_NAME')
secret = u.get_sm_secret(f'telegram/{telegram_bot_name}')
token = secret['Token']
bot = Bot(token)


def try_process_update(params):
    print('PARAMS', params)
    try:
        message = params['message']
        text = message['text']
        chat_id = message['chat']['id']
        from_user = message['from']
        from_id = str(from_user['id'])
    
    except Exception as exc:
        raise UserWarning(f'Not enough parameters in the update ({exc})')


def handler(event, context):
    try:
        method, params = u.request_params(event)
        passed_token = params.get('token')

        if not passed_token:
            raise UserWarning('No authentication token')

        if token != passed_token:
            raise UserWarning('Access denied: invalid token')

        if method == 'POST':
            return try_process_update(params)

        raise UserWarning(f'Unknown call with {method}')

    except Exception:
        traceback.print_exc()
        print('OFFENDING EVENT', event)
        return True
