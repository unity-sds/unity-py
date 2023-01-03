import requests
from unity_py.unity_session import UnitySession
from unity_py.utils.http import get_headers


class JobService(object):
    """
    The JobService class is a wrapper to the job endpoint(s) within Unity.
    This wrapper interfaces with the Science Processing Service endpoints.

    The JobService class allows for the querying and deploying of processes.
    In addition, the querying, execution, monitoring of jobs and the job information retrieval.
    """

    def __init__(
        self,
        session: UnitySession,
        endpoint: str = None
    ):
        """
        Initialize the JobService class.

        Parameters
        ----------
        session : UnitySession
            The Unity Session that will be used to facilitate making calls to the SPS endpoints.

        Returns
        -------
        JobService
            The Job Service object.
        """
        self._session = session
        if endpoint is None:
            self.endpoint = self._session.get_service_endpoint("jobs", "sps_endpoint")

    def get_processes(self):
        """
        Returns a list of processes already deployed within SPS
        """

        url = self.endpoint + "processes"
        token = self._session.get_auth().get_token()
        headers = get_headers(token)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_result = response.json()['processes']

        return json_result
