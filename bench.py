import argparse
import requests
from collections import Counter
import re
import os


# Создание парсера и аргументов
parser = argparse.ArgumentParser(description='Enter comma-separated hosts')

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-H', '--hosts', help='Enter hosts', type=str)
group.add_argument('-F', '--file')

parser.add_argument('-C', '--count', help='Enter count number', default=1, type=int)
parser.add_argument('-O', '--output')
args = parser.parse_args()


# Функция, которая обращается по заданному адресу
def request(url):
    try:
        response = requests.get(url, timeout=5)
        time = response.elapsed.total_seconds()

        # Определяем тип ответа
        if response.status_code < 400:
            return time, 'Success'
        elif 400 <= response.status_code <= 599:
            return time, 'Failed'
        else:
            return None, 'Error'

    except requests.exceptions.Timeout:
        return None, 'Timeout'
    except requests.exceptions.ConnectionError:
        return None, 'ConnectionError'
    except requests.exceptions.RequestException:
        return None, 'RequestError'


# Функция, которая собирает и считает статистику по адресу заданное число раз
def host_info(url, count):
    times = []
    types = []

    for _ in range(count):
        time, response_type = request(url)
        if time:
            times.append(time)
        types.append(response_type)

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


# Расчлененка ввода и проверка, что он состоит как минимум из одного непробельного символа
def separate_check_input(user_input):
    separated_input = [host.strip() for host in user_input if host.strip()]
    if not separated_input:
        print('Enter hosts using -H/--hosts option OR -F/--file option')
        exit(1)
    return separated_input


# Будущий вывод
outputs = []

# Проверка наличия пользовательского ввода
if args.hosts:
    separated_hosts = separate_check_input(args.hosts.split(','))

# Проверка наличия файлового ввода
elif args.file and os.path.exists(args.file):
    try:
        with open(args.file, 'r') as infile:
            separated_hosts = separate_check_input(infile)
    except IOError as e:
        print(f"Error reading file: {e}")
        exit(1)


# Проверка того, что count больше нуля
if args.count <= 0:
    print(f'Invalid count number: {args.count}')
    exit(1)

# Проверка хостов на соответствие заданному шаблону
for host in separated_hosts:
    if not re.match(r'^https?://[0-9A-Za-z-]+\.[A-Za-z]{2,}', host):
        print(f'{host} is invalid URL. You have to use the following pattern: https://example.com')
        continue

    # Запуск функции сбора статистики, если введенные параметры верны
    result = host_info(host, args.count)
    outputs.append(result)

# Вывод статистики в консоль или в файл
if not args.output:
    for out in outputs:
        for key, value in out.items():
            print(f"{key}: {value}")
        print()
else:
    try:
        with open(args.output, 'w') as outfile:
            for out in outputs:
                for key, value in out.items():
                    outfile.write(f"{key}: {value}\n")
    except IOError as e:
        print(f"Error reading file: {e}")
        exit(1)

