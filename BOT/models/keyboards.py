from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)


main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Помощь')],
                                     [KeyboardButton(text='Найти мем')],
                                     [KeyboardButton(text='Избранное')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')