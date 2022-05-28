import hashlib
import requests
import random
import json
from datetime import datetime, timezone, timedelta


class SagemcomClient:
    def __init__(self, user: str, password: str, host: str = 'http://192.168.1.1'):
        self.sess = requests.session()
        self.path = '/cgi/json-req'
        self.id, self.sessId = (0, 0)
        self.last_nonce = ''
        self.datamodel = None
        self._set_datamodel()

        self.host = host
        self.user = user
        self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()

    def login(self):
        params = {
            "parameters": {
                "user": self.user,
                "persistent": "true",
                "session-options": {
                    "nss": self.datamodel['nss'],
                    "language": "ident",
                    "context-flags": {
                        "get-content-name": True,
                        "local-time": True
                    },
                    "capability-depth": 2,
                    "capability-flags": {
                        "name": True,
                        "default-value": False,
                        "restriction": True,
                        "description": False,
                    },
                    "time-format": "ISO_8601",
                    "write-only-string": "_XMO_WRITE_ONLY_",
                    "undefined-write-only-string": "_XMO_UNDEFINED_WRITE_ONLY_"
                }
            }
        }
        result = self._request(self._create_action('logIn', params), True)
        self.sessId = result['parameters']['id']
        self.last_nonce = result['parameters']['nonce']

    def reboot(self):
        action = {
            "method": "reboot",
            "xpath": "Device",
            "parameters": {"source": "GUI"},
        }
        return self._request(self._create_action('reboot', action))

    def _set_datamodel(self, model: dict = None):
        if model is None:
            self.datamodel = {
                "name": 'Internal',
                "nss": [
                    {
                        "name": "gtw",
                        "uri": "http://sagemcom.com/gateway-data"
                    }
                ]
            }
        else:
            self.datamodel = model

    @staticmethod
    def _create_action(method: str, params: dict) -> list:
        action = {
            "id": 0,
            "method": method
        }
        action.update(params)
        return [action]

    def _request(self, action: list, priority: bool = False) -> dict:
        auth = self._get_auth()
        body = {
            "request": {
                "id": self.id,
                "session-id": self.sessId,
                "priority": priority,
                "actions": action,
                "cnonce": auth['cnonce'],
                "auth-key": auth['auth-key']
            }
        }
        cookie = self._get_cookie(auth['ha1'], auth['cnonce'])
        self.id += 1
        r = self.sess.post(f'{self.host}{self.path}', data={"req": json.dumps(body)}, cookies=cookie)

        if r.status_code == 200:
            response = r.json()
            if response['reply']['error']['description'] == 'XMO_REQUEST_NO_ERR':
                return response['reply']['actions'][0]['callbacks'][0]
        raise Exception('Authentication error')

    def _get_cookie(self, ha1: str, nonce: int) -> dict:
        expires = datetime.now(timezone.utc) + timedelta(days=1)
        cookie = {
            "name": "session",
            "value": json.dumps({
                "req_id": self.id,
                "sess_id": self.sessId,
                "basic": False,
                "user": self.user,
                "dataModel": self.datamodel,
                "ha1": f'{ha1[:10]}{self.password}{ha1[:10]}',
                "nonce": nonce
            }),
            "expires": expires.strftime("%Y%m%d"),
            "path": '/'
        }
        return cookie

    def _get_auth(self) -> dict:
        current_nonce = random.randint(0, 4294967295)
        ha1 = hashlib.sha512(f'{self.user}:{self.last_nonce}:{self.password}'.encode('utf-8')).hexdigest()
        self.last_nonce = current_nonce
        return {
            "ha1": ha1,
            "cnonce": current_nonce,
            "auth-key": hashlib.sha512(f'{ha1}:{self.id}:{current_nonce}:JSON:{self.path}'.encode('utf-8')).hexdigest()
        }
