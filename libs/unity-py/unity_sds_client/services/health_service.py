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

    def __str__(self):
        return self.generate_health_status_report()

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
    
    def generate_health_status_report(self):
        """
        Return a generated report of health status information
        """

        if self._health_statuses is None:
            self.get_health_status()

        health_status_title = "HEALTH STATUS REPORT"
        report = f"\n\n{health_status_title}\n"
        report = report + len(health_status_title) * "-" + "\n\n"
        for service in self._health_statuses:
            service_name = service["service"]
            report = report + f"{service_name}\n"
            for status in service["healthChecks"]:
                service_status = status["status"]
                service_status_date = status["date"]
                report = report + f"{service_status_date}: {service_status}\n"
            report = report + "\n"
        
        return report

    def print_health_status(self):
        """
        Print the health status report
        """
        print(f"{self.generate_health_status_report()}")
