import requests
from unity_py.unity_session import UnitySession
from unity_py.resources.job import Job
from unity_py.utils.http import get_headers


class JobService(object):
    """
    The JobService class is a wrapper to the job endpoint(s) within Unity.
    This wrapper interfaces with the Science Processing Service endpoints.

    The JobService class allows for the querying and execution of jobs.
    In addition, job status and results can be retrieved.
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
        endpoint : str
            An endpoint URL to override the endpoint specified in the package's config.

        Returns
        -------
        JobService
            The Job Service object.
        """
        self._session = session
        if endpoint is None:
            self.endpoint = self._session.get_service_endpoint("sps", "sps_endpoint")
    
    def get_jobs_for_process(self, app_name):
    
        token = self._session.get_auth().get_token()
        headers = get_headers(token)
        job_url = self.endpoint + "/processes/{}/jobs".format(app_name)
        response = requests.get(job_url, headers=headers)
        response.raise_for_status()
        json_result = response.json()['jobs']

        #jobs = []
        #for job in response.json()['jobs']:
        #    jobs.append(
        #        Job(
        #            self._session,
        #            self.endpoint,
        #            job['jobID'],
        #            job['status'],
        #            job['inputs']
        #        )
        #    )


        return json_result
