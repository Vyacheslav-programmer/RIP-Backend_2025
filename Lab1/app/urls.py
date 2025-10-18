from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('tariffs/<int:tariff_id>/', tariff_page),
    path('calculations/<int:calculation_id>/', calculation_page),
]