import requests
from django.conf import settings


def fetch_coordinates(address, apikey=settings.GEOCODER_TOKEN):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    try:
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']
        if 'error' in found_places:
            raise requests.exceptions.HTTPError(found_places['error'])
        if not found_places:
            return None
        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        return lat, lon
    except requests.exceptions.HTTPError as err:
        logging.debug(err)
    except requests.exceptions.ConnectionError as err:
        logging.debug(err)
    except requests.exceptions.Timeout as err:
        logging.debug(err)
    except requests.exceptions.JSONDecodeError:
        logging.debug('Non valid format of json file')
    except requests.exceptions.MissingSchema:
        logging.debug('Non valid format of url. (ex. http://name.ru)')
    except requests.exceptions.RequestException as err:
        logging.debug(err)
