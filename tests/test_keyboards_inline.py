from BOT.keyboards import inline as kb
from aiogram.types import InlineKeyboardMarkup


def test_pick_number_kb_creates_markup():
    markup = kb.pick_number_kb(3, batch_id=42)
    assert isinstance(markup, InlineKeyboardMarkup)

    buttons = [btn for row in markup.inline_keyboard for btn in row]

    texts = [b.text for b in buttons]
    assert {"1", "2", "3"}.issubset(set(texts))

    number_buttons = [b for b in buttons if b.text in {"1", "2", "3"}]
    assert all("42" in (b.callback_data or "") for b in number_buttons)

    assert any("Отмена" in (t or "") for t in texts)


def test_fav_delete_number_kb_creates_markup():
    try:
        markup = kb.fav_delete_number_kb(2)
    except TypeError:
        markup = kb.fav_delete_number_kb(2, batch_id=99)

    assert isinstance(markup, InlineKeyboardMarkup)

    buttons = [btn for row in markup.inline_keyboard for btn in row]
    texts = [b.text for b in buttons]

    assert {"1", "2"}.issubset(set(texts))
    assert any("Отмена" in (t or "") for t in texts)
