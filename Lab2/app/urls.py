from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('tariffs/<int:tariff_id>/', tariff_page, name="tariff_page"),
    path('forecasts/<int:forecast_id>/', forecast_page, name="forecast_page"),
    path('tariffs/<int:tariff_id>/add_to_forecast/', add_tariff_to_draft_forecast, name="add_tariff_to_draft_forecast"),
    path('forecasts/<int:forecast_id>/delete/', delete_forecast, name="delete_forecast")
]
