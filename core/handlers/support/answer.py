from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo
from aiogram.fsm.context import FSMContext
import logging
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import StorageKey
from core.utils import RestHandler
from aiogram.filters import Command

from core.utils.redis_client import redis

router = Router()


@router.message(Command("ответ"), F.chat.type == "supergroup", F.message_thread_id)
async def handle_answer_command(message: Message, state: FSMContext):
    topic_id = await redis.get(f"session:group_to_topic:{message.chat.id}")
    group_chat_id = await redis.get(f"session:topic_to_group:{message.message_thread_id}")

    if not group_chat_id:
        return await message.reply("❌ Не удалось найти объект, связанный с этим топиком.")

    # Аккуратно удаляем команду "/ответ"
    text = message.caption or message.text or ""
    # print(f"TEXT:{message}")
    if text.startswith("/ответ"):
        text = text.replace("/ответ", "", 1).strip()

    # ======================== ОБРАБОТКА С МЕДИА ========================
    media_group = []

    # Фото
    if message.photo:
        largest_photo = message.photo[-1]  # Берём самое большое фото
        media_group.append(
            InputMediaPhoto(
                media=largest_photo.file_id,
                caption=f"📷 Фото от саппорта\n{text}" if text else "📷 Фото от саппорта"
            )
        )

    # Видео
    if message.video:
        media_group.append(
            InputMediaVideo(
                media=message.video.file_id,
                caption=f"🎥 Видео от саппорта\n{text}" if text else "🎥 Видео от саппорта"
            )
        )

    if media_group:
        await message.bot.send_media_group(
            chat_id=int(group_chat_id),
            media=media_group
        )
        await message.reply("✅ Медиа отправлено объекту.")
        return

    # Голосовое сообщение
    if message.voice:
        await message.bot.send_voice(
            chat_id=int(group_chat_id),
            voice=message.voice.file_id,
            caption=f"🎤 Голосовое сообщение от саппорта\n{text}" if text else "🎤 Голосовое сообщение от саппорта"
        )
        await message.reply("✅ Голосовое сообщение отправлено объекту.")
        return

    # Видео-записка
    if message.video_note:
        await message.bot.send_video_note(
            chat_id=int(group_chat_id),
            video_note=message.video_note.file_id
        )
        await message.reply("✅ Видео-записка отправлена объекту.")
        return

    # Только текст
    if text:
        await message.bot.send_message(
            chat_id=int(group_chat_id),
            text=f"📨 Ответ от саппорта:\n{text}"
        )
        await message.reply("✅ Ответ отправлен объекту.")
        return

    # Если ничего не подошло
    await message.reply("⚠️ Не удалось определить тип сообщения.")
