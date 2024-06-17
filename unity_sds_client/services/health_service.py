from unity_sds_client.unity_session import UnitySession

class HealthService(object):
    """
    The HealthService class is a wrapper to Unity's Health API endpoints.
    """

    def __init__(
        self,
        session:UnitySession
    ):
        """
        Initialize the HealthService class.

        Parameters
        ----------
        session : UnitySession
            The Unity Session that will be used to facilitate making calls to the Health endpoints.

        Returns
        -------
        List
            List of applications and their health statses
        """

        self._health_statuses = None

    def get_health_status(self):
        """
        Returns a list of services and their respective health status
        """

        # Get Health Information
        # Stubbed in health data until Health API endpoint is available
        self._health_statuses = [
          {
            "service": "airflow",
            "landingPage":"https://unity.jpl.nasa.gov/project/venue/processing/ui",
            "healthChecks": [
              {
                "status": "HEALTHY",
                "date": "2024-04-09T18:01:08Z"
              }
            ]
          },
          {
            "service": "jupyter",
            "landingPage":"https://unity.jpl.nasa.gov/project/venue/ads/jupyter",
            "healthChecks": [
              {
                "status": "HEALTHY",
                "date": "2024-04-09T18:01:08Z"
              }
            ]
          },
          {
            "service": "other_service",
            "landingPage":"https://unity.jpl.nasa.gov/project/venue/other_service",
            "healthChecks": [
              {
                "status": "UNHEALTHY",
                "date": "2024-04-09T18:01:08Z"
              }
            ]
          }
        ]

        return self._health_statuses
    
    def print_health_status(self):

        if self._health_statuses is None:
            self.get_health_status()

        health_status_title = "HEALTH STATUSES"
        response = f"\n\n{health_status_title}\n"
        response = response + len(health_status_title) * "-" + "\n\n"
        for service in self._health_statuses:
            response = response + f"{service["service"]}\n"
            for status in service["healthChecks"]:
                response = response + f"{status["date"]}: {status["status"]}\n"
            response = response + "\n"
        
        print(response)