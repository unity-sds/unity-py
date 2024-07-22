import os
import getpass
import json
import requests

from configparser import ConfigParser
from unity_sds_client.unity_environments import UnityEnvironments
from unity_sds_client.unity_exception import UnityException



class UnitySession(object):
    """
    passable session object containing configuration, auth objects, and environment.
    """

    def __init__(self, env: UnityEnvironments, config: ConfigParser):
        """initialize the unitySession object which holds configuration and auth objects.

        Parameters
        ----------
        env : str
            The environment in use (e.g. dev, test, ops)
        config : type
            the configuration object for the python configuration file.

        Returns
        -------
        class
            Class declaration, returns the initialized UnitySession class.

        """
        self._env = env
        self._config = config

        # set up unity authentication
        self._auth = UnityAuth(self._config.get(env, "client_id"), self._config.get(env, "auth_endpoint"))
        self._unity_href =  self._config.get(env, "unity_href")

        self._project = None
        self._venue = None
        self._venue_id = None

    def get_service_endpoint(self, section, setting):
        """convenience method for getting a configured item from the included configuration.


        Parameters
        ----------
        section : str
            The section of the configuration to read.
        setting : str
            The item within a block to read.

        Returns
        -------
        str
            the configuration entry

        """
        return self._config.get(section.upper(), setting)

    def get_unity_href(self):
        """convenience method for getting the unity href.

                Parameters
                ----------
                none

                Returns
                -------
                str
                    the url to the unity top url

                """
        return self._unity_href


    def get_auth(self):
        """Returns the auth object in use by the session

        Returns
        -------
        UnityAuth
            The authentication object which allows access to a "token" for api calls.

        """
        return self._auth

    def get_config(self):
        """Returns the configuration being used by the session

        Returns
        -------
        Config
            The configuration object which contains configuration information used for api calls.
        """
        return self._config

    def get_venue_id(self):
        if self._venue_id is None:
            if self._project is None or self._venue is None:
                raise UnityException("session variables project and venue or venue_id are required to interact with a "
                                     "processing service.")
            else:
                return self._project + "/" + self._venue
        else:
            return self._venue_id

class UnityAuth(object):
    """
    Unity Auth object for handling cognito authentication on behalf of all service wrappers.
    """

    _token = None
    _token_expiration = None

    # The auth_json is template for authorizing with AWS Cognito for a token that can be used for calls to the
    # data service. For now this is just an empty data structure. You will be prompted for your username and password
    # in a few steps.
    auth_json = '''{
         "AuthParameters" : {
            "USERNAME" : "",
            "PASSWORD" : ""
         },
         "AuthFlow" : "USER_PASSWORD_AUTH",
         "ClientId" : ""
      }'''

    def __init__(self, client_id, auth_endpoint):
        """initialize the Unity Auth class. The initialization looks for username/passwords in the following locations:
        1. The UNITY_USER and UNITY_PASSWORD environment variables.
        2. Prompt a user if no any of the previous fail

        Parameters
        ----------
        client_id : str
            The client ID of the unity API Gateway in use.
        auth_endpoint : str
            the https:// endpoint for use in obtaining a credential

        Returns
        -------
        UnityAuth
            The unityAuth object which allows access to a token

        """
        self._client_id = client_id
        self._endpoint = auth_endpoint

        # order of operations:
        # environment
        # netrc? //todo
        self._user = os.getenv('UNITY_USER', None)
        self._password = os.getenv('UNITY_PASSWORD', None)

        if None in [self._user, self._password]:
            username = input('Please enter your Unity username: ')
            password = getpass.getpass("Please enter your Unity password: ")
            self._user = username
            self._password = password

    def get_token(self):
        """Public convenience method for getting a token. This begins the
        process of returning an already created token or will create a new token if necessary

        Returns
        -------
        str
            The token for use in API calls

        """
        # If the token doesn't exist or the token is expired, create a new one.
        if self._token is None or UnityAuth._is_expired(self._token_expiration):
            self._get_unity_token()

        return self._token

    def _is_expired(expiration_date):
        """Convenience method for checking if a token is expired. static method

        Parameters
        ----------
        expiration_date : datetime
            expiration date of the token

        Returns
        -------
        bool
            True if the token is expired, False if still valid

        """
        if expiration_date is None:
            return True
        else:
            # TODO
            return False

    def _get_unity_token(self):
        """Queries the backing service for a new API Token

        Returns
        -------
        str
            the token generated. Also stored in the UnityAuth._token field

        """
        aj = json.loads(self.auth_json)
        aj['AuthParameters']['USERNAME'] = self._user
        aj['AuthParameters']['PASSWORD'] = self._password
        aj['ClientId'] =self._client_id
        try:
            response = requests.post(self._endpoint, headers={"Content-Type":"application/x-amz-json-1.1", "X-Amz-Target":"AWSCognitoIdentityProviderService.InitiateAuth"}, json=aj)
            json_resp = response.json()
            self._token = json_resp['AuthenticationResult']['AccessToken']
            self._token_expiration = json_resp['AuthenticationResult']['AccessToken']
        except:
            print("Error, check username and password and try again.")
        return self._token
