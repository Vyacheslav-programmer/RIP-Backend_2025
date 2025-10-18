import uuid
from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .calc import calc
from .permissions import IsModerator, IsAuthenticated, IsBuyer
from .redis import session_storage
from .serializers import *
from .utils import get_session, get_draft_forecastCloudPrice, identity_user


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'tariff_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_tariffs(request):
    tariff_name = request.GET.get("tariff_name", "")

    tariffs = Tariff.objects.filter(status=1)
    if tariff_name:
        tariffs = tariffs.filter(name__icontains=tariff_name)

    serializer = TariffsSerializer(tariffs, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_tariff_by_id(request, tariff_id):
    if not Tariff.objects.filter(pk=tariff_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tariff = Tariff.objects.get(pk=tariff_id)
    serializer = TariffSerializer(tariff)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=TariffSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_tariff(request, tariff_id):
    if not Tariff.objects.filter(pk=tariff_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tariff = Tariff.objects.get(pk=tariff_id)

    serializer = TariffSerializer(tariff, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=TariffAddSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
def create_tariff(request):
    serializer = TariffSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Tariff.objects.create(**serializer.validated_data)

    tariffs = Tariff.objects.filter(status=1)
    serializer = TariffSerializer(tariffs, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_tariff(request, tariff_id):
    if not Tariff.objects.filter(pk=tariff_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tariff = Tariff.objects.get(pk=tariff_id)
    tariff.status = 2
    tariff.save()

    tariffs = Tariff.objects.filter(status=1)
    serializer = TariffSerializer(tariffs, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsBuyer])
def add_tariff_to_forecastCloudPrice(request, tariff_id):
    if not Tariff.objects.filter(pk=tariff_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tariff = Tariff.objects.get(pk=tariff_id)

    draft_forecastCloudPrice = get_draft_forecastCloudPrice(request)

    if draft_forecastCloudPrice is None:
        draft_forecastCloudPrice = Forecastcloudprice.objects.create()
        draft_forecastCloudPrice.owner = identity_user(request)
        draft_forecastCloudPrice.save()

    if TariffForecastcloudprice.objects.filter(forecastCloudPrice=draft_forecastCloudPrice, tariff=tariff).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = TariffForecastcloudprice.objects.create(
        forecastCloudPrice=draft_forecastCloudPrice,
        tariff=tariff
    )
    item.save()

    serializer = ForecastcloudpriceSerializer(draft_forecastCloudPrice)
    return Response(serializer.data["tariffs"])


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE),
    ]
)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def update_tariff_image(request, tariff_id):
    if not Tariff.objects.filter(pk=tariff_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tariff = Tariff.objects.get(pk=tariff_id)

    image = request.data.get("image")
    if image is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    tariff.image = image
    tariff.save()

    serializer = TariffSerializer(tariff)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER
        ),
        openapi.Parameter(
            'date_formation_start',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_end',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_forecastCloudPrices(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    forecastCloudPrices = Forecastcloudprice.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        forecastCloudPrices = forecastCloudPrices.filter(owner=user)

    if status > 0:
        forecastCloudPrices = forecastCloudPrices.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        forecastCloudPrices = forecastCloudPrices.filter(
            date_formation__gt=parse_datetime(date_formation_start) - timedelta(days=1))

    if date_formation_end and parse_datetime(date_formation_end):
        forecastCloudPrices = forecastCloudPrices.filter(
            date_formation__lt=parse_datetime(date_formation_end) + timedelta(days=1))

    serializer = ForecastcloudpricesSerializer(forecastCloudPrices, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsBuyer])
def get_cart_info(request):
    resp = {
        "tariffs_count": 0,
        "draft_forecastCloudPrice": 0
    }

    draft_forecastCloudPrice = get_draft_forecastCloudPrice(request)
    if draft_forecastCloudPrice:
        tariffs = TariffForecastcloudprice.objects.filter(forecastCloudPrice=draft_forecastCloudPrice)
        resp = {
            "tariffs_count": tariffs.count(),
            "draft_forecastCloudPrice": draft_forecastCloudPrice.pk
        }

    return Response(resp)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_forecastCloudPrice_by_id(request, forecastCloudPrice_id):
    if not Forecastcloudprice.objects.filter(pk=forecastCloudPrice_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    forecastCloudPrice = Forecastcloudprice.objects.get(pk=forecastCloudPrice_id)

    user = identity_user(request)
    if not user.is_superuser and forecastCloudPrice.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ForecastcloudpriceSerializer(forecastCloudPrice, many=False)
    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=ForecastcloudpriceSerializer)
@api_view(["PUT"])
@permission_classes([IsBuyer])
def update_forecastCloudPrice(request, forecastCloudPrice_id):
    user = identity_user(request)
    if not Forecastcloudprice.objects.filter(pk=forecastCloudPrice_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    forecastCloudPrice = Forecastcloudprice.objects.get(pk=forecastCloudPrice_id)
    serializer = ForecastcloudpriceSerializer(forecastCloudPrice, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsBuyer])
def update_status_user(request, forecastCloudPrice_id):
    user = identity_user(request)
    if not Forecastcloudprice.objects.filter(pk=forecastCloudPrice_id, owner=user).exists():
        return Response({
            "error": "прогноз не найден"
        }, status=status.HTTP_404_NOT_FOUND)

    forecastCloudPrice = Forecastcloudprice.objects.get(pk=forecastCloudPrice_id)

    if forecastCloudPrice.status != 1:
        return Response({
            "error": "прогноз не в том статусе"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if not forecastCloudPrice.days:
        return Response({
            "error": "поле days не заполнено"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    forecastCloudPrice.status = 2
    forecastCloudPrice.date_formation = timezone.now()
    forecastCloudPrice.save()

    serializer = ForecastcloudpriceSerializer(forecastCloudPrice)
    return Response(serializer.data)


@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    )
)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, forecastCloudPrice_id):
    if not Forecastcloudprice.objects.filter(pk=forecastCloudPrice_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])
    if request_status not in [3, 4]:
        return Response({
            "error": "некорректный status"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    forecastCloudPrice = Forecastcloudprice.objects.get(pk=forecastCloudPrice_id)

    if forecastCloudPrice.status != 2:
        return Response({
            "error": "прогноз не в том статусе"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        serializer = ForecastcloudpriceSerializer(forecastCloudPrice)
        forecastCloudPrice.price = calc(serializer.data)

    forecastCloudPrice.date_complete = timezone.now()
    forecastCloudPrice.status = request_status
    forecastCloudPrice.moderator = identity_user(request)
    forecastCloudPrice.save()

    serializer = ForecastcloudpriceSerializer(forecastCloudPrice)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsBuyer])
def delete_forecastCloudPrice(request, forecastCloudPrice_id):
    user = identity_user(request)
    if not Forecastcloudprice.objects.filter(pk=forecastCloudPrice_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    forecastCloudPrice = Forecastcloudprice.objects.get(pk=forecastCloudPrice_id)

    if forecastCloudPrice.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    forecastCloudPrice.status = 5
    forecastCloudPrice.save()

    serializer = ForecastcloudpriceSerializer(forecastCloudPrice, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsBuyer])
def delete_tariff_from_forecastCloudPrice(request, forecastCloudPrice_id, tariff_id):
    user = identity_user(request)
    if not Forecastcloudprice.objects.filter(pk=forecastCloudPrice_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not TariffForecastcloudprice.objects.filter(forecastCloudPrice_id=forecastCloudPrice_id,
                                                   tariff_id=tariff_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = TariffForecastcloudprice.objects.get(forecastCloudPrice_id=forecastCloudPrice_id, tariff_id=tariff_id)
    item.delete()

    items = TariffForecastcloudprice.objects.filter(forecastCloudPrice_id=forecastCloudPrice_id)
    data = [TariffItemSerializer(item.tariff, context={"count": item.count}).data for item in items]

    return Response(data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='PUT', request_body=TariffForecastcloudpriceSerializer)
@api_view(["PUT"])
@permission_classes([IsBuyer])
def update_tariff_in_forecastCloudPrice(request, forecastCloudPrice_id, tariff_id):
    user = identity_user(request)
    if not Forecastcloudprice.objects.filter(pk=forecastCloudPrice_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not TariffForecastcloudprice.objects.filter(tariff_id=tariff_id,
                                                   forecastCloudPrice_id=forecastCloudPrice_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    forecastCloudPrice = Forecastcloudprice.objects.get(pk=forecastCloudPrice_id)
    if forecastCloudPrice.status != 1:
        return Response({
            "error": "Некорректный статус прогноза"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = TariffForecastcloudprice.objects.get(tariff_id=tariff_id, forecastCloudPrice_id=forecastCloudPrice_id)

    serializer = TariffForecastcloudpriceSerializer(item, data=request.data, partial=True)

    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@api_view(["GET"])
def user_info(request):
    user = identity_user(request)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='PUT', request_body=UserUpdateProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = identity_user(request)

    serializer = UserUpdateProfileSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)
