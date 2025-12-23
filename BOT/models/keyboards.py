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


def search_controls_kb(batch_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Добавить в избранное", callback_data=f"search:fav:{batch_id}")],
            [InlineKeyboardButton(text="🔁 Еще мемы", callback_data="search:more")],
        ]
    )


favourites_manage_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🗑 Удалить мемчик",
                callback_data="favourites:delete_menu"
            )
        ],
        [
            InlineKeyboardButton(
                text="🧹 Очистить избранное",
                callback_data="favourites:clear_ask"
            )
        ]
    ]
)

favourites_clear_confirm_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, очистить", callback_data="favourites:clear_confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="favourites:clear_cancel")],
    ]
)


def pick_number_kb(n: int, batch_id: str) -> InlineKeyboardMarkup:
    n = max(1, min(n, 10))
    buttons = [
        InlineKeyboardButton(text=str(i), callback_data=f"search:add:{batch_id}:{i}")
        for i in range(1, n + 1)
    ]
    rows = [buttons[:3], buttons[3:]] if n > 3 else [buttons]
    rows.append([InlineKeyboardButton(text="Отмена", callback_data=f"search:cancel:{batch_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def fav_delete_number_kb(n: int) -> InlineKeyboardMarkup:
    n = max(1, min(n, 10))
    buttons = [
        InlineKeyboardButton(text=str(i), callback_data=f"fav:del:{i}")
        for i in range(1, n + 1)
    ]

    rows = []
    for i in range(0, len(buttons), 5):
        rows.append(buttons[i:i + 5])

    rows.append([InlineKeyboardButton(text="Отмена", callback_data="fav:del_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def fav_delete_kb(meme_ids: list[int]) -> InlineKeyboardMarkup:
    meme_ids = meme_ids[:10]
    buttons = [
        InlineKeyboardButton(text=str(i), callback_data=f"favourites:del:{meme_id}")
        for i, meme_id in enumerate(meme_ids, start=1)
    ]

    rows = []
    for i in range(0, len(buttons), 5):
        rows.append(buttons[i:i + 5])

    rows.append([InlineKeyboardButton(text="Отмена", callback_data="favourites:del_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
