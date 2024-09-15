# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (UserViewSet, HallsViewSet, FoodsViewSet, BookedViewSet, GoodsViewSet, 
ServicesViewSet, SMSViewSet, WebAppDataViewSet, HistoryViewSet, SupportViewSet, FiltersDataViewSet, PresentsViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'halls', HallsViewSet)
router.register(r'foods', FoodsViewSet)
router.register(r'booked', BookedViewSet)
router.register(r'goods', GoodsViewSet)
router.register(r'services', ServicesViewSet)
router.register(r'sms', SMSViewSet)
router.register(r'webappdata', WebAppDataViewSet)

router.register(r'history', HistoryViewSet)
router.register(r'support', SupportViewSet)
router.register(r'filters', FiltersDataViewSet)
router.register(r'presents', PresentsViewSet)



urlpatterns = [
    path('', include(router.urls)),
]
