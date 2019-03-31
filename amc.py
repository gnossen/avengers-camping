import bs4
import collections


class Showtime(collections.namedtuple('Showtime', ('time', 'status'))):
    @staticmethod
    def from_elem(showtime_elem):
        time = showtime_elem.attrs['aria-label']
        status = showtime_elem.find(class_='ShowtimeButtons-status').text
        return Showtime(time, status)


def get_title(film_div):
    film_title_elem = film_div.find('a', class_='MovieTitleHeader-title')
    film_title_h2 = film_title_elem.find('h2')
    return film_title_h2.text


def get_showtimes(showtimes_section):
    showtime_elems = showtimes_section.find_all(class_='Showtime')
    return tuple(
        Showtime.from_elem(showtime_elem) for showtime_elem in showtime_elems)


def get_films(page_text):
    page = bs4.BeautifulSoup(page_text, 'html.parser')
    films = {}
    film_divs = page.find_all('div', class_='ShowtimesByTheatre-film')
    for film_div in film_divs:
        film_title = get_title(film_div)
        showtimes_sections = film_div.find_all(class_='Showtimes-Section')
        films[film_title] = {}
        for showtimes_section in showtimes_sections:
            showtime_type = showtimes_section.find(
                'h4', class_='txt--uppercase').text
            films[film_title][showtime_type] = get_showtimes(showtimes_section)
    return films
