from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class IPInfoBase:
    """
    Base class for IP API services.

    This class serves as a blueprint for creating subclasses that will
    implement methods to fetch IP information from different IP API services.
    """

    _url = None

    def _create_session(self) -> requests.Session:
        session = requests.Session()

        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retries)

        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def get_ip_info(self, url: str = None) -> Optional[dict]:
        try:
            response = self._create_session().get(url or self._url)
            response.raise_for_status()
        except Exception:
            return None

        return response.json()

    def get_country_code(self) -> Optional[str]:
        raise NotImplemented


class FreeIPAPI(IPInfoBase):
    """
    Concrete class to get IP information using Free IP API.

    Documentation:
        https://docs.freeipapi.com/
    """

    _url = 'https://freeipapi.com/api/json/'

    def get_country_code(self) -> Optional[str]:
        ip_info = self.get_ip_info()
        if not ip_info:
            return None

        return ip_info['countryCode']


class IP2Location(IPInfoBase):
    """
    Concrete class to get IP information using IP2Location.

    Documentation:
        https://www.ip2location.io/ip2location-documentation/
    """

    _url = 'https://api.ip2location.io/'

    def get_country_code(self) -> Optional[str]:
        ip_info = self.get_ip_info()
        if not ip_info:
            return None

        return ip_info['country_code']
