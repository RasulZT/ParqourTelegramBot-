from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import StorageKey

from core.handlers.basic import get_start
from core.keyboards.inline import get_back_inline_keyboard
from core.utils import RestHandler
from aiogram.filters import Command, CommandObject

from core.utils.ChatHistoryHandler import ChatHistoryHandler
from core.utils.redis_client import redis
from core.utils.states import States

router = Router()


@router.callback_query(F.data.startswith("open_ticket:"))
async def open_ticket_callback(callback: CallbackQuery, rest: RestHandler, bot: Bot, state: FSMContext):
    try:
        ticket_id = int(callback.data.split(":")[1])
        support_telegram_id = callback.from_user.id
        payload_upd = {
            "telegram_id": f"{support_telegram_id}"
        }
        response_upd = await rest.update(url=f"v1/services/tickets/{ticket_id}/update-ticket/", data=payload_upd)

        payload = {
            "support_telegram_id": support_telegram_id,
            "ticket_id": ticket_id
        }

        response = await rest.post(url="v1/services/tickets/create_session/", data=payload)

        if "error" in response:
            return await callback.answer(f"⚠ {response['error']}", show_alert=True)

        MY_GROUP_ID = -1002571604070  # Твой супергрупп чат ID
        parking = response.get("parking", {})
        print(f"Parking : {parking}")
        parking_name = response.get("parking", {}).get("name")
        parking_group_id = response.get("parking", {}).get("group_chat_id")
        topic = await bot.create_forum_topic(
            chat_id=MY_GROUP_ID,
            name=f"Сессия {parking_name}"
        )
        topic_id = topic.message_thread_id
        print(f"Topic : {topic}")

        await redis.set(f"session:topic_to_group:{topic_id}", parking_group_id)
        await redis.set(f"session:group_to_topic:{parking_group_id}", topic_id)
        await redis.set(f"ticket:topic_id:{ticket_id}", topic_id)

        # key = StorageKey(
        #     bot_id=bot.id,
        #     chat_id=callback.from_user.id,  # user ID вместо chat_id
        #     user_id=callback.from_user.id,
        # )
        # data = await state.storage.get_data(key)
        # topics = data.get("topics", {})
        # topics[topic.message_thread_id] = parking.get("group_chat_id")
        # await state.storage.set_data(key, {"topics": topics})
        # ⬇⬇⬇ Вот этот блок вставляется СЮДА

        new_keyboard = InlineKeyboardBuilder()
        new_keyboard.button(
            text="🚪 Перейти в чат",
            url=f"https://t.me/c/{str(MY_GROUP_ID)[4:]}/{topic_id}"
        )
        await callback.message.edit_reply_markup(reply_markup=new_keyboard.as_markup())

        await callback.answer("✅ Сессия и чат созданы!")

    except Exception as e:
        logging.error(f"❌ Ошибка при создании сессии и топика: {e}", exc_info=True)
        await callback.answer("⚠ Ошибка", show_alert=True)


@router.callback_query(F.data == "support:my_sessions")
async def show_support_sessions(callback: CallbackQuery, state, rest: RestHandler, chat_handler: ChatHistoryHandler):
    try:
        telegram_id = callback.from_user.id
        url = f"v1/services/support-sessions/?telegram_id={telegram_id}"

        sessions = await rest.get(url=url, state=state)

        if not sessions:
            return await callback.message.answer("🟡 У вас нет активных сессий.")

        for s in sessions:
            session_id = s.get("id")
            ticket_id = s.get("ticket", {}).get("id")
            parking_name = s.get("parking", {}).get("name")
            description = s.get("ticket", {}).get("description")

            text = (
                f"🆔 Сессия #{session_id}\n"
                f"🎫 Тикет #{ticket_id}\n"
                f"📍 Объект: {parking_name}\n"
                f"📝 Описание: {description or '—'}"
            )
            MY_GROUP_ID = -1002571604070
            topic_url = f"https://t.me/c/{str(MY_GROUP_ID)[4:]}"  # предполагается, что у тебя есть topic_id  /{s.get('topic_id')}

            kb = InlineKeyboardBuilder()
            kb.button(
                text="🔍 Информация",
                callback_data=f"support:session_info:{session_id}"
            )
            kb.button(
                text="🚪 Перейти в чат",
                url=topic_url
            )
            await callback.message.answer(text, reply_markup=kb.as_markup())

        await callback.message.answer(
            text="⬅️ Вернуться в главное меню",
            reply_markup=get_back_inline_keyboard()
        )
        await state.set_state(States.MY_SESSIONS)


    except Exception as e:
        logging.error(f"❌ Ошибка: {e}", exc_info=True)
        await callback.message.answer(f"⚠️ Ошибка при получении сессий: {e}")


@router.callback_query(States.MY_SESSIONS, F.data == 'to-back')
async def go_back(callback: CallbackQuery, chat_handler: ChatHistoryHandler, rest: RestHandler, state: FSMContext,
                  command: CommandObject | None = None):
    await chat_handler.delete_messages(callback.message.chat.id)
    await get_start(callback.message, rest, state, chat_handler, command)
