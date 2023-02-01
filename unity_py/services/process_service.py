import requests
from typing import List

from unity_py.unity_session import UnitySession
from unity_py.resources.process import Process
from unity_py.resources.job import Job, JobStatus
from unity_py.utils.http import get_headers

class ProcessService(object):
    """
    The ProcessService class is a wrapper to Unity's Science Processing Service endpoints.
    """

    def __init__(
        self,
        session:UnitySession,
        endpoint:str = None
    ):
        """
        Initialize the ProcessService class.

        Parameters
        ----------
        session : UnitySession
            The Unity Session that will be used to facilitate making calls to the SPS endpoints.
        endpoint : str
            An endpoint URL to override the endpoint specified in the package's config.

        Returns
        -------
        ProcessService
            The Process Service object.
        """
        self._session = session
        if endpoint is None:
            self.endpoint = self._session.get_service_endpoint("sps", "sps_endpoint")


    def get_processes(self) -> List[Process]:
        """
        Returns a list of processes already deployed within SPS
        """

        url = self.endpoint + "processes"
        token = self._session.get_auth().get_token()
        headers = get_headers(token)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        processes = []
        for process in response.json()['processes']:
            processes.append(
                Process(
                    self._session,
                    self.endpoint,
                    process['id'],
                    process['title'],
                    process['abstract'],
                    process['executionUnit'],
                    process['immediateDeployment'],
                    process['jobControlOptions'],
                    process['keywords'],
                    process['outputTransmission'],
                    process['owsContextURL'],
                    process['processVersion']
                )
            )

        return processes
    
    
    def get_jobs(self, process:Process):
    
        token = self._session.get_auth().get_token()
        headers = get_headers(token)
        job_url = self.endpoint + "processes/{}/jobs".format(process.id)
        response = requests.get(job_url, headers=headers)
        response.raise_for_status()

        jobs = []
        for item in response.json()['jobs']:
            jobs.append(
                Job(
                    self._session,
                    self.endpoint,
                    process,
                    item['jobID'],
                    JobStatus(item['status']),
                    item['inputs']
                )
            )

        return jobs