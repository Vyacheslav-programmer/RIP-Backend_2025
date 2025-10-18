from django.shortcuts import render

tariffs_mock = [
    {
        "id": 1,
        "name": "AWS EC2",
        "description": "Amazon Elastic Compute Cloud — одна из инфраструктурных служб Amazon Web Services, позволяющая подписчику арендовать виртуальные выделенные серверы, называемые «экземплярами». Взаимодействовать со службой возможно с помощью веб-интерфейса, интерфейса командной строки, а также программно посредством API.",
        "ram": 16,
        "cpu": 4,
        "ssd": 40,
        "image": "http://localhost:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "Google Cloud",
        "description": "Google Cloud (GCP) — это облачная платформа от Google, которая предоставляет компаниям и разработчикам набор сервисов для работы с данными, вычислениями, хранением информации, аналитикой и машинным обучением.",
        "ram": 32,
        "cpu": 2,
        "ssd": 20,
        "image": "http://localhost:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "Azure Cloud",
        "description": "Azure Cloud (Microsoft Azure) — это постоянно расширяющийся набор облачных сервисов компании Microsoft, который предоставляет пользователям доступ к вычислительным ресурсам, хранилищу данных, сетевым решениям, аналитике и услугам искусственного интеллекта через Интернет",
        "ram": 16,
        "cpu": 8,
        "ssd": 10,
        "image": "http://localhost:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "Sber Cloud",
        "description": "Sber Cloud — это онлайн-сервис, позволяющий хранить ваши файлы (фото, видео, документы) и работать с ними удалённо, используя интернет с любого устройства.",
        "ram": 8,
        "cpu": 4,
        "ssd": 20,
        "image": "http://localhost:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "Yandex Cloud",
        "description": "Yandex Cloud — публичная облачная платформа, разработанная российской интернет-компанией Яндекс. Yandex Cloud предоставляет частным и корпоративным пользователям инфраструктуру и вычислительные ресурсы в формате «как услуга»",
        "ram": 24,
        "cpu": 2,
        "ssd": 16,
        "image": "http://localhost:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "VK Cloud",
        "description": "VK Cloud — это универсальная платформа облачных сервисов от VK, которая предоставляет компаниям и разработчикам доступ к вычислительным ресурсам, хранилищам, управляемым базам данных, контейнерам и другим услугам по модели «плати за потребление»",
        "ram": 32,
        "cpu": 8,
        "ssd": 32,
        "image": "http://localhost:9000/images/6.png"
    }
]

calculations_mock = [
    {
        "id": 1,
        "status": "Черновик",
        "date_created": "5 сентября 2025г",
        "ram": "15000",
        "tariffs": [
            {
                "id": 1,
                "count": 2
            },
            {
                "id": 2,
                "count": 4
            },
            {
                "id": 3,
                "count": 1
            }
        ]
    },
    {
        "id": 2,
        "status": "В работе",
        "date_created": "3 сентября 2025г",
        "ram": "123",
        "tariffs": [
            {
                "id": 1,
                "count": 3
            },
            {
                "id": 3,
                "count": 2
            }
        ]
    },
    {
        "id": 3,
        "status": "Завершена",
        "date_created": "27 августа 2025г",
        "ram": "123",
        "tariffs": [
            {
                "id": 2,
                "count": 4
            }
        ]
    }
]


def get_tariff(tariff_id):
    for tariff in tariffs_mock:
        if tariff["id"] == tariff_id:
            return tariff


def get_tariffs():
    return tariffs_mock


def search_tariffs(tariff_name):
    res = []

    for tariff in tariffs_mock:
        if tariff_name.lower() in tariff["name"].lower():
            res.append(tariff)

    return res


def get_draft_calculation():
    for calculation in calculations_mock:
        if calculation["status"] == "Черновик":
            return calculation


def get_calculation(calculation_id):
    for calculation in calculations_mock:
        if calculation["id"] == calculation_id:
            return calculation


def index(request):
    tariff_name = request.GET.get("tariff_name", "")
    tariffs = search_tariffs(tariff_name) if tariff_name else get_tariffs()
    draft_calculation = get_draft_calculation()

    context = {
        "tariffs": tariffs,
        "tariff_name": tariff_name,
        "tariffs_count": len(draft_calculation["tariffs"]),
        "draft_calculation": draft_calculation
    }

    return render(request, "tariffs_page.html", context)


def tariff_page(request, tariff_id):
    context = {
        "tariff": get_tariff(tariff_id),
    }

    return render(request, "tariff_page.html", context)


def calculation_page(request, calculation_id):
    calculation = get_calculation(calculation_id)
    tariffs = [
        {**get_tariff(tariff["id"]), "count": tariff["count"]}
        for tariff in calculation["tariffs"]
    ]

    context = {
        "calculation": calculation,
        "tariffs": tariffs
    }

    return render(request, "calculation_page.html", context)
