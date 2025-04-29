from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder,InlineKeyboardBuilder



main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Каталог', callback_data='catalog')],
    [InlineKeyboardButton(text='Корзина', callback_data='basket'),
     InlineKeyboardButton(text='Контакты', callback_data='contacts')]
])

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='YouTube', url='https://youtube.com/@sudoteach')]
])

# testcallback = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text='Каталог', callback_data='catalog')],
#     [InlineKeyboardButton(text='Корзина', callback_data='basket'),
#      InlineKeyboardButton(text='Контакты', callback_data='contacts')]
# ])


tickets = ['Ticket1', 'Ticket2', 'Ticket3']

async def inline_cars():
    keyboard = ReplyKeyboardBuilder()
    for ticket in tickets:
        keyboard.add(KeyboardButton(text=ticket))
    return keyboard.adjust(2).as_markup()

async def inline_cars2():
    keyboard = InlineKeyboardBuilder()
    for car in tickets:
        keyboard.add(InlineKeyboardButton(text=car, callback_data=f'car_{car}'))
    return keyboard.adjust(2).as_markup()
