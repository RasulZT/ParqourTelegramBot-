from aiogram import Router, F
from aiogram.types import Message

router = Router()


# @router.message(F.chat.type.in_({"group", "supergroup"}))
# async def handle_group_message(message: Message):
#     print(f"📩 Сообщение из группы: {message.chat.id}")
