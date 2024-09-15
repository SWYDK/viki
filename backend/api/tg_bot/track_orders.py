from aiogram import Bot
from asgiref.sync import sync_to_async
from api.models import User, Admins, Booked, Halls, Foods, Goods, Services, Notify,WebAppData, Presents
from api.tg_bot.database import *
from api.tg_bot.user_private import *

import api.tg_bot.reply as kb
import re

# П
# Регулярное выражение для поиска номера заказа



async def notify_user(bot: Bot):
    n = await get_msgs()
    tg_ids_to_delete = []

    for el in n:
        msg = el['msg']
        tg_id = int(el['tg_id'])
        if el['tg_id'] == '-4500825826':
            await bot.send_message(chat_id=-4500825826, text=msg)
            tg_ids_to_delete.append(el['tg_id'])
        else:
            await bot.send_message(chat_id=int(el['tg_id']), text=msg)
            deleted_count = await delete_notifications(tg_id, msg)
            deleted_count = await delete_notifications(tg_id, msg)
            deleted_count = await delete_notifications(tg_id, msg)
            deleted_count = await delete_notifications(tg_id, msg)
            deleted_count = await delete_notifications(tg_id, msg)
            deleted_count = await delete_notifications(tg_id, msg)
            deleted_count = await delete_notifications(tg_id, msg)
            deleted_count = await delete_notifications(tg_id, msg)
            deleted_count = await delete_notifications(tg_id, msg)
            deleted_count = await delete_notifications(tg_id, msg)
            print(deleted_count)
            tg_ids_to_delete.append(el['tg_id'])
    await delete_msgs(tg_ids_to_delete)

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


async def getwebdata(bot):
    n = await get_web_data()
    tg_ids_to_delete = []

    for el in n:
        if 'id' not in el:
            print("Ошибка: поле 'id' отсутствует")
            continue  # Пропускаем элемент, если нет 'id'

        data_id = el['id']

        d = el['order_data']

        if isinstance(d, dict):
            parsed_data = d
        else:
            parsed_data = json.loads(d)

        # Получаем итоговую сумму и скидку для заказа
        summa, discount = await get_summa(data_id)

        # Извлекаем ID пользователя Telegram
        tg_id = parsed_data["Order"]["user"]["tg_id"]
        tg_id = int(tg_id)

        # Зал
        hall = list(parsed_data["Order"]["info"]["halls"].values())[0]
        hall_name = hall["name"]
        hall_datetime = hall["datetime"]
        hall_hours = hall["hours"]

        # Дополнительные товары, еда и услуги
        additional_items = []

        # Еда
        if 'foods' in parsed_data["Order"]["info"]:
            food_items = parsed_data["Order"]["info"]["foods"]
            for food_id, food in food_items.items():
                food_obj = await sync_to_async(Foods.objects.get)(id=food_id)  # Используем food_id как ID
                food_name = food_obj.name
                food_weight = food_obj.weight
                food_price = food_obj.price
                food_quantity = food['quantity']
                additional_items.append(f'{food_name} ({food_weight} г.) — {food_price}₽ x {food_quantity}')

        # Услуги
        if 'services' in parsed_data["Order"]["info"]:
            service_items = parsed_data["Order"]["info"]["services"]
            for service_id, service in service_items.items():
                service_obj = await sync_to_async(Services.objects.get)(id=service_id)  # Используем service_id как ID
                service_name = service_obj.name
                service_time = service_obj.time
                service_price = service_obj.price
                service_quantity = service['quantity']
                additional_items.append(f'{service_name} ({service_time} мин.) — {service_price}₽ x {service_quantity}')

        # Товары
        if 'goods' in parsed_data["Order"]["info"]:
            goods_items = parsed_data["Order"]["info"]["goods"]
            for goods_id, goods in goods_items.items():
                goods_obj = await sync_to_async(Goods.objects.get)(id=goods_id)  # Используем goods_id как ID
                goods_name = goods_obj.name
                goods_volume = goods_obj.weight
                goods_price = goods_obj.price
                goods_quantity = goods['quantity']
                additional_items.append(f'{goods_name} ({goods_volume} мл.) — {goods_price}₽ x {goods_quantity}')

        # Формируем строку с дополнительными товарами/услугами
        additional_items_str = "\n".join(f"{i+1}. {item}" for i, item in enumerate(additional_items))

        # Формируем сообщение
        message = (
            f'🛒 Ваш заказ\n'
            f'\n'
            f'Выбранный зал: {hall_name}\n'
            f'Дата: {hall_datetime}\n'
            f'Количество часов: {hall_hours}\n'
            f'\n'
            f'Дополнительно:\n'
            f'{additional_items_str}\n'
            f'\n'
            f'💳 Итоговая стоимость: {summa}₽ (скидка {discount}%)'
        )

        # Отправляем сообщение пользователю
        await bot.send_message(chat_id=int(tg_id), text=message, reply_markup=kb.check_order(data_id))

        # Помечаем данные как просмотренные
        await view_web_data(data_id)

    # Удаляем сообщения пользователей, если это необходимо
    await delete_msgs(tg_ids_to_delete)