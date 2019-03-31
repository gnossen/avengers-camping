import amc
import argparse
import datetime
import functools
import logging
import requests
import subprocess
import sys
import tempfile
import time

LOGGER = logging.getLogger('camp')

URL = 'https://www.amctheatres.com/movie-theatres/san-jose/amc-mercado-20/showtimes/all/2019-04-25/amc-mercado-20/all'
CAMP_INTERVAL = datetime.timedelta(seconds=10)


def is_avengers_title(title):
    return ('avengers' in title.lower() and
            'endgame' in title.lower())


def is_available(showtime):
    return showtime.status != 'Available Soon'


def has_available_time(film_info):
    for showtime_type, showtimes in film_info.items():
        if any(is_available(showtime) for showtime in showtimes):
            return True
    return False


def is_avengers_on_sale(films):
    for film_title, film_info in films.items():
        if is_avengers_title(film_title):
            return has_available_time(film_info)
    else:
        return False


PARSER = argparse.ArgumentParser(description='Camp for Avengers Endgame')
PARSER.add_argument('email', help='The email address to send mail to.')
PARSER.add_argument('filepath', help='An HTML file to load for testing.', nargs='?', default=None)


def download_page():
        page_resp = requests.get(URL)
        page_resp.raise_for_status()
        return page_resp.text


def load_page_from_filesystem(path):
    page = None
    with open(path, 'r') as f:
        page = f.read()
    return page


def get_get_page_function(filepath):
    if filepath is None:
        return download_page
    else:
        return functools.partial(load_page_from_filesystem, filepath)


def camp_once(get_page):
    page = get_page()
    films = amc.get_films(page)
    return is_avengers_on_sale(films)


def send_email(email):
    subject = 'Avengers On Sale!'
    body = URL
    email_content = 'Subject: {}\n\n{}'.format(subject, body).encode('ascii')
    with tempfile.TemporaryFile(mode='r') as stdout:
        with tempfile.TemporaryFile(mode='r') as stderr:
            email_process = subprocess.Popen(('sendmail', '-v', email), stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
            email_process.communicate(input=email_content)
            stdout.seek(0)
            stderr.seek(0)
            LOGGER.info('sendmail STDOUT: {}'.format(stdout.read()))
            LOGGER.info('sendmail STDERR: {}'.format(stderr.read()))
            if email_process.returncode != 0:
                raise RuntimeError('Failed to send email.')


def camp(email, get_page):
    while True:
        try:
            if camp_once(get_page):
                break
        except requests.exceptions.HTTPError as e:
            LOGGER.error('Page download failed: {}'.format(e))
        except Exception as e:
            LOGGER.error('Exception during parsing: {}'.format(e))
        LOGGER.info('Avengers is not on sale!')
        time.sleep(CAMP_INTERVAL.total_seconds())
    LOGGER.info('Avengers is on sale!')
    send_email(email)


def main(argv):
    args = PARSER.parse_args(argv)
    email_address = args.email
    get_page = get_get_page_function(args.filepath)
    camp(email_address, get_page)


if __name__ == '__main__':
    fmt = '%(asctime)-15s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt)
    main(sys.argv)
