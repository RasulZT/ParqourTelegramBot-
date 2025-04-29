import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_common_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📄 Мои данные", callback_data="common:my_data")
    kb.button(text="📇 Контакты", callback_data="common:contacts")
    return kb.as_markup()


def get_support_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📅 Мои сессии", callback_data="support:my_sessions")
    kb.button(text="🧑‍💼 Сотрудники", callback_data="support:staff_info")
    kb.button(text="✅ Завершённые", callback_data="support:done")
    return kb.as_markup()


def get_admin_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Все сессии", callback_data="admin:all_sessions")
    kb.button(text="👥 Все саппорты", callback_data="admin:all_supports")
    kb.button(text="🕘 История", callback_data="admin:history")
    return kb.as_markup()


def get_back_inline_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='🔙 На главную', callback_data='to-back')

    return keyboard_builder.as_markup(
        input_field_placeholder='⏬ Нажмите кнопку, чтобы перейти на главную страницу',
        resize_keyboard=True,
        # one_time_keyboard=True
    )


def get_support_ticket_inline_keyboard(ticket_id: str | int):
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(
        text='Взять тикет',
        callback_data=f'open_ticket:{ticket_id}'  # обязательно!
    )

    return keyboard_builder.as_markup()