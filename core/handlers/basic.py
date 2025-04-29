import json
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
import core.keyboards.keyboards as kb
from core.utils.ChatHistoryHandler import ChatHistoryHandler
from core.utils.RestHandler import RestHandler
from rest_framework import response

from core.keyboards.inline import get_common_menu, get_support_menu, get_admin_menu
from core.utils.redis_client import redis

router = Router()


# Хендлер из группы объекта → в топик
@router.message(F.chat.type == "supergroup", ~F.message_thread_id)
async def redirect_to_topic(message: Message, state: FSMContext):
    MY_GROUP_ID = -1002571604070
    group_chat_id = message.chat.id
    topic_id = await redis.get(f"session:group_to_topic:{group_chat_id}")
    if not topic_id:
        await message.reply("⚠️ Топик для этого объекта не найден.")
        return

    if message.text:
        await message.bot.send_message(
            chat_id=MY_GROUP_ID,
            message_thread_id=topic_id,
            text=f"📩 Ответ от объекта:\n{message.text}"
        )

        # Фото
    elif message.photo:
        file_id = message.photo[-1].file_id  # лучшее качество
        await message.bot.send_photo(
            chat_id=MY_GROUP_ID,
            message_thread_id=topic_id,
            photo=file_id,
            caption="📷 Фото от объекта"
        )

        # Видео
    elif message.video:
        await message.bot.send_video(
            chat_id=MY_GROUP_ID,
            message_thread_id=topic_id,
            video=message.video.file_id,
            caption="🎥 Видео от объекта"
        )

        # Видео-заметка
    elif message.video_note:
        await message.bot.send_video_note(
            chat_id=MY_GROUP_ID,
            message_thread_id=topic_id,
            video_note=message.video_note.file_id
        )

        # Голосовое
    elif message.voice:
        await message.bot.send_voice(
            chat_id=MY_GROUP_ID,
            message_thread_id=topic_id,
            voice=message.voice.file_id,
            caption="🎤 Голосовое сообщение"
        )

    else:
        await message.reply("⚠️ Тип сообщения не поддерживается.")


@router.message(Command(commands=['start', 'run']))
async def _get_start(message: Message, command: CommandObject, rest: RestHandler,
                     state: FSMContext, chat_handler: ChatHistoryHandler):
    try:
        image = FSInputFile("public/assets/images/welcome.png")

        caption = (
            "<b>👋 Добро пожаловать в Parqour Support Bot</b>\n\n"
            "Этот бот помогает сотрудникам работать с заявками, чатами и сессиями.\n"
            "Выберите роль и начнём!"
        )

        await message.answer_photo(
            photo=image,
            caption=caption,
            reply_markup=get_common_menu(),
            parse_mode="HTML"
        )

        await get_start(message, rest, state, chat_handler, command)
    except Exception as e:
        logging.error(f"_get_start error: {e}")


# @router.message(Command(commands=['test']))
# async def test(message: Message):
#     logging.info(f"User_id: {message.chat.id}.")
#     logging.info(f"User_id: {message.model_dump_json(indent=2)}.")


async def get_start(
        message: Message,
        rest: RestHandler,
        state: FSMContext,
        chat_handler: ChatHistoryHandler,
        command: CommandObject | None = None,
        delete_previous_messages: bool = True
) -> None:
    try:
        logging.info("🔹 Старт обработки /start")

        payload = {
            'telegram_id': str(message.chat.id),
            'telegram_fullname': message.from_user.full_name,
        }
        logging.info(f"📤 Payload to [v1/auth/tgregister/]: {json.dumps(payload)}")

        # Первый запрос — регистрация
        try:
            user = await rest.post(url="v1/auth/tgregister/", data=payload)
        except Exception as e:
            logging.warning(f"⚠️ Ошибка при регистрации: {e}")
            user = None

        # Альтернативная регистрация, если получен список или ошибка
        if isinstance(user, list) or not user:
            payload['telegram_fullname'] = f"-telegram- {message.from_user.full_name}"
            payload['promo'] = ''
            logging.info(f"📤 Альтернативный payload [auth/register/]: {json.dumps(payload)}")
            user = await rest.post(url="auth/register/", data=payload)

        # Сохраняем пользователя в FSM
        await state.update_data(token=user.get("access"),
                                user=user,
                                role=user.get("role"))

        logging.info(f"✅ Пользователь зарегистрирован: {user}")

        if user["role"] == "support":
            await chat_handler.send_message(message=message, text=
            f"*🏠 Вы находитесь на главной странице сапорта компании*\n"
            f"_Для управления воспользуйтесь кнопками_",
                                            reply_markup=get_support_menu())

        if user["role"] == "admin":
            await chat_handler.send_message(message=message, text=
            f"*🏠 Вы находитесь на главной странице Админа компании*\n"
            f"_Для управления воспользуйтесь кнопками_",
                                            reply_markup=get_admin_menu())

    except Exception as e:
        logging.error(f"❌ Main function error: {e}", exc_info=True)

        # if user["role"] == "admin":
        #     await chat_handler.send_message(message,
        #                                     f"*🏠 Вы находитесь на главной странице админа компании*\n"
        #                                     f"_Чтобы увидеть заказы, воспользуйтесь кнопками_",
        #                                     reply_markup=get_manager_inline_keyboard())
        #
        # if user["role"] == "manager":
        #     await chat_handler.send_message(message,
        #                                     f"*🏠 Вы находитесь на главной странице менеджера*\n"
        #                                     f"_Чтобы увидеть заказы, воспользуйтесь кнопками_",
        #                                     reply_markup=get_manager_inline_keyboard())
        #
        # if user["role"] == "cook":
        #     await chat_handler.send_message(message,
        #                                     f"*🏠 Вы находитесь на главной странице повара*\n"
        #                                     f"_Чтобы увидеть заказы, воспользуйтесь кнопками_",
        #                                     reply_markup=get_manager_inline_keyboard())
        #
        # if user["role"] == "runner":
        #     await chat_handler.send_message(message,
        #                                     f"*🏠 Вы находитесь на главной странице с раздачей готовых заказов*\n"
        #                                     f"_Чтобы увидеть заказы, воспользуйтесь кнопками_",
        #                                     reply_markup=get_manager_inline_keyboard())
        #
        # if user["role"] == "client":
        #     await chat_handler.send_message(message,
        #                                     f"*Вы находитесь на главной странице* "
        #                                     f"{'' if user['telegram_fullname'] is None else user['telegram_fullname']}"
        #                                     f"!\n*В данный момент у вас:* {user['bonus']} бонусов!\n" +
        #                                     f"_При оформление заказа, вы сможете потратить эти бонусы_\n" +
        #                                     f"_Чтобы сделать предзаказ, воспользуйтесь кнопками._",
        #                                     reply_markup=get_main_inline_keyboard())
        #
        # if user["role"] == "delivery":
        #     await chat_handler.send_message(message,
        #                                     "*🏠 Вы находитесь на главной странице доставщика*\n"
        #                                     f"_Чтобы увидеть заказы, воспользуйтесь кнопками_",
        #                                     reply_markup=get_delivery_reply_keyboard())
        # logging.info(f"8")
    # except Exception as e:
    #     print(f"Main function error: {e}")

# @router.message(CommandStart())
# async def cmd_start(message: Message):
#     await message.answer(f'Привет, ID: {message.from_user.id}\n',reply_markup=  kb.main)
#
# @router.message(Command('help'))
# async def get_help(message: Message):
#     await message.answer('Это команда /help')
#
# @router.message(F.text == 'Как дела?')
# async def how_are_you(message: Message):
#     await message.answer('ОК!')
#
# @router.message(F.text == 'Как дела?')
# async def how_are_you(message: Message):
#     await message.answer('ОК!')
#
# @router.message(Command('get_photo'))
# async def get_photo(message: Message):
#     await message.answer_photo(
#         photo='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSw1-HFGXIZ1ZpK4-ksQiYXffU6xQelzNF6fA&s',
#         caption='Это лого ТГ'
#     )

# @router.message()
# async def debug_all_messages(message: Message):
#     print("DEBUG:", message)
