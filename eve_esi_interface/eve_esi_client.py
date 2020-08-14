﻿"""Contains all shared OAuth 2.0 flow functions

This module contains all shared functions between the two different OAuth 2.0
flows recommended for web based and mobile/desktop applications. The functions
found here are used by the OAuth 2.0 contained in this project.

See https://github.com/esi/esi-docs
"""
import urllib
import requests
import sys
import base64
import hashlib
import secrets

from .auth_cache import EveESIAuth
from .error import EveOnlineClientError


class EveESIClient:
    def __init__(self, auth_cache, debug=False, logger=True, user_agent=None):
        """ constructor

        :param EveESIAuth auth_cache: authz tokens storage
        :param debug: flag which says that we are in debug mode
        :param logger: flag which says that we are in logger mode
        """
        self.__client_callback_url = 'https://localhost/callback/'
        self.__content_type = 'application/x-www-form-urlencoded'
        self.__login_host = 'login.eveonline.com'
        self.__base_auth_url = 'https://login.eveonline.com/v2/oauth/authorize/'
        self.__token_req_url = 'https://login.eveonline.com/v2/oauth/token'
        self.__attempts_to_reconnect = 5
        self.__debug = debug
        self.__logger = logger

        # экземпляр объекта, кеширующий аутентификационные токену и хранящий их в указанной директории
        if not isinstance(auth_cache, EveESIAuth):
            raise EveOnlineClientError("You should use EveESIAuth to configure client")
        self.__auth_cache = auth_cache

        # используется, если не пользователь не будет указаывать свой собственный идентификатор
        # Application: R Initiative 4 Q.Industrialist
        self.__default_ri4_client_id = "022ea197e3f2414f913b789e016990c8"

        # для корректной работы с ESI Swagger Interface следует указать User-Agent в заголовках запросов
        self.__user_agent = user_agent

    @property
    def auth_cache(self):
        """ authz tokens storage
        """
        return self.__auth_cache

    @property
    def client_callback_url(self):
        """ url to send back authorization code
        """
        return self.__client_callback_url

    def setup_client_callback_url(self, client_callback_url):
        self.__client_callback_url = client_callback_url

    @property
    def debug(self):
        """ flag which says that we are in debug mode
        """
        return self.__debug

    def enable_debug(self):
        self.__debug = True

    def disable_debug(self):
        self.__debug = False

    @property
    def logger(self):
        """ flag which says that we are in logger mode
        """
        return self.__logger

    def enable_logger(self):
        self.__logger = True

    def disable_logger(self):
        self.__logger = False

    @property
    def user_agent(self):
        """ User-Agent which used in http requests to CCP Servers
        """
        return self.__user_agent

    def setup_user_agent(self, user_agent):
        """ configures User-Agent which used in http requests to CCP Servers

        :param user_agent: format recomendation - '<project_url> Maintainer: <maintainer_name> <maintainer_email>'
        """
        self.__user_agent = user_agent

    @staticmethod
    def __combine_client_scopes(scopes):
        return " ".join(scopes)

    def __print_auth_url(self, client_id, client_scopes, code_challenge=None):
        """Prints the URL to redirect users to.

        :param client_id: the client ID of an EVE SSO application
        :param code_challenge: a PKCE code challenge
        """
        params = {
            "response_type": "code",
            "redirect_uri": self.__client_callback_url,
            "client_id": client_id,
            "scope": self.__combine_client_scopes(client_scopes),
            "state": "unique-state"
        }

        if code_challenge:
            params.update({
                "code_challenge": code_challenge,
                "code_challenge_method": "S256"
            })

        string_params = urllib.parse.urlencode(params)
        full_auth_url = "{}?{}".format(self.__base_auth_url, string_params)

        print("\nOpen the following link in your browser:\n\n {} \n\n Once you "
              "have logged in as a character you will get redirected to "
              "{}.".format(full_auth_url, self.__client_callback_url))

    def __send_token_request(self, form_values, add_headers=None):
        """Sends a request for an authorization token to the EVE SSO.

        :param form_values: a dict containing the form encoded values that should be sent with the request
        :param add_headers: a dict containing additional headers to send
        :returns: requests.Response: A requests Response object
        """
        headers = {
            "Content-Type": self.__content_type,
            "Host": self.__login_host}
        if self.__user_agent:
            headers.update({"User-Agent": self.__user_agent})
        if not (add_headers is None):
            headers.update(add_headers)

        res = requests.post(
            self.__token_req_url,
            data=form_values,
            headers=headers)

        if self.__debug:
            print("Request sent to URL {} with headers {} and form values: "
                  "{}\n".format(res.url, headers, form_values))
        res.raise_for_status()

        return res

    def __send_token_refresh(self, refresh_token, client_id, client_scopes=None):
        headers = {
            "Content-Type": self.__content_type,
            "Host": self.__login_host}
        if self.__user_agent:
            headers.update({"User-Agent": self.__user_agent})
        form_values = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id
        }
        if not (client_scopes is None) and len(client_scopes) > 0:
            form_values.update({
                "scope": self.__combine_client_scopes(client_scopes)  # OPTIONAL
            })

        res = requests.post(
            self.__token_req_url,
            data=form_values,
            headers=headers,
        )

        if self.__debug:
            print("Request sent to URL {} with headers {} and form values: "
                  "{}\n".format(res.url, headers, form_values))
        res.raise_for_status()

        return res

    def send_esi_request_http(self, uri, etag, body=None):
        headers = {
            "Authorization": "Bearer {}".format(self.__auth_cache.access_token),
        }
        if not (etag is None) and (body is None):
            headers.update({"If-None-Match": etag})
        if self.__user_agent:
            headers.update({"User-Agent": self.__user_agent})

        res = None
        try:
            proxy_error_times = 0
            while True:
                if body is None:
                    res = requests.get(uri, headers=headers)
                    if self.__debug:
                        print("\nMade GET request to {} with headers: "
                              "{}\nAnd the answer {} was received with "
                              "headers {} and encoding {}".
                              format(uri,
                                     res.request.headers,
                                     res.status_code,
                                     res.headers,
                                     res.encoding))
                else:
                    headers.update({"Content-Type": "application/json"})
                    res = requests.post(uri, data=body, headers=headers)
                    if self.__debug:
                        print("\nMade POST request to {} with data {} and headers: "
                              "{}\nAnd the answer {} was received with "
                              "headers {} and encoding {}".
                              format(uri,
                                     body,
                                     res.request.headers,
                                     res.status_code,
                                     res.headers,
                                     res.encoding))
                # вывод отладочной информации : код, uri, last-modified, etag
                if self.__logger:
                    log_line = str(res.status_code) + " " + uri[31:]
                    if 'Last-Modified' in res.headers:
                        log_line = log_line + " " + str(res.headers['Last-Modified'])[17:-4]
                    if 'Etag' in res.headers:
                        log_line = log_line + " " + str(res.headers['Etag'])
                    print(log_line)
                # обработка исключительных ситуаций
                if (res.status_code in [502, 504]) and (proxy_error_times < self.__attempts_to_reconnect):
                    # пять раз пытаемся повторить отправку сломанного запроса (часто случается
                    # при подключении через 3G-модем)
                    proxy_error_times = proxy_error_times + 1
                    continue
                res.raise_for_status()
                break
        except requests.exceptions.HTTPError as err:
            print(err)
            print(res.json())
            raise
        except:
            print(sys.exc_info())
            raise
        return res

    def send_esi_request_json(self, uri, etag, body=None):
        return self.send_esi_request_http(uri, etag, body).json()

    @staticmethod
    def __print_sso_failure(sso_response):
        print("\nSomething went wrong! Here's some debug info to help you out:")
        print("\nSent request with url: {} \nbody: {} \nheaders: {}".format(
            sso_response.request.url,
            sso_response.request.body,
            sso_response.request.headers
        ))
        print("\nSSO response code is: {}".format(sso_response.status_code))
        print("\nSSO response JSON is: {}".format(sso_response.json()))

    def auth(self, client_scopes, client_id=""):
        print("Follow the prompts and enter the info asked for.")

        # Generate the PKCE code challenge
        random = base64.urlsafe_b64encode(secrets.token_bytes(32))
        m = hashlib.sha256()
        m.update(random)
        d = m.digest()
        code_challenge = base64.urlsafe_b64encode(d).decode().replace("=", "")

        if not client_id:
            client_id = input("Copy your SSO application's client ID and enter it "
                              "here [press 'Enter' for R Initiative 4 app]: ")
            if not client_id:
                client_id = self.__default_ri4_client_id

        # Because this is a desktop/mobile application, you should use
        # the PKCE protocol when contacting the EVE SSO. In this case, that
        # means sending a base 64 encoded sha256 hashed 32 byte string
        # called a code challenge. This 32 byte string should be ephemeral
        # and never stored anywhere. The code challenge string generated for
        # this program is ${random} and the hashed code challenge is ${code_challenge}.
        # Notice that the query parameter of the following URL will contain this
        # code challenge.

        self.__print_auth_url(client_id, client_scopes, code_challenge=code_challenge)

        auth_code = input("Copy the \"code\" query parameter and enter it here: ")

        code_verifier = random

        form_values = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": auth_code,
            "code_verifier": code_verifier
        }

        # Because this is using PCKE protocol, your application never has
        # to share its secret key with the SSO. Instead, this next request
        # will send the base 64 encoded unhashed value of the code
        # challenge, called the code verifier, in the request body so EVE's
        # SSO knows your application was not tampered with since the start
        # of this process. The code verifier generated for this program is
        # ${code_verifier} derived from the raw string ${random}

        sso_auth_response = self.__send_token_request(form_values)

        if sso_auth_response.status_code == 200:
            data = sso_auth_response.json()
            access_token = data["access_token"]
            refresh_token = data["refresh_token"]
            auth_cache_data = self.__auth_cache.make_cache(access_token, refresh_token)
            return auth_cache_data
        else:
            self.__print_sso_failure(sso_auth_response)
            sys.exit(1)

    def re_auth(self, client_scopes, auth_cache_data=None):
        if auth_cache_data is None:
            auth_cache_data = self.__auth_cache.auth_cache
        refresh_token = self.__auth_cache.auth_cache["refresh_token"]
        client_id = self.__auth_cache.auth_cache["client_id"]

        sso_auth_response = self.__send_token_refresh(refresh_token, client_id, client_scopes)

        if sso_auth_response.status_code == 200:
            data = sso_auth_response.json()
            self.__auth_cache.refresh_cache(data["access_token"], data["refresh_token"], data["expires_in"])
            return auth_cache_data
        else:
            self.__print_sso_failure(sso_auth_response)
            sys.exit(1)
