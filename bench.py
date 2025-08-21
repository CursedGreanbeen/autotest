import argparse
import requests
from collections import Counter
import re


# Создание парсера и аргументов
parser = argparse.ArgumentParser(description='Enter hosts separated with comma without space')
parser.add_argument('-H', '--hosts', help='Enter hosts', type=str)
parser.add_argument('-C', '--count', help='Key number', default=1, type=int)
parser.add_argument('-F', '--file')
parser.add_argument('-O', '--output')
args = parser.parse_args()


# Функция, которая обращается по заданному адресу
def request(url):
    try:
        response = requests.get(url)
        time = response.elapsed.total_seconds()

        # Определяем тип ответа
        if response.status_code < 400:
            return time, 'Success'
        elif 400 <= response.status_code <= 599:
            return time, 'Failed'
        else:
            return None, 'Error'

    except requests.exceptions.RequestException:
        print(f'Request error for host {url}...')
        return None, 'Error'


# Функция, которая собирает и считает статистику по адресу заданное число раз
def host_info(url, count):
    times = []
    types = []

    for _ in range(count):
        time, type = request(url)
        if time:
            times.append(time)
        types.append(type)

    stats = Counter(types)

    if times:
        time_avg = sum(times) / len(times)
        time_max = max(times)
        time_min = min(times)
    else:
        time_avg = time_max = time_min = None

    total_info = {
        'Host': url,
        'Success': stats['Success'],
        'Failed': stats['Failed'],
        'Error': stats['Error'],
        'Min': time_min,
        'Max': time_max,
        'Avg': time_avg
    }

    return total_info


# Выполнение скрипта по заданным хостам
if args.hosts:
    # Проверка того, что строка состоит как минимум из одного непробельного символа
    if not args.hosts.strip():
        print('Enter hosts using -H or --hosts option')
        exit(1)

    # Разделение строки на отдельные хосты и проверка соответствия заданному шаблону
    separated_hosts = args.hosts.split(',')
    for host in separated_hosts:
        if not re.match(r'^https?://[0-9A-Za-z-]+\.[A-Za-z]+', host):
            print(f'{host} is invalid URL. You must use the following pattern: https://example.com')
            continue

        # Проверка того, что count больше нуля, и запуск функций с учетом введенных параметров
        if args.count > 0:
            output = host_info(host, args.count)
        else:
            print(f'Invalid count: {args.count}. Set to default value 1')
            output = host_info(host, 1)

        # Вывод статистики в консоль
        for key, value in output.items():
            print(f"{key}: {value}")

