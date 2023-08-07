from __future__ import annotations
from typing import TYPE_CHECKING
import requests

from unity_sds_client.unity_session import UnitySession
from unity_sds_client.resources.job_status import JobStatus
from unity_sds_client.utils.http import get_headers

if TYPE_CHECKING:
    from unity_sds_client.resources.process import Process


class Job(object):

    def __str__(self):
        return '''unity_sds_client.resources.Job(
    id="{}",
    status="{}",
    inputs={}
)'''.format(
    self.id,
    self.status.value if self.status else "",
    self.inputs
)

    def __init__(self, session: UnitySession, endpoint:str, process:Process, id:int, status:JobStatus = None, inputs:object = None):
        """
        Initialize the Job class.

        Parameters
        ----------
        session : UnitySession
            The Unity Session that will be used to facilitate making calls to the SPS endpoints.
        endpoint : str
            The endpoint to call for SPS.
        process : Process
            The process associated with this Job
        id : int
            The identifier associated with this Job
        status : JobStatus
            The status of this job
        inputs : object
            The input data used for this job

        Returns
        -------
        Job
            The Job object.

        """

        self._session = session
        self._endpoint = endpoint
        self._process = process
        self.id = id
        self.status = status
        self.inputs = None

    def get_status(self):

        token = self._session.get_auth().get_token()
        headers = get_headers(token)
        url = self._endpoint + "processes/{}/jobs/{}".format(self._process.id, self.id)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        self._status = JobStatus(response.json()['status'])

        return self._status

    def get_result(self):
    
        token = self._session.get_auth().get_token()
        headers = get_headers(token)
        url = self._endpoint + "processes/{}/jobs/{}/result".format(self._process.id, self.id)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_result = response.json()
        
        return json_result

    def dismiss(self):
    
        token = self._session.get_auth().get_token()
        headers = get_headers(token)
        job_url = self._endpoint + "processes/{}/jobs/{}".format(self._process.id, self.id)
        response = requests.delete(job_url, headers=headers)
        response.raise_for_status()
        json_result = response.json()['statusInfo']
        
        return json_result
