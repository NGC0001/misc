import datetime
import random
import math

html_head = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>HTTP TEST</title>
    </head>
    <body>
        <pre>
'''
html_tail = '''
        </pre>
    </body>
</html>
'''


def generate_random_string(minlen, maxlen):
    lnmin, lnmax = math.log(minlen), math.log(maxlen)
    lnlen = random.uniform(lnmin, lnmax)
    length = int(math.exp(lnlen))
    txt = ''
    for i in range(length):
        txt += chr(random.randint(32, 126))
    return txt


def is_http_request(recv_data):
    Accepted_Method = ['GET', 'POST']
    try:
        data = recv_data.decode('utf-8')
        lines = data.strip().splitlines()
        method, requestURI, http_version = lines[0].strip().upper().split()
        if method in Accepted_Method:
            if http_version[:4] == 'HTTP':
                return True
    except:
        return False
    return False


def compose_http_response(recieved_data=b''):
    try:
        if is_http_request(recieved_data):
            response_message_raw = html_head + generate_random_string(10, 10000) + html_tail

            # Reply as HTTP/1.1 server, saying "HTTP OK" (code 200).
            response_proto = 'HTTP/1.1'
            response_status_code = '200'
            response_status_text = 'OK' # this can be random
            response_status_raw = '{} {} {}\r\n'.format(
                    response_proto, response_status_code, response_status_text)

            HTTP_DATE_TIME_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
            response_headers = {
                'Server': 'nginx/1.10.3 (Ubuntu)',
                'Date': datetime.datetime.utcnow().strftime(HTTP_DATE_TIME_FORMAT),
                'Content-Type': 'text/html; charset=utf-8',
                'Content-Length': len(response_message_raw),
                'Connection': 'close',
            }
            response_headers_raw = ''.join(
                    '{}: {}\r\n'.format(k, v) for k, v in response_headers.items())

            response = '{}{}\r\n{}'.format(
                    response_status_raw, response_headers_raw, response_message_raw)
            response = response.encode('utf-8')
            return response
    except:
        return b''
    return b''

