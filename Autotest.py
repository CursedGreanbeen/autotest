import argparse
import requests


parser = argparse.ArgumentParser(description='Enter hosts separated with commas without spaces')
parser.add_argument('-H', '--hosts', help='Enter hosts', type=str)
parser.add_argument('-C', '--count', help='key number', default=1, type=int)
parser.add_argument('-F', '--file')
parser.add_argument('-O', '--output')
args = parser.parse_args()


def request(url):
    try:
        response = requests.get(url)
        time = response.elapsed

        if response.status_code < 400:
            response_type = 'success'
        if 400 <= response.status_code <= 500:
            response_type = 'failed'
        else:
            response_type = 'error'

            return time, response_type

    except ConnectionError:
        print('Check your Internet connection')


def host_info(url, count):
    times = []
    types = {'success': 0, 'failed': 0, 'error': 0}

    for _ in range(count):
        times.append(request(url[0]))
        time_avg = sum(times)/len(times)
        time_max = max(times)
        time_min = min(times)

        for key in types:
            if url[1] == key:
                types[key] += 1

    total_info = {
        'url': url,
        'success': types['success'],
        'failed': types['failed'],
        'error': types['error'],
        'Min': time_min,
        'Max': time_max,
        'Avg': time_avg
    }

    return total_info

if args.hosts:
    separated_hosts = args.hosts.split(',')
    for host in separated_hosts:
        output = host_info(host, args.count)

        for key, value in output.items():
            print(f"{key}: {value}")

