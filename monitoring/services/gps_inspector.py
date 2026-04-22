import requests
from requests import RequestException


class GPSInspectorService:
    BASE_URL = "http://172.20.20.9:7900"
    TOKEN = "87da45bef050487d75a3c787828c9104"
    TIMEOUT = 20

    @classmethod
    def _headers(cls):
        return {
            "Authorization": cls.TOKEN,
            "Content-Type": "application/json",
        }

    @classmethod
    def _request(cls, method: str, endpoint: str, params=None):
        url = f"{cls.BASE_URL}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=cls._headers(),
                params=params or {},
                timeout=cls.TIMEOUT,
            )
            data = response.json()

            if response.status_code >= 400:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": data,
                }

            return {
                "success": True,
                "status_code": response.status_code,
                "data": data,
            }
        except RequestException as e:
            return {
                "success": False,
                "status_code": 503,
                "error": {
                    "message": "GPS Inspector service bilan ulanishda xatolik yuz berdi",
                    "detail": str(e),
                },
            }
        except ValueError:
            return {
                "success": False,
                "status_code": 502,
                "error": {
                    "message": "GPS Inspector service noto‘g‘ri JSON qaytardi",
                },
            }

    @classmethod
    def get_districts(cls):
        return cls._request("GET", "/v1/districts")

    @classmethod
    def get_mfys(cls, page: int, limit: int, district_cad_code=None, mfy_cad_code=None):
        params = {
            "page": page,
            "limit": limit,
        }
        if district_cad_code:
            params["district_cad_code"] = district_cad_code
        if mfy_cad_code:
            params["mfy_cad_code"] = mfy_cad_code

        return cls._request("GET", "/v1/mfys", params=params)

    @classmethod
    def get_gps_inspectors_by_mfy(cls, mfy_id, minutes=None):
        params = {}
        if minutes is not None:
            params["minutes"] = minutes

        return cls._request("GET", f"/v1/inspects/gps-mfy/{mfy_id}", params=params)