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

search_controls_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="▶️ Следующие мемы",
                callback_data="search:next"
            )
        ],
        [
            InlineKeyboardButton(
                text="⭐ Добавить в избранное",
                callback_data="search:fav"
            )
        ]
    ]
)

favourites_manage_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🗑 Удалить мемчик",
                callback_data="favourites:delete_menu"
            )
        ]
    ]
)


def pick_number_kb(n: int) -> InlineKeyboardMarkup:
    n = max(1, min(n, 6))
    buttons = [InlineKeyboardButton(text=str(i), callback_data=f"search:add:{i}") for i in range(1, n + 1)]
    rows = [buttons[:3], buttons[3:]] if n > 3 else [buttons]
    rows.append([InlineKeyboardButton(text="Отмена", callback_data="search:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
