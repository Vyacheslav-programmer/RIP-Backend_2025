def calc(tarrifs):
    ram = 0

    for tarrif in tarrifs:
        ram += tarrif["count"] * tarrif["price"]

    return ram