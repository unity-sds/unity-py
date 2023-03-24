import json
import logging
import requests

from functools import cached_property

from abc import ABC, abstractmethod
from enum import Enum

from attrs import define, field


class ApplicationCatalogAccessError(Exception):
    "An error occuring when attempting to access an application catalog"
    pass


class WorkflowType(Enum):
    """
    Encapsulates the types of workflows that Unity supports. This may be a subset of
    what the application catalog supports.
    """

    CWL = "CWL"


#
# Associations of the workflow type and corresponding Dockstore file types to be used to upload various format files
# for supported by Unity workflow types.
#
# Values come from repo:
#     https://github.com/dockstore/dockstore
#
# File:
#     https://github.com/dockstore/dockstore/blob/develop/dockstore-common/src/main/java/io/dockstore/common/DescriptorLanguage.java
#

# File type for the workflow parameter file
DockstoreFileType = {
    WorkflowType.CWL: "DOCKSTORE_CWL"
}

# File type for the JSON format file
DockstoreJSONFileType = {
    WorkflowType.CWL: "CWL_TEST_JSON"
}


@define
class ApplicationPackage(object):
    """
    Describes an application package either stored within an application catalog or that
    can be registered with an application catalog.
    """

    # Required arguments
    name: str
    source_repository: str
    workflow_path: str

    # Optional
    id: str = None  # Not yet commited to catalog
    is_published: bool = False
    description: str = ""

    workflow_type: str = field()

    @workflow_type.default
    def check_workflow_default(self):
        return "CWL"

    @workflow_type.validator
    def check_workflow_type(self, attribute, value):
        # This will raise a value error for us if value is not part of the WorkflowType Enum
        _ = WorkflowType(value)


@define
class DockstoreApplicationPackage(ApplicationPackage):
    """
    Adds extra information only available to a application package stored within Dockstore
    """

    # Closest Dockstore has to a name
    dockstore_info: dict = field(kw_only=True)


class ApplicationCatalog(ABC):
    """
    Abstract interface for interacting with an application catalog in an implementation agnostic way
    """

    def __init__(self):
        """
        """
        pass

    @abstractmethod
    def application(self, app_id):
        "Retrieve an ApplicationPackage from the catalog based on application id"
        pass

    @abstractmethod
    def application_list(self):
        "Return a list of ApplicationPackage objects representing the applications the catalog knows about"
        pass

    @abstractmethod
    def register(self, application, publish=True):
        "Register an ApplicationPackage object into the catalog, optionally publish it"
        pass

    @abstractmethod
    def unregister(self, application, delete=False):
        "Unregister an ApplicationPackage object into the catalog, optionally delete it instead of just unpublishing"
        pass


class DockstoreSourceMethod(Enum):
    """
    Encapsulates the enum strings that Dockstore uses for source control methods, translates from URL

    Values come from repo:
    https://github.com/dockstore/dockstore

    File:
    dockstore/dockstore-common/src/main/java/io/dockstore/common/SourceControl.java

    Parsing from a manualRegister in Dockstore occurs here:
    https://github.com/dockstore/dockstore/blob/7c4c08b9eed85334d5998bb02bc5b651f95e1f15/dockstore-webservice/src/main/java/io/dockstore/webservice/resources/WorkflowResource.java#L1298
    """

    DOCKSTORE = "dockstore.org"
    GITHUB = "github.com"
    BITBUCKET = "bitbucket.org"
    GITLAB = "gitlab.com"


class DockstoreAppCatalog(ApplicationCatalog):
    """
    Implementation of an application catalog interface to the Dockstore application
    """

    def __init__(self, api_url, token):
        """
        Creates a new DockstoreAppCatalog.

        api_url: Dockstore API URL
        token: Token is a string that can be obtained from the Dockstore user Account screen
        """

        self.api_url = api_url
        self.token = token

    @property
    def _headers(self):
        "Headers needed by the Dockstore API"

        return {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _get(self, request_url):

        request_url = request_url.strip("/")

        response = requests.get(f"{self.api_url}/{request_url}", headers=self._headers)

        if response.status_code != 200:
            raise ApplicationCatalogAccessError(f"GET operation to application catalog at {self.api_url}/{request_url} return unexpected status code: {response.status_code} with message: {response.content}")

        return response

    def _post(self, request_url, params=None, data=None):

        request_url = request_url.strip("/")

        if data is not None:
            response = requests.post(f"{self.api_url}/{request_url}", headers=self._headers, params=params, data=json.dumps(data))
        else:
            response = requests.post(f"{self.api_url}/{request_url}", headers=self._headers, params=params)

        if response.status_code != 200:
            raise ApplicationCatalogAccessError(f"POST operation to application catalog at {self.api_url}/{request_url} return unexpected status code: {response.status_code} with message: {response.content} using params: {params}")

        return response

    def _patch(self, request_url, data):
        """
        Submit patch request to upload files associated with the workflow to the Dockstore.
        """
        request_url = request_url.strip("/")

        response = requests.patch(f"{self.api_url}/{request_url}", headers=self._headers, data=json.dumps(data))

        if response.status_code != 200:
            raise ApplicationCatalogAccessError(f"PATCH operation to application catalog at {self.api_url}/{request_url} return unexpected status code: {response.status_code} with message: {response.content} using data: {data}")

        return response

    def _delete(self, request_url):
        """
        Submit DELETE request to the Dockstore API.
        """
        request_url = request_url.strip("/")

        response = requests.delete(f"{self.api_url}/{request_url}", headers=self._headers)

        if response.status_code != 200 and response.status_code != 204:
            raise ApplicationCatalogAccessError(f"DELETE operation to application catalog at {self.api_url}/{request_url} return unexpected status code: {response.status_code} with message: {response.content}")

        return response

    def _publish(self, application: DockstoreApplicationPackage, publish: bool = True):
        """
        Publish or unpublish the worksflow based on the "publish" input parameter value.
        """
        return self._post(f"/workflows/{application.id}/publish", data={"published": publish})

    @cached_property
    def _user_info(self):
        request_url = "/users/user"
        return self._get(request_url).json()

    @property
    def _user_id(self):
        return self._user_info['id']

    def _application_from_json(self, json_dict):
        """
        Collect application information from provided JSON dictionary
        (usually a response header for the request as submitted to the Dockstore).
        """
        # Name when using manual registry is an extra string given
        # after registry path
        name = json_dict['full_workflow_path'].split("/")[-1]

        return DockstoreApplicationPackage(id=str(json_dict['id']),
                                           name=name,
                                           source_repository=json_dict['gitUrl'],
                                           workflow_path=json_dict['workflow_path'],
                                           is_published=json_dict['is_published'],
                                           description=json_dict['description'],
                                           dockstore_info=json_dict)

    def application(self, app_id):
        """
        Get application information from the Dockstore based on the application ID.
        """
        request_url = f"/workflows/{app_id}"
        return self._application_from_json(self._get(request_url).json())

    def application_list(self, for_user=False, published=None):
        """
        For Dockstore optionally filter the application list for the user belonging to the token
        as well as restrict to just published applications.

        Unpublished applications can only be seen when using for_user=True
        """
        if for_user or (published is not None and not published):
            request_url = f"/users/{self._user_id}/workflows"

        else:
            request_url = "/workflows/published"

        app_list = []
        for app_info in self._get(request_url).json():
            # Searching for user workflows does not return the full
            # set of application information
            if for_user:
                app_obj = self.application(app_info['id'])

            else:
                app_obj = self._application_from_json(app_info)

            if published is None or published:
                app_list.append(app_obj)

        return app_list

    def register(self, application: DockstoreApplicationPackage, publish: bool = True):
        """
        Register new hosted workflow with the Dockstore.
        """
        # Set up request parameters for the Dockstore application as expected for
        # the hosted workflow
        params = {
            'name': application.name,
            'descriptorType': application.workflow_type,
        }
        logging.info(f'Using request parameters to register new workflow: {params}')

        request_url = "/workflows/hostedEntry"

        response = self._post(request_url, params)

        # Add id to the ApplicationPackage object
        new_app_id = response.json()['id']
        application.id = new_app_id

        # Optionally publish workflow
        if publish:
            self._publish(application, publish)

        return self.application(new_app_id)

    def uploadWorkflowParameterFile(self, application: DockstoreApplicationPackage, param_filename: str, workflow_path: str):
        """
        Upload local workflow parameter file "param_filename" as "workflow_path" to the hosted by Dockstore workflow.
        """
        data = None
        # Read contents of the local file
        with open(param_filename, 'r') as fhandle:
            data = fhandle.read()

        # Create JSON dictionary of parameters for the file
        params = {
            'path': workflow_path,
            'absolutePath': workflow_path,
            'content': data,
            'type': DockstoreFileType[application.workflow_type]
        }

        request_url = "/workflows/hostedEntry/{application.id}"

        self._patch(request_url, params, data)

    def uploadWorkflowJSONFile(self, application: DockstoreApplicationPackage, param_filename: str, workflow_path: str):
        """
        Upload local JSON file "param_filename" as "workflow_path" to the hosted by Dockstore workflow.
        """
        data = None
        # Read contents of the local file
        with open(param_filename, 'r') as fhandle:
            data = fhandle.read()

        # Create JSON dictionary of parameters for the file
        params = {
            'path': workflow_path,
            'absolutePath': workflow_path,
            'content': data,
            'type': DockstoreJSONFileType[application.workflow_type]
        }

        request_url = "/workflows/hostedEntry/{application.id}"

        self._patch(request_url, params, data)

    def unregister(self, application: DockstoreApplicationPackage, delete: bool = False):
        """
        Unregister existing application from the dockstore, and delete it from the Dockstore if
        'delete' input parameter is set to True.
        """
        # Unpublish application
        self._publish(application, publish=False)

        # Delete application
        if delete:
            self.delete(application)

    def delete(self, application: DockstoreApplicationPackage):
        """
        Delete existing application from the Dockstore.
        """
        self._delete(f"/workflows/hostedEntry/{application.id}")
