import logging
from aiogram import Bot, Router, F
from core.utils.ChatHistoryHandler import ChatHistoryHandler
from core.models.ticket import Ticket
from core.keyboards.inline import get_support_menu, get_support_ticket_inline_keyboard
from core.utils.fetch_users import fetch_users


async def send_new_ticket_to_role(ticket: Ticket, bot: Bot, role: str, message_history: ChatHistoryHandler):
    try:
        message_text = (
            f"📨 <b>------------------------Новый тикет #{ticket.id}------------------------</b>\n"
            f"📍 Паркинг: {ticket.parking.name}\n"
            f"📝 Описание:\n{ticket.description or '—'}\n\n"
        )

        GROUP_ID = -1002571604070


        sent_message = await bot.send_message(
            chat_id=GROUP_ID,
            text=message_text,
            parse_mode='HTML',
            reply_markup=get_support_ticket_inline_keyboard(ticket.id)
        )

        # Сохраняем по chat_id|ticket_id — один раз
        message_history.add_new_message(f'{GROUP_ID}|{ticket.id}', sent_message.message_id)

    except Exception as e:
        logging.error(f"New ticket error in group: {e}")

# async def new_ticket(bot: Bot, message_history: ChatHistoryHandler, ticket: Ticket):
#     try:
#         message_id = (await bot.send_message(int(ticket.user_id), f"Ваш заказ сохранен\n")).message_id
#         message_history.add_new_message(order.client_id, message_id)
#         await send_new_order_to_role(order.company_id, order.id, bot, 'manager', message_history)
#         await send_new_order_to_role(order.company_id, order.id, bot,  'admin', message_history)
#     except Exception as e:
#         logging.error(f"Error new_order: {e}")
