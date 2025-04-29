import logging
from core.utils.RestHandler import RestHandler
from core.handlers.websocket.new_ticket import send_new_ticket_to_role
from aiogram import Bot, Router, F
from core.models.ticket import Ticket,TicketSerializer
from core.utils.ChatHistoryHandler import ChatHistoryHandler


rest = RestHandler()
serializer = TicketSerializer()


async def ticket_main(bot: Bot, message_history: ChatHistoryHandler,
                     request: Ticket):
    try:

        if request.section == "NEW":
            await send_new_ticket_to_role(request, bot ,'support',message_history)
    except Exception as e:
        logging.error(f"Error order_main: {e}")
