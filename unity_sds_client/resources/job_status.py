from enum import Enum


class JobStatus(Enum):
    """
    The JobServices class is used to specify a job status.
    """

    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    FAILED = "failed"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
