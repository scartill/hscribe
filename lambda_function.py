import os
import io
import traceback
import asyncio
from typing import Any, Dict

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Update, Message
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from aiogram.fsm.state import State

import utils as u
import hscribe


telegram_bot_name = os.getenv('TELEGRAM_BOT_NAME')
secret = u.get_sm_secret(f'telegram/{telegram_bot_name}')
token = secret['Token']
bot = Bot(token=token)

admin_router = Router()
router = Router()


class UserContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Any,
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            data['user_id'] = user_id
            data['allowed_accounts'] = []  # Placeholder list
        elif hasattr(event, "message") and event.message and event.message.from_user:
            user_id = event.message.from_user.id
            data['user_id'] = user_id
            data['allowed_accounts'] = []  # Placeholder list

        return await handler(event, data)


class DynamoDBStorage(BaseStorage):
    async def set_state(self, key: StorageKey, state: str | State | None = None) -> None:
        pass

    async def get_state(self, key: StorageKey) -> str | None:
        return None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        pass

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        return {}

    async def close(self) -> None:
        pass


dp = Dispatcher(storage=DynamoDBStorage())
dp.message.middleware(UserContextMiddleware())
dp.include_router(admin_router)
dp.include_router(router)


@router.message(F.audio)
async def handle_audio(message: Message, bot: Bot) -> None:
    try:
        if not message.audio:
            print('No audio file found')
            return

        print('MESSAGE', message.model_dump())
        chat_id = message.chat.id

        file_id = message.audio.file_id
        file = await bot.get_file(file_id)

        file_io = io.BytesIO()
        await bot.download_file(file.file_path, destination=file_io)
        array = file_io.getvalue()

        translation = hscribe.process_blob(array)
        print('TRANSLATION', translation)
        await message.answer(text=translation)

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
            try:
                if loop := asyncio.get_event_loop():
                    if loop.is_closed():
                        asyncio.set_event_loop(asyncio.new_event_loop())
            except RuntimeError:
                print('Starting the first asyncio loop')

            update = Update(**params)
            asyncio.run(dp.feed_update(bot, update))
            return

        raise UserWarning(f'Unknown call with {method}')

    except Exception:
        traceback.print_exc()
        print('OFFENDING EVENT', event)
    finally:
        return u.response()
