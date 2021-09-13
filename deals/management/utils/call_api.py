from ratelimit import limits, sleep_and_retry
import requests


@sleep_and_retry
@limits(calls=30, period=300)
def call_api(url: str, payload: dict = None):

    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        return f'Call API FAILED!\nHTTP Error: {err}'
    except:
        return 'Call API FAILED!\nUndefined error'

    return response