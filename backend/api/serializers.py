from rest_framework import serializers
from .models import (User, Halls, Foods, Booked, Services, Goods, SMS, WebAppData, History, Support, FiltersData, Presents)


class HallsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Halls
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    hall = serializers.PrimaryKeyRelatedField(queryset=Halls.objects.all(), required=False, allow_null=True)
    class Meta:
        model = User
        fields = ['id', 'tg_id', 'tg_username','photo', 'name', 'phone_number', 'reg_date', 'isActive', 'user_theme', 'hall', 'book_time', 'booking_time', 'data','got_present']


class FoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foods
        fields = '__all__'


class BookedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booked
        fields = '__all__'


class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = '__all__'


class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = '__all__'
        
class SMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMS
        fields = '__all__'


class WebAppDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebAppData
        fields = '__all__'

class SupportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Support
        fields = '__all__'
    
class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'

class FiltersDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = FiltersData
        fields = '__all__'
    
class PresentsSerializer(serializers.ModelSerializer):
    present = FoodsSerializer()
    
    class Meta:
        model = Presents
        fields = '__all__'