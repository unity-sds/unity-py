from enum import Enum


class JobStatus(Enum):
    """
    The JobServices class is used to specify a job status.
    """

    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    FAILED = "failed"
    RUNNING = "running"
    SUCCESSFUL = "successful"

    def from_status(status):
        try:
            job_status = JobStatus(status)
        except ValueError:
            raise ValueError(f"{status} is not a valid job_status")
        return job_status
