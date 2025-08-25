import argparse
import requests
from collections import Counter
import re
import os
from concurrent.futures import ThreadPoolExecutor
import time


# Обращение по заданному адресу
def request(url):
    try:
        response = requests.get(url, timeout=5)
        time = response.elapsed.total_seconds()

        # Определяем тип ответа
        status = 'Success' if response.status_code < 400 else 'Failed'
        return time, status

    except requests.exceptions.RequestException:
        return None, 'Error'


# Сбор и подсчет статистики по адресу заданное число раз
def host_info(url, count):
    times, types = [], []

    for _ in range(count):
        time, response_type = request(url)
        if time:
            times.append(time)
        types.append(response_type)

    stats = Counter(types)

    total_info = {
        'Host': url,
        'Success': stats.get('Success', 0),
        'Failed': stats.get('Failed', 0),
        'Error': stats.get('Error', 0),
        'Min': min(times) if times else 'N/A',
        'Max': max(times) if times else 'N/A',
        'Avg': sum(times) / len(times) if times else 'N/A'
    }

    return total_info


# Расчленение ввода и проверка того, что он состоит как минимум из одного непробельного символа
def analyze_input(user_input):
    separated_input = [host.strip() for host in user_input if host.strip()]
    if not separated_input:
        print('Enter hosts using -H/--hosts option OR -F/--file option')
        exit(1)
    return separated_input


# Проверка хостов на соответствие шаблону из задания
def if_valid_url(url):
    if not re.match(r'^https?://[0-9A-Za-z-]+\.[A-Za-z]{2,}', url):
        print(f'{url} is invalid URL. You have to use the following pattern: https://example.com')
        return None
    else:
        return url


# Вывод статистики в консоль или в файл
def write_output(res, out_file=None):
    if out_file:
        try:
            with open(out_file, 'w') as outfile:
                for r in res:
                    for key, value in r.items():
                        outfile.write(f'{key}: {value}\n')
                    outfile.write('\n')
        except IOError as e:
            print(f"Error writing file: {e}")
            exit(1)
    else:
        for r in res:
            for key, value in r.items():
                print(f'{key}: {value}')
            print()


def main():
    start_time = time.time()

    # Создание парсера и аргументов
    parser = argparse.ArgumentParser(description='Enter comma-separated hosts')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-H', '--hosts', help='Enter hosts', type=str)
    group.add_argument('-F', '--file')

    parser.add_argument('-C', '--count', help='Enter count number', default=1, type=int)
    parser.add_argument('-O', '--output')
    args = parser.parse_args()

    # Проверка наличия ввода прямо в консоль
    if args.hosts:
        separated_hosts = analyze_input(args.hosts.split(','))

    # Проверка наличия файлового ввода
    elif args.file and os.path.exists(args.file):
        try:
            with open(args.file, 'r') as infile:
                separated_hosts = analyze_input(infile)
        except FileNotFoundError:
            print("File Not Found Error: No such file or directory")
            exit(1)
        except PermissionError:
            print("Permission Denied Error: Access is denied")
            exit(1)
        except IOError as e:
            print(f"Error reading file: {e}")
            exit(1)

    # Проверка того, что count больше нуля
    if args.count <= 0:
        print(f'Invalid count number: {args.count}')
        exit(1)

    # Проверка хостов на соответствие заданному шаблону
    valid_urls = [if_valid_url(host) for host in separated_hosts]
    if not any(valid_urls):
        print('No valid URLs provided!')
        exit(1)

    # Сбор статистики и вывод итогов
    else:
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_results = {executor.submit(host_info, host, args.count): host for host in valid_urls}

            outputs = []
            for future in future_results:
                try:
                    result = future.result()
                    outputs.append(result)
                except Exception as e:
                    print(f"Error processing URL {future_results[future]}: {e}")
            write_output(outputs, args.output)

    end_time = time.time()
    run_time = end_time - start_time
    print(f'Время выполнения программы: {run_time:.2f} секунд(ы)')

if __name__ == "__main__":
    main()

