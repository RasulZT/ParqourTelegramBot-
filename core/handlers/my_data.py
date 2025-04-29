from aiogram import Bot, Router, F
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.handlers.basic import get_start
from core.keyboards.inline import get_back_inline_keyboard
from core.utils.ChatHistoryHandler import ChatHistoryHandler
from core.utils.RestHandler import RestHandler
from core.utils.states import States

router = Router()


@router.callback_query(F.data == 'common:my_data')
async def get_my_data(callback: CallbackQuery, chat_handler: ChatHistoryHandler, state: FSMContext):
    context = await state.get_data()
    user = context.get('user')
    if user is None:
        return

    await chat_handler.delete_messages(callback.message.chat.id)
    await chat_handler.send_message(callback.message, f'👤 *Мои данные:*\n\n'
                                                      f'ID: {user["telegram_id"]}\n'
                                                      f'Роль: {user["role"]}\n'
                                    ,
                                    reply_markup=get_back_inline_keyboard())
    await state.set_state(States.MY_DATA)


@router.callback_query(States.MY_DATA, F.data == 'to-back')
async def go_back(callback: CallbackQuery, chat_handler: ChatHistoryHandler, rest: RestHandler, state: FSMContext,
                  command: CommandObject | None = None):
    await chat_handler.delete_messages(callback.message.chat.id)
    await get_start(callback.message, rest, state, chat_handler, command)
