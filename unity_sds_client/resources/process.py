import requests
from unity_sds_client.unity_session import UnitySession
from unity_sds_client.resources.job import Job
from unity_sds_client.utils.http import get_headers

class Process(object):

    def __str__(self):
        return '''unity_sds_client.resources.Process(
    id="{}",
    title="{}",
    abstract="{}",
    execution_unit="{}",
    immediate_deployment={},
    job_control_options={},
    keywords="{}",
    output_transmission={},
    ows_context_url="{}",
    process_version="{}"
)'''.format(
    self.id,
    self.title,
    self.abstract,
    self.execution_unit,
    self.immediate_deployment,
    self.job_control_options,
    self.keywords,
    self.output_transmission,
    self.ows_context_url,
    self.process_version
)

    def __init__(
        self,
        session:UnitySession,
        endpoint:str,
        id:str,
        title:str,
        abstract:str,
        execution_unit:str,
        immediate_deployment:bool,
        job_control_options:list,
        keywords:str,
        output_transmission:list,
        ows_context_url:str,
        process_version:str
    ):
        """
        Initialize the Process class.

        Parameters
        ----------
        session : UnitySession
            The Unity Session that will be used to facilitate making calls to the SPS endpoints.
        endpoint : str
            The endpoint to call for executing processes

        Returns
        -------
        Process
            The Process object.

        """

        self._session = session
        self._endpoint = endpoint
        self.id = id
        self.title = title
        self.abstract = abstract
        self.execution_unit = execution_unit
        self.immediate_deployment = immediate_deployment
        self.job_control_options = job_control_options
        self.keywords = keywords
        self.output_transmission = output_transmission
        self.ows_context_url = ows_context_url
        self.process_version = process_version

    def execute(self, data) -> Job:

        token = self._session.get_auth().get_token()
        headers = get_headers(token, {
            'Content-type': 'application/json'
        })
        url = self._endpoint + "processes/{}/jobs".format(self.id)
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        # Parse the job_id from the returned 'location' header
        job_location = response.headers['location']
        if "http://127.0.0.1:5000" in job_location:
            job_location = job_location.replace("http://127.0.0.1:5000/", self._endpoint)
        job_id = job_location.replace(url + "/","")

        job = Job(self._session, self._endpoint, self, job_id)

        return job