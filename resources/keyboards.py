from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.database import get_book_data


async def creating_book_kb() -> InlineKeyboardBuilder:
    """
    Асинхронная функция для создания встроенной клавиатуры (Inline Keyboard) с кнопками,
    представляющими книги.
    """
    books_data = await get_book_data()

    books_btns = []

    for item in books_data:
        btn_books = InlineKeyboardButton(text=f'{item[1]}', callback_data=f'book_id_{item[0]}')
        books_btns.append(btn_books)

    books_kb = InlineKeyboardBuilder()
    books_kb.add(*books_btns)
    books_kb.adjust(1)

    return books_kb