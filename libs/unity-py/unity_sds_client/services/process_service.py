import json
import requests
from typing import List

from unity_sps_ogc_processes_api_python_client.exceptions import NotFoundException

from unity_sds_client.unity_exception import UnityException
from unity_sds_client.unity_session import UnitySession
from unity_sds_client.resources.process import Process
from unity_sds_client.resources.job import Job, JobStatus
from unity_sds_client.utils.http import get_headers

import unity_sps_ogc_processes_api_python_client
from unity_sps_ogc_processes_api_python_client.rest import ApiException
from unity_sps_ogc_processes_api_python_client.models.process_list import ProcessList

import traceback


class ProcessService(object):
    """
    The ProcessService class is a wrapper to Unity's Science Processing Service endpoints.
    """

    def __init__(
            self,
            session: UnitySession,
            endpoint: str = None
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
            self.endpoint = self._session.get_unity_href() + self._session.get_venue_id() + "/wps/"

    def get_processes(self) -> List[Process]:
        """
        Returns a list of processes already deployed within SPS
        """
        token = self._session.get_auth().get_token()
        url = self.endpoint

        processes = []
        configuration = unity_sps_ogc_processes_api_python_client.Configuration(
            host=url,
            access_token=token
        )
        with unity_sps_ogc_processes_api_python_client.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = unity_sps_ogc_processes_api_python_client.DefaultApi(api_client)

            try:
                # Retrieve the list of available processes
                api_response = api_instance.process_list_processes_get()  # add auth
                for process in api_response.processes:
                    processes.append(
                        Process(
                            self._session,
                            self.endpoint,
                            process.id,
                            process.title,
                            process.description,
                            process.version,
                            process.keywords,
                            process.job_control_options
                        )
                    )
            except Exception as e:
                print(traceback.format_exc())
                print("Exception when calling DefaultApi->process_list_processes_get: %s\n" % e)
        #
        return processes

    def get_process(self, process_id: str) -> Process:
        """
        Returns a process deployed within SPS
        """

        token = self._session.get_auth().get_token()
        url = self.endpoint

        configuration = unity_sps_ogc_processes_api_python_client.Configuration(
            host=url,
            access_token=token
        )
        with unity_sps_ogc_processes_api_python_client.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = unity_sps_ogc_processes_api_python_client.DefaultApi(api_client)

            try:
                # Retrieve the list of available processes
                process_output = api_instance.process_description_processes_process_id_get(process_id)  # add auth
                return Process(
                    self._session,
                    self.endpoint,
                    process_output.id,
                    process_output.title,
                    process_output.description,
                    process_output.version,
                    process_output.keywords,
                    process_output.job_control_options,
                    inputs=process_output.inputs
                )
            except NotFoundException as nfe:
                raise UnityException(nfe.body)
            except Exception as e:
                print(traceback.format_exc())
                print("Exception when calling DefaultApi->process_list_processes_get: %s\n" % e)

    def get_jobs(self, process: Process = None):

        """
                Returns a process deployed within SPS
                """
        token = self._session.get_auth().get_token()
        url = self.endpoint
        jobs = []
        configuration = unity_sps_ogc_processes_api_python_client.Configuration(
            host=url,
            access_token=token
        )
        with unity_sps_ogc_processes_api_python_client.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = unity_sps_ogc_processes_api_python_client.DefaultApi(api_client)

            try:
                # Retrieve the list of available processes
                job_output = api_instance.job_list_jobs_get()  # add auth
                for j in job_output.jobs:
                    jobs.append(
                        Job(
                            self._session,
                            self.endpoint,
                            j.process_id,
                            j.job_id,
                            JobStatus(j.status.value)
                        )
                    )

            except NotFoundException as nfe:
                raise UnityException(nfe.body)
            except Exception as e:
                print(traceback.format_exc())
                print("Exception when calling DefaultApi->process_list_processes_get: %s\n" % e)

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
