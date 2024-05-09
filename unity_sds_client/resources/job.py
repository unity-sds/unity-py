from __future__ import annotations

import traceback
from typing import TYPE_CHECKING
import requests
import unity_sps_ogc_processes_api_python_client
from unity_sps_ogc_processes_api_python_client.exceptions import NotFoundException

from unity_sds_client.unity_exception import UnityException
from unity_sds_client.unity_session import UnitySession
from unity_sds_client.resources.job_status import JobStatus
from unity_sds_client.utils.http import get_headers

if TYPE_CHECKING:
    from unity_sds_client.resources.process import Process


class Job(object):

    def __str__(self):
        return '''unity_sds_client.resources.Job(
    id="{}",
    process="{}",
    status="{}",
    inputs={}
)'''.format(
            self.id,
            self._process_id,
            self.status.value if self.status else "",
            self.inputs
        )

    def __init__(
            self,
            session: UnitySession,
            endpoint: str,
            process_id: str,
            job_id: int,
            status: JobStatus = None,
            inputs: object = None):
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
        self._process_id = process_id
        self.id = job_id
        self.status = status
        self.inputs = None

    def get_status(self):
        token = self._session.get_auth().get_token()
        url = self._endpoint
        configuration = unity_sps_ogc_processes_api_python_client.Configuration(
            host=url,
            access_token=token
        )
        with unity_sps_ogc_processes_api_python_client.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = unity_sps_ogc_processes_api_python_client.DefaultApi(api_client)
            try:
                # Retrieve the list of available processes
                job = api_instance.status_jobs_job_id_get(self.id)  # add auth
                return Job(
                    self._session,
                    self._endpoint,
                    job.process_id,
                    job.job_id,
                    JobStatus(job.status.value)
                )

            except NotFoundException as nfe:
                raise UnityException(nfe.body)
            except Exception as e:
                print(traceback.format_exc())
                print("Exception when calling DefaultApi->process_list_processes_get: %s\n" % e)
                raise UnityException(e.body)

        return None

    def get_result(self):
        token = self._session.get_auth().get_token()
        url = self._endpoint
        configuration = unity_sps_ogc_processes_api_python_client.Configuration(
            host=url,
            access_token=token
        )
        with unity_sps_ogc_processes_api_python_client.ApiClient(configuration) as api_client:
            api_instance = unity_sps_ogc_processes_api_python_client.DefaultApi(api_client)
            try:
                job_result = api_instance.results_jobs_job_id_results_get(self.id)  # add auth
                return job_result

            except NotFoundException as nfe:
                raise UnityException(nfe.body)
            except Exception as e:
                print(traceback.format_exc())
                print("Exception when calling DefaultApi->process_list_processes_get: %s\n" % e)
                raise UnityException(e.body)
        return None

    def dismiss(self):
        token = self._session.get_auth().get_token()
        url = self._endpoint
        configuration = unity_sps_ogc_processes_api_python_client.Configuration(
            host=url,
            access_token=token
        )
        with unity_sps_ogc_processes_api_python_client.ApiClient(configuration) as api_client:
            api_instance = unity_sps_ogc_processes_api_python_client.DefaultApi(api_client)
            try:
                job = api_instance.dismiss_jobs_job_id_delete(self.id)  # add auth
                return Job(
                    self._session,
                    self._endpoint,
                    job.process_id,
                    job.job_id,
                    JobStatus(job.status.value)
                )

            except NotFoundException as nfe:
                raise UnityException(nfe.body)
            except Exception as e:
                print(traceback.format_exc())
                print("Exception when calling DefaultApi->process_list_processes_get: %s\n" % e)
                raise UnityException(e.body)
        return None
