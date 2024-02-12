import json
import requests
from typing import List

from unity_sds_client.unity_session import UnitySession
from unity_sds_client.resources.process import Process
from unity_sds_client.resources.job import Job, JobStatus
from unity_sds_client.utils.http import get_headers

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
            # end point is the combination of the processes API and the project/venue
            # self._session.get_unity_href()
            self.endpoint = self._session.get_unity_href() + self._session.get_venue_id() + "/ades-wpst/"

    def get_processes(self) -> List[Process]:
        """
        Returns a list of processes already deployed within SPS
        """

        token = self._session.get_auth().get_token()
        headers = get_headers(token)
        url = self.endpoint + "processes"
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
    
    
    def get_process(self, process_id:str) -> Process:
        """
        Returns a list of processes already deployed within SPS
        """

        token = self._session.get_auth().get_token()
        headers = get_headers(token)
        url = self.endpoint + "processes/{}".format(process_id)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        process_json = response.json()['process']
        process = Process(
            self._session,
            self.endpoint,
            process_json['id'],
            process_json['title'],
            process_json['abstract'],
            process_json['executionUnit'],
            process_json['immediateDeployment'],
            process_json['jobControlOptions'],
            process_json['keywords'],
            process_json['outputTransmission'],
            process_json['owsContextURL'],
            process_json['processVersion']
        )

        return process
    
    
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
    
    def deploy_process(self, data):

        token = self._session.get_auth().get_token()
        headers = get_headers(token, {
            'Content-type': 'application/json'
        })
        url = self.endpoint + "processes"
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        return response
