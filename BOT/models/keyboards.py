from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)


main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Помощь')],
                                     [KeyboardButton(text='Найти мем')],
                                     [KeyboardButton(text='Избранное')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')

search_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Назад')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Введите запрос или нажмите «Назад»...'
)

not_found_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Ввести новый запрос',
                callback_data='new_query'
            )
        ]
    ]
)