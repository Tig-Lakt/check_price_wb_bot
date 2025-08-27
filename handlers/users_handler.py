import logging
from aiogram import types
from aiogram import Router, F

from database.database import get_book_price
from resources import creating_book_kb, images


logger = logging.getLogger("wb_check_price_bot.handlers.users")
router = Router()
    
    
@router.callback_query(F.data.startswith('book_id_'))
async def f_book_id(callback: types.CallbackQuery):
    """
    Обработчик callback запросов для получения цены книги.
    
    Args:
        callback (types.CallbackQuery): Callback запрос от инлайн-кнопки
    """
    try:
        
        await callback.message.delete()
        
        # Извлечение ID книги из callback данных
        book_id = callback.data[8:]
        
        # Получение данные о книге из базы данных
        book_data = await get_book_price(int(book_id))
        
        if not book_data:
            logger.warning("Данные о книге не найдены для book_id: %s", book_id)
            await callback.message.answer("Информация о книге не найдена")
            return
            
        # Формирование текст сообщения в зависимости от наличия книги
        if book_data[0]['price'] == 'Нет в наличии':
            msg_text = '<b>Выбранной книги нет в наличии</b>'
            logger.info(
                "Книга %s отсутствует в наличии (пользователь: %s)",
                book_data[0]['book_name'], callback.from_user.full_name
            )
        else: 
            msg_text = f"""
            Стоимость книги <b>{book_data[0]['book_name']}</b> составляет <b>{book_data[0]['price']}₽</b>
            """

        img = images.get(book_id)
        kb = await creating_book_kb()
        
        # Отправка сообщения с фото и информацией о книге
        await callback.message.answer_photo(
            photo=img,
            caption=msg_text,
            reply_markup=kb.as_markup(resize_keyboard=True)
        )
        
    except ValueError as e:
        logger.error(
            "Ошибка преобразования book_id: %s, данные: %s, пользователь: %s",
            e, callback.data, callback.from_user.full_name,
            exc_info=True
        )
        await callback.message.answer("Ошибка обработки запроса")
        await callback.answer()
        
    except Exception as e:
        logger.error(
            "Неожиданная ошибка при обработке callback: %s, данные: %s, пользователь: %s",
            e, callback.data, callback.from_user.full_name,
            exc_info=True
        )
        await callback.message.answer("Произошла ошибка. Попробуйте позже.")
        await callback.answer()