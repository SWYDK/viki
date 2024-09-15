from asgiref.sync import sync_to_async
from api.models import User, Admins, Booked, Halls, Foods, Goods, Services, Notify,WebAppData, FiltersData,History
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Count
import json
@sync_to_async
def add_or_check_kitchen(msg):
    return FiltersData.objects.filter(tg_id=tg_id, msg=msg).count()

@sync_to_async
def add_user(user_id):
    if not User.objects.filter(tg_id=user_id).exists():
        user = User(tg_id=user_id)
        user.save()
        return True

    return False
@sync_to_async
def create_booking_record(hall_id, user_id, book_time, booking_time, order_data):
    hall = Halls.objects.get(id=hall_id)
    user = User.objects.get(tg_id=user_id)
    Booked.objects.create(
        hall=hall,
        user=user,
        book_time=book_time,
        booking_time=booking_time,
        order_data=order_data
    )
    return True

def parse_datetime(date_str):
    return datetime.strptime(date_str, "%d.%m.%y, %H:%M")

@sync_to_async
def create_history(hall_id, user_id, book_time_str, booking_time, order_data):
    hall = Halls.objects.get(id=hall_id)
    user = User.objects.get(tg_id=user_id)
    print(hall.photo[0])
    # Преобразуем строку в формат datetime
    book_time = parse_datetime(book_time_str)

    # Создаем запись в Booked
    booked = Booked.objects.create(
        hall=hall,
        user=user,
        book_time=book_time,
        booking_time=booking_time,
        order_data=order_data
    )

    # Создаем запись в History
    History.objects.create(
        user=user,
        photo=hall.photo[0],  # предполагается, что у пользователя есть фото
        max_people=hall.max_people,  # предполагается, что у зала есть максимальное количество человек
        name=hall.name,
        booked_time=book_time  # возможно, нужно преобразовать в DateField
    )

    return True
    
@sync_to_async
def add_user_data(user_id, photo, username, first_name):
    if not User.objects.filter(tg_id=user_id).exists():
        User.objects.create(
            tg_id=user_id,
            photo=photo,
            tg_username=username,
            name=first_name
        )
        return False
    return True
@sync_to_async
def get_foods():

    
    return list(Foods.objects.all())

@sync_to_async
def get_users():

    queryset = User.objects.all().values('tg_id')
    return len(list(queryset))

@sync_to_async
def get_msgs():

    queryset = Notify.objects.all().values('tg_id','msg')
    return list(queryset)
@sync_to_async
def order_notify(tg_id,text):
    return Notify.objects.create(tg_id=tg_id,msg=text)
@sync_to_async
def record_count(tg_id, msg):
    return Notify.objects.filter(tg_id=tg_id, msg=msg).count()
@sync_to_async
def delete_item(model, item_id):
    try:
        item = model.objects.get(id=item_id)
        item.delete()
        return True
    except model.DoesNotExist:
        return False
@sync_to_async
def get_web_data():
    queryset = WebAppData.objects.filter(is_viewed=False).values('id', 'order_data')
    return list(queryset)
    
@sync_to_async
def get_web_data_all(data_id):
    queryset = WebAppData.objects.filter(id=data_id).values('id', 'order_data')
    return list(queryset)

@sync_to_async
def view_web_data(data_id):
    order = WebAppData.objects.get(id=data_id)
    order.is_viewed = True
    order.save()

    return True    


@sync_to_async
def save_food(photo, weight, name, kitchen, compounds, status, price):
    return Foods.objects.create(
        photo=photo,
        weight=weight,
        name=name,
        kitchen=kitchen,
        compounds=compounds,
        status=status,
        price=price
    )

@sync_to_async
def delete_notifications(tg_id, msg):
    # Фильтруем записи по tg_id и msg
    records_to_delete = Notify.objects.filter(tg_id=tg_id, msg=msg)

    # Удаляем записи
    deleted_count, _ = records_to_delete.delete()

    return deleted_count

@sync_to_async
def delete_msgs(tg_ids):
    # Удаляем записи с указанными tg_id
    Notify.objects.filter(tg_id__in=tg_ids).delete()


@sync_to_async
def get_users_status():
    return User.objects.filter(isActive=True).count()

@sync_to_async
def get_users_status2():
    return User.objects.filter(isActive=False).count()

@sync_to_async
def get_users_post():
    queryset = User.objects.all().values('tg_id')
    return list(queryset)


@sync_to_async
def check_admin(user_id):
    if not Admins.objects.filter(tg_id=user_id).exists():
        return False
    return True


@sync_to_async
def get_total_bookings_count():
    return Booked.objects.count()

@sync_to_async
def get_today_bookings_count():
    today = timezone.now().date()
    return Booked.objects.filter(create_date__date=today).count()

@sync_to_async
def get_week_bookings_count():
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    return Booked.objects.filter(create_date__date__gte=week_start, create_date__date__lte=today).count()

@sync_to_async
def get_month_bookings_count():
    today = timezone.now().date()
    month_start = today.replace(day=1)
    return Booked.objects.filter(create_date__date__gte=month_start, create_date__date__lte=today).count()