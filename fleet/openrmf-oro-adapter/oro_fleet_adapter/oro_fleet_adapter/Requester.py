import requests
from rclpy.impl.rcutils_logger import RcutilsLogger
from requests import Response


class Requester:
    def __init__(self, base_url: str, headers: dict, timeout: float, logger: RcutilsLogger) -> None:
        self.base_url = base_url
        self.headers = headers
        self.timeout = timeout
        self.logger = logger
        self.HTTP_OK = 200

    def get_request(self, /, *, endpoint: str, json=None) -> Response | None:
        url = f"{self.base_url}{endpoint}"
        try:
            res = requests.get(url, headers=self.headers, json=json, timeout=self.timeout)
            if res.status_code != self.HTTP_OK:
                self.logger.warn(
                    f"\nStatus code {res.status_code} on GET {url} " f"with body {json}\nmessage: {res.text}"
                )
            return res
        except Exception as e:
            self.logger.error(f"Exception on GET {url}: {e}")
        return None

    def post_request(self, /, *, endpoint: str, json=None) -> Response | None:
        url = f"{self.base_url}{endpoint}"
        try:
            res = requests.post(url, headers=self.headers, json=json, timeout=self.timeout)
            if res.status_code != self.HTTP_OK:
                self.logger.warn(
                    f"\nStatus code {res.status_code} on POST {url} " f"with body {json}\nmessage: {res.text}"
                )
            return res
        except Exception as e:
            self.logger.error(f"Exception on POST {url}: {e}")
        return None
