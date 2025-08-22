import argparse
import requests
from collections import Counter
import re
import os


# Создание парсера и аргументов
parser = argparse.ArgumentParser(description='Enter comma-separated hosts')
parser.add_argument('-H', '--hosts', help='Enter hosts', type=str)
parser.add_argument('-C', '--count', help='Enter count number', default=1, type=int)
parser.add_argument('-F', '--file')
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

    except requests.exceptions.RequestException:
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


# Проверка наличия пользовательского ввода
if args.hosts:
    user_input = args.hosts

    # Проверка того, что хосты состоят как минимум из одного непробельного символа
    separated_hosts = [host.strip() for host in user_input.split(',') if host.strip()]
    if not separated_hosts:
        print('Enter hosts using -H/--hosts option OR -F/--file option')
        exit(1)

# Проверка наличия файлового ввода
elif args.file and os.path.exists(args.file):
    try:
        with open(args.file, 'r') as infile:
            separated_hosts = [host.strip() for host in infile if host.strip()]
            if not separated_hosts:
                print('Enter hosts using -H/--hosts option OR -F/--file option')
                exit(1)
    except IOError as e:
        print(f"Error reading file: {e}")
        exit(1)

else:
    print('Enter hosts using -H/--hosts option OR -F/--file option')
    exit(1)


# Проверка хостов на соответствие заданному шаблону
for host in separated_hosts:
    if not re.match(r'^https?://[0-9A-Za-z-]+\.[A-Za-z]{2,}', host):
        print(f'{host} is invalid URL. You have to use the following pattern: https://example.com')
        continue

    # Проверка того, что count больше нуля. Запуск функции сбора статистики, если введенные параметры верны
    if args.count <= 0:
        print(f'Invalid count number: {args.count}')
        exit(1)
    output = host_info(host, args.count)

    # Вывод статистики в консоль или в файл
    if not args.output:
        for key, value in output.items():
            print(f"{key}: {value}\n")
    else:
        with open(args.output, 'a') as outfile:
            for key, value in output.items():
                outfile.write(f"{key}: {value}\n")

