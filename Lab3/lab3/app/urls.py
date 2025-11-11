from django.urls import path
from .views import *

urlpatterns = [
    path('api/tariffs/', search_tariffs),  # GET
    path('api/tariffs/<int:tariff_id>/', get_tariff_by_id),  # GET
    path('api/tariffs/<int:tariff_id>/update/', update_tariff),  # PUT
    path('api/tariffs/<int:tariff_id>/update_image/', update_tariff_image),  # POST
    path('api/tariffs/<int:tariff_id>/delete/', delete_tariff),  # DELETE
    path('api/tariffs/create/', create_tariff),  # POST
    path('api/tariffs/<int:tariff_id>/add_to_forecastCloudPrice/', add_tariff_to_forecastCloudPrice),  # POST

    path('api/forecastCloudPrices/', search_forecastCloudPrices),  # GET
    path('api/forecastCloudPrices/cart/', get_cart_info),  # GET
    path('api/forecastCloudPrices/<int:forecastCloudPrice_id>/', get_forecastCloudPrice_by_id),  # GET
    path('api/forecastCloudPrices/<int:forecastCloudPrice_id>/update/', update_forecastCloudPrice),  # PUT
    path('api/forecastCloudPrices/<int:forecastCloudPrice_id>/update_status_user/', update_status_user),  # PUT
    path('api/forecastCloudPrices/<int:forecastCloudPrice_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/forecastCloudPrices/<int:forecastCloudPrice_id>/delete/', delete_forecastCloudPrice),  # DELETE

    path('api/forecastCloudPrices/<int:forecastCloudPrice_id>/update_tariff/<int:tariff_id>/', update_tariff_in_forecastCloudPrice),  # PUT
    path('api/forecastCloudPrices/<int:forecastCloudPrice_id>/delete_tariff/<int:tariff_id>/', delete_tariff_from_forecastCloudPrice),  # DELETE

    path('api/users/register/', register), # POST
    path('api/users/update/', update_user), # PUT
    path("api/users/info/", user_info), # GET
    path('api/users/login/', login), # POST
    path('api/users/logout/', logout), # POST
]
