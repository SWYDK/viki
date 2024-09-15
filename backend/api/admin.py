
from django.contrib import admin
from .models import User, Halls, Foods, Booked, Admins, Goods, Services, Notify, WebAppData, History, Support, FiltersData, Presents
from django.contrib.auth.models import Group

admin.site.unregister(Group)

admin.site.register(User)
admin.site.register(Halls)
admin.site.register(Foods)
admin.site.register(Booked)
admin.site.register(Admins)
admin.site.register(Goods)
admin.site.register(Services)

admin.site.register(Notify)
admin.site.register(WebAppData)
admin.site.register(History)
admin.site.register(Support)
admin.site.register(FiltersData)
admin.site.register(Presents)






