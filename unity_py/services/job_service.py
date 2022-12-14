import requests
from unity_py.unity_session import UnitySession


class JobService(object):
    """
    The JobService class is a wrapper to the job endpoint(s) within Unity. This wrapper interfaces with the Science Processing Service endpoints.

    The JobService class allows for the querying and deploying of processes. In addition, the querying, execution, monitoring of jobs and the job information retrieval.
    """

    def __init__(
        self,
        session: UnitySession
    ):
        """
        Initialize the JobService class.

        Parameters
        ----------
        session : UnitySession
            The Unity Session that will be used to facilitate making calls to the SPS endpoints.

        Returns
        -------
        JobSertvice
            The Job Service object.
        """
        self._session = session
