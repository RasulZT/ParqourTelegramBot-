import logging
from core.utils.RestHandler import RestHandler
from core.handlers.websocket.new_ticket import send_new_ticket_to_role
from aiogram import Bot, Router, F
from core.models.ticket import Ticket, TicketSerializer
from core.utils.ChatHistoryHandler import ChatHistoryHandler
from core.utils.redis_client import redis

rest = RestHandler()
serializer = TicketSerializer()


# async def cleanup_orphaned_topics():
#     session_keys = await redis.keys("session:topic_to_group:*")
#     deleted = 0
#
#     for key in session_keys:
#         topic_id = key.split(":")[-1]
#         ticket_keys = await redis.keys("ticket:topic_id:*")
#
#         topic_is_used = False
#         for t_key in ticket_keys:
#             used_topic_id = await redis.get(t_key)
#             if used_topic_id == topic_id:
#                 topic_is_used = True
#                 break
#
#         if not topic_is_used:
#             await redis.delete(key)
#             deleted += 1
#             print(f"🧹 Удалено: {key}")
#
#     print(f"✅ Завершено. Удалено {deleted} ключей.")


async def handle_ticket_closed(ticket_id: int, bot: Bot, message_history: ChatHistoryHandler):
    GROUP_ID = -1002571604070

    topic_id = await redis.get(f"ticket:topic_id:{ticket_id}")
    if not topic_id:
        logging.warning(f"⚠️ Топик не найден в Redis для тикета #{ticket_id}")
        return

    # Отправляем сообщение о завершении
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            text=f"✅ Тикет #{ticket_id} был завершён.",
        )
    except Exception as e:
        logging.warning(f"❗ Не удалось отправить сообщение о завершении тикета #{ticket_id}: {e}")

    # Удаляем сам топик
    try:
        await bot.delete_forum_topic(
            chat_id=GROUP_ID,
            message_thread_id=int(topic_id)
        )
    except Exception as e:
        logging.warning(f"❗ Не удалось удалить топик #{topic_id} для тикета #{ticket_id}: {e}")

    # Получаем связанную группу
    group_chat_id = await redis.get(f"session:topic_to_group:{topic_id}")
    if not group_chat_id:
        logging.warning(f"⚠️ Связь topic_to_group не найдена для топика #{topic_id}")

    # Удаляем всё из Redis
    await redis.delete(f"ticket:topic_id:{ticket_id}")
    await redis.delete(f"session:topic_to_group:{topic_id}")
    if group_chat_id:
        await redis.delete(f"session:group_to_topic:{group_chat_id}")



async def ticket_delete(bot: Bot, message_history: ChatHistoryHandler,
                        request):
    try:

        await handle_ticket_closed(request.id, bot, message_history)



    except Exception as e:
        logging.error(f"Error order_main: {e}")
