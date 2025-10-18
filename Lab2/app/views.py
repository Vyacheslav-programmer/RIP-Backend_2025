from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Tariff, Forecast, TariffForecast


def index(request):
    tariff_name = request.GET.get("tariff_name", "")
    tariffs = Tariff.objects.filter(status=1)

    if tariff_name:
        tariffs = tariffs.filter(name__icontains=tariff_name)

    context = {
        "tariff_name": tariff_name,
        "tariffs": tariffs
    }

    draft_forecast = get_draft_forecast()
    if draft_forecast:
        context["tariffs_count"] = len(draft_forecast.get_tariffs())
        context["draft_forecast"] = draft_forecast

    return render(request, "tariffs_page.html", context)


def tariff_page(request, tariff_id):
    if not Tariff.objects.filter(pk=tariff_id).exists():
        return redirect("/")

    context = {
        "tariff": Tariff.objects.get(id=tariff_id)
    }

    return render(request, "tariff_page.html", context)


def forecast_page(request, forecast_id):
    if not Forecast.objects.filter(pk=forecast_id).exists():
        return redirect("/")

    forecast = Forecast.objects.get(id=forecast_id)
    if forecast.status == 5:
        return render(request, "404.html")

    context = {
        "forecast": forecast,
    }

    return render(request, "forecast_page.html", context)


def add_tariff_to_draft_forecast(request, tariff_id):
    tariff_name = request.POST.get("tariff_name")
    redirect_url = f"/?tariff_name={tariff_name}" if tariff_name else "/"

    draft_forecast = get_draft_forecast()
    if draft_forecast is None:
        draft_forecast = Forecast.objects.create()
        draft_forecast.owner = get_current_user()
        draft_forecast.date_created = timezone.now()
        draft_forecast.save()

    tariff = Tariff.objects.get(pk=tariff_id)
    if TariffForecast.objects.filter(forecast=draft_forecast, tariff=tariff).exists():
        return redirect(redirect_url)

    item = TariffForecast(
        forecast=draft_forecast,
        tariff=tariff
    )
    item.save()

    return redirect(redirect_url)


def delete_forecast(request, forecast_id):
    if not Forecast.objects.filter(pk=forecast_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE forecasts SET status=5 WHERE id = %s", [forecast_id])

    return redirect("/")


def get_draft_forecast():
    return Forecast.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()