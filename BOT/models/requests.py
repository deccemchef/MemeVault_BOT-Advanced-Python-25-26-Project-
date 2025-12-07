from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


router = Router()

class MemeSearchState(StatesGroup):
    waiting_for_query = State()


def generate_ngrams(words):
    """
    Принимает список слов и возвращает все возможные фразы
    из подряд идущих слов: все 1-словные, 2-словные, ..., n-словные.
    """
    ngrams = []
    n = len(words)
    for start in range(n):
        for end in range(start + 1, n + 1):
            ngrams.append(" ".join(words[start:end]))
    return ngrams



@router.message(Command("memes"))
async def memes_start(message: Message, state: FSMContext):
    await message.answer("Введите текст запроса:")
    await state.set_state(MemeSearchState.waiting_for_query)



@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    # Проверяем, есть ли состояние
    current_state = await state.get_state()

    if current_state is None:
        await message.answer("Нет активного действия. Нечего отменять.")
        return

    # Очищаем состояние
    await state.clear()
    await message.answer("Действие отменено.")


#пользователь вводит текст

@router.message(MemeSearchState.waiting_for_query, F.text)
async def memes_get_query(message: Message, state: FSMContext):
    query = message.text.strip()

    # Разбиваем текст на слова
    words = query.split()

    ngrams = generate_ngrams(words)

    # Выводим в консоль
    print("Слова:", words)
    print("N-граммы:", ngrams)

    # Ответ пользователю
    await message.answer("Поиск мемов...")

    # Завершаем состояние
    await state.clear()
