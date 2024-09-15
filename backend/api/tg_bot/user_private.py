from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import json
from asgiref.sync import sync_to_async
import requests
import api.tg_bot.reply as kb
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import LabeledPrice, PreCheckoutQuery, SuccessfulPayment, ContentType
from aiogram.utils.i18n import gettext as _
from api.tg_bot.classes_functions import Admin
from aiogram import Bot
from api.tg_bot.database import  *
user_private = Router()
from os import getenv, environ
from dotenv import load_dotenv
from aiogram.methods.get_user_profile_photos import GetUserProfilePhotos
import uuid
from api.models import User, Admins, Booked, Halls, Foods, Goods, Services, Notify,WebAppData, Presents
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
import aiohttp
import os
from pathlib import Path
from datetime import datetime
from yookassa import Configuration, Payment

Configuration.account_id = '444865'
Configuration.secret_key = 'test_nI8QUkSZ2iv-HYfnk40r37LBxmSZpev44ko2xCsH0Jo' 

load_dotenv()

bot = Bot(getenv('bot_token'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def get_summa(data_id):
    order_data = await get_web_data_all(data_id=data_id)
    order = order_data[0]['order_data']['Order']
    
    total_sum = 0
    discount = 0

    # Расчет стоимости зала
    if 'halls' in order['info']:
        for hall_id, hall_info in order['info']['halls'].items():
            hall_hours = int(hall_info['hours'])
            hall_obj = await sync_to_async(Halls.objects.get)(id=hall_id)
            hall_price_per_hour = hall_obj.price  
            hall_total = hall_hours * hall_price_per_hour

            # Определяем скидку в зависимости от количества часов
            if hall_hours >= 6:
                discount = 15
            elif hall_hours == 5:
                discount = 12
            elif hall_hours == 4:
                discount = 9
            elif hall_hours == 3:
                discount = 7
            else:
                discount = 0

            total_sum += hall_total

    # Расчет стоимости еды
    if 'foods' in order['info']:
        for food_id, food_info in order['info']['foods'].items():
            food_obj = await sync_to_async(Foods.objects.get)(id=food_id)
            food_price = food_obj.price
            food_quantity = int(food_info['quantity'])
            total_sum += food_price * food_quantity

    # Расчет стоимости услуг
    if 'services' in order['info']:
        for service_id, service_info in order['info']['services'].items():
            service_obj = await sync_to_async(Services.objects.get)(id=service_id)
            service_price = service_obj.price
            service_quantity = int(service_info['quantity'])
            total_sum += service_price * service_quantity

    # Расчет стоимости товаров
    if 'goods' in order['info']:
        for goods_id, goods_info in order['info']['goods'].items():
            goods_obj = await sync_to_async(Goods.objects.get)(id=goods_id)
            goods_price = goods_obj.price
            goods_quantity = int(goods_info['quantity'])
            total_sum += goods_price * goods_quantity
    # Применяем скидку ко всей корзине
    total_sum_with_discount = total_sum - (total_sum * discount / 100)
   
    return total_sum_with_discount, discount

def create(prices,chat_id):
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
            "amount": {
                "value": f"{prices}",
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "capture":True,
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/Vikingrznbot"
            },
            "metadata": {
                "chat_id": chat_id,
            },
            "description": f"Заказ в VIKING"
        },  idempotence_key)

        
    
    confirmation_url = payment.confirmation.confirmation_url

    return confirmation_url , payment.id

def check(payment_id):
    payment = Payment.find_one(payment_id)

    if payment.status == 'succeeded':
        return False
    else:
        return payment.metadata



@user_private.message(CommandStart())
async def start_message(message: Message, bot: Bot):
    UserProfilePhotos = await bot.get_user_profile_photos(user_id=message.from_user.id)
    file_id = 0
    if UserProfilePhotos.total_count > 0:
        # Извлекаем `file_id` первой фотографии
        first_photo = UserProfilePhotos.photos[0][0]
        file_id = first_photo.file_id
        
        # Сформируем URL для получения фотографии
        file = await bot.get_file(file_id=file_id)
        file_path = file.file_path
        file_url = f'https://api.telegram.org/file/bot{bot.token}/{file_path}'
        
        # Путь для сохранения фотографии
        save_path = Path('static/media/users') / f'{file_id}.webp'
        save_path.parent.mkdir(parents=True, exist_ok=True)  # Создаем папку, если она не существует
        
        # Скачиваем и сохраняем фотографию
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                if response.status == 200:
                    with open(save_path, 'wb') as f:
                        f.write(await response.read())


    user_reg = await add_user_data(user_id=message.from_user.id, photo=f'{file_id}.webp', username=message.from_user.username, first_name=message.from_user.first_name )

    if user_reg:
        await message.answer('⚔️ Премиальные караоке-бани «Viking»\n'
                            '\n'
                            'Наш официальный бот поможет:\n'
                            '\n'
                            '—  Посмотреть цены на залы, товары и услуги\n'
                            '—  Сделать онлайн-бронь\n'
                            '—  Получать напоминания о записях\n'
                            '\n'
                            '📍 Ул. Кутузова 15\n'
                            '\n'
                            'Нажмите «Начать», чтобы открыть приложение!' ,reply_markup=kb.start_inline(True))
    else:
        await message.answer('⚔️ Премиальные караоке-бани «Viking»\n'
                            '\n'
                            'Наш официальный бот поможет:\n'
                            '\n'
                            '—  Посмотреть цены на залы, товары и услуги\n'
                            '—  Сделать онлайн-бронь\n'
                            '—  Получать напоминания о записях\n'
                            '\n'
                            '📍 Ул. Кутузова 15\n'
                            '\n'
                            'Нажмите «Начать», чтобы открыть приложение!' ,reply_markup=kb.start_inline(False))


@user_private.callback_query(F.data.startswith("pay_"))
async def order_delivered_point(callback: CallbackQuery):
    data_id = callback.data.split("_")[1]
    n = await get_web_data_all(data_id=data_id)
    summa, discount = await get_summa(data_id)
    tg_id = n[0]['order_data']['Order']['user']['tg_id']
    summa = summa
    tg_id = int(tg_id)
    confirmation_url,pay_id = create(summa, tg_id)


    await callback.message.edit_text(f'Оплатите заказ по ссылке ниже',reply_markup=kb.get_pay(confirmation_url, summa, pay_id, data_id))

# Функция для расчета скидки на основе количества часов аренды
def calculate_discount(hours):
    discount = 0
    if hours >= 6:
        discount = 15
    elif hours == 5:
        discount = 12
    elif hours == 4:
        discount = 9
    elif hours == 3:
        discount = 7
    return discount

async def add_present_to_cart(user: User):
    """Функция для добавления подарка пользователю, если он еще его не получил."""
    if not user.got_present:
        present = await sync_to_async(Presents.objects.first)()  # Получаем первый подарок
        if present:
            present_item = {
                'id': present.present.id,
                'name': present.present.name,
                'quantity': 1,
                'price': 0  # Бесплатный подарок
            }

            if not user.data:
                user.data = {'food': {}}
            
            # Добавляем подарок в корзину
            user.data['food'][str(present.present.id)] = present_item
            user.got_present = True
            await sync_to_async(user.save)()  # Сохраняем изменения

            return present_item

# Функция для получения данных о заказе и расчета суммы с учетом скидки
@user_private.callback_query(F.data.startswith("pay_"))
async def order_delivered_point(callback: CallbackQuery):
    data_id = callback.data.split("_")[1]

    order_data = await get_web_data_all(data_id=data_id)
    order = order_data[0]['order_data']['Order']
    
    total_sum = 0
    

    tg_id = order['user']['tg_id']
    # Ищем пользователя в базе данных по tg_id
    user = await sync_to_async(User.objects.get)(tg_id=tg_id)

    # Проверяем статус пользователя и добавляем подарок, если его еще нет
    if not user.got_present:
        item = await add_present_to_cart(user)

    if 'halls' in order['info']:
        for hall_id, hall_info in order['info']['halls'].items():
            hall_hours = int(hall_info['hours'])
            hall_obj = await sync_to_async(Halls.objects.get)(id=hall_id)
            hall_price_per_hour = hall_obj.price  
            hall_total = hall_hours * hall_price_per_hour
            discount = calculate_discount(hall_hours)
            hall_total_with_discount = hall_total - (hall_total * discount / 100)
            total_sum += hall_total_with_discount
    
    if 'food' in order['info']:
        for food_id, food_info in order['info']['food'].items():
            food_obj = await sync_to_async(Foods.objects.get)(id=food_id) 
            food_price = food_obj.price
            food_quantity = int(food_info['quantity'])
            total_sum += food_price * food_quantity
    
    if 'services' in order['info']:
        for service_id, service_info in order['info']['services'].items():
            service_obj = await sync_to_async(Services.objects.get)(id=service_id)  
            service_price = service_obj.price
            service_quantity = int(service_info['quantity'])
            total_sum += service_price * service_quantity
    
    if 'goods' in order['info']:
        for goods_id, goods_info in order['info']['goods'].items():
            goods_obj = await sync_to_async(Goods.objects.get)(id=goods_id)  
            goods_price = goods_obj.price
            goods_quantity = int(goods_info['quantity'])
            total_sum += goods_price * goods_quantity


    tg_id = int(tg_id)
    
    # Создаем ссылку для оплаты
    confirmation_url, pay_id = create(total_sum, tg_id)
    
    

    await callback.message.edit_text(f'Оплатите заказ по ссылке ниже',reply_markup=kb.get_pay(confirmation_url, total_sum, pay_id, data_id))
@user_private.callback_query(F.data.startswith('check_'))
async def check_it(callback: CallbackQuery):
    tg_id = callback.from_user.id
    result = check(callback.data.split('_')[-1])
    order_id = callback.data.split('_')[-2]

    await callback.answer()

    if result:
        await callback.message.answer('Ошибка')
    else:
        # Отправка уведомления в чат о новой брони
        order_data = await get_web_data_all(order_id)
        if order_data:
            order_info = order_data[0]['order_data']
            username = callback.from_user.username
            phone_number = order_info['Order']['user']['phone']

            summa, discount = await get_summa(order_id)
            
            hall_info = order_info["Order"]["info"]["halls"]
            hall_id = list(hall_info.keys())[0]
            hall_name = hall_info[hall_id]["name"]
            hall_datetime = hall_info[hall_id]["datetime"]
            hall_hours = hall_info[hall_id]["hours"]
            
            additional_items = []
            if 'foods' in order_info["Order"]["info"]:
                food_items = order_info["Order"]["info"]["foods"].values()
                for food in food_items:
                    additional_items.append(f'{food["name"]} ({food["weight"]} г.) — {food["price"]}₽ x {food["quantity"]}')
            if 'services' in order_info["Order"]["info"]:
                service_items = order_info["Order"]["info"]["services"].values()
                for service in service_items:
                    additional_items.append(f'{service["name"]} ({service["time"]} мин.) — {service["price"]}₽')
            if 'goods' in order_info["Order"]["info"]:
                goods_items = order_info["Order"]["info"]["goods"].values()
                for goods in goods_items:
                    additional_items.append(f'{goods["name"]} ({goods["weight"]} мл.) — {goods["price"]}₽ x {goods["quantity"]}')

            additional_items_str = "\n".join(f"{i+1}. {item}" for i, item in enumerate(additional_items))

            notify_text = (
                f'🆕 Новая бронь от @{username}\n\n'
                f'Выбранный зал: {hall_name}\n'
                f'Дата: {hall_datetime}\n'
                f'Количество часов: {hall_hours}\n'
                f'Телефон: {phone_number}\n\n'
                f'Дополнительно:\n'
                f'{additional_items_str}\n\n'
                f'💳 Итоговая стоимость: {summa} ₽ (скидка {discount}%)'
            )

            await order_notify(-4500825826, notify_text)

            # Создание записи в Booked и History через асинхронную функцию
            await create_history(
                hall_id=hall_id,
                user_id=tg_id,
                book_time_str=hall_datetime,
                booking_time=hall_hours,
                order_data=order_data
            )

            await callback.message.edit_text(
                '✅ Спасибо за покупку! Я буду \n'
                'присылать тебе уведомления \n'
                'об изменениях статуса заказа'
            )