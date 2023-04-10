import json
import os
import requests

from functools import cached_property

from abc import ABC, abstractmethod
from enum import Enum

from attrs import define, field


class ApplicationCatalogAccessError(Exception):
    "An error occuring when attempting to access an application catalog"
    pass


class HostedWorkflowError(Exception):
    "An error occuring when attempting to create a hosted workflow"
    pass


# String values that define workflow types
CWL_VALUE = "CWL"


class WorkflowType(Enum):
    """
    Encapsulates the types of workflows that Unity supports. This may be a subset of
    what the application catalog supports.
    """

    CWL = CWL_VALUE


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
    CWL_VALUE: 'DOCKSTORE_CWL'
}

# File type for the JSON format file based on the workflow type
DockstoreJSONFileType = {
    CWL_VALUE: 'CWL_TEST_JSON'
}


@define
class ApplicationPackage(object):
    """
    Describes an application package either stored within an application catalog or that
    can be registered with an application catalog.
    """

    # Required arguments
    name: str

    # Optional
    source_repository: str = None
    workflow_path: str = 'Dockstore.cwl'  # Dockstore hard-codes the primary descriptor path
    id: str = None  # Not yet commited to catalog
    is_published: bool = False
    description: str = ""

    workflow_type: str = field()

    @workflow_type.default
    def check_workflow_default(self):
        return CWL_VALUE

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
    def publish(self, application):
        "Publish an ApplicationPackage object into the catalog"
        pass

    @abstractmethod
    def unpublish(self, application):
        "Unpublish an ApplicationPackage object into the catalog"
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

    def _publish(self, app_id, publish: bool = True):
        """
        Publish or unpublish the worksflow based on the "publish" input parameter value.
        """
        return self._post(f"/workflows/{app_id}/publish", data={"publish": publish})

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
        (a response header for the request as submitted to the Dockstore).
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

    @staticmethod
    def _file_to_json(file_path: str, file_format: str):
        """
        Generate JSON format of the file representation for the Dockstore request.

        file_path: Path to the file create JSON format request representation for.
        file_format: Dockstore file type for the file.
        """
        # Read contents of the local file
        with open(file_path, 'r') as fhandle:
            data = fhandle.read()

            dockstore_path = file_path
            if dockstore_path[0] != '/':
                # Dockstore requires absolute path for the file to be uploaded
                dockstore_path = f'/{dockstore_path}'

            return {
                'path': dockstore_path,
                'absolutePath': dockstore_path,
                'content': data,
                'type': file_format
            }

    def application(self, app_id):
        """
        Get application information from the Dockstore based on the application ID.
        """
        request_url = f"/workflows/{app_id}"
        return self._application_from_json(self._get(request_url).json())

    def application_list(self, for_user: bool = False, published: bool = None):
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
            app_obj = None

            # Searching for user workflows does not return the full
            # set of application information
            if for_user:
                app_obj = self.application(app_info['id'])

            else:
                app_obj = self._application_from_json(app_info)

            # Check if all or only published applications are requested
            if app_obj is not None:
                if (published is None) or (published and app_obj.is_published):
                    app_list.append(app_obj)

        return app_list

    def register(
        self,
        app_name: str,
        app_type: str = CWL_VALUE,
        cwl_files: list = [],
        json_files: list = [],
        cwd: str = '.',
        publish: bool = True
    ):
        """
        Register new hosted workflow with the Dockstore, upload workflow parameter files and publish
        the workflow if requested.

        Inputs:
        app_name: Application name to register within the Dockstore.
        app_type: Type of the application. Default is 'CWL'.
        cwl_files: List of CWL format parameter file paths to upload to the Dockstore. Default is an empty list.
        json_files: List of JSON format parameter file paths to upload to the Dockstore. Default is an empty list.
        cwd: Base level directory that stores all CWL and JSON files to upload to the Dockstore. Default is '.'
             meaning the current directory. All "cwl_files" and "json_files" are relative to the "cwd" directory.
        publish: Flag if registered application should be published within the Dockstore. Default is True meaning that
            application should be published once it's registered within the Dockstore.
        """
        # Set up request parameters for the Dockstore application as expected for
        # the hosted workflow
        params = {
            'name': app_name,
            'descriptorType': app_type,
        }

        request_url = "/workflows/hostedEntry"

        response = self._post(request_url, params)

        # Dockstore ID of newly registered application
        new_app_id = response.json()['id']

        if len(cwl_files) or len(json_files):
            # Format contents of the parameter files for the request to upload all CWL and JSON files if any
            params = []

            current_dir = os.getcwd()

            try:
                # cd to the directory with parameter files (even if it's a current directory)
                os.chdir(cwd)

                for each_path in cwl_files:
                    params.append(
                        DockstoreAppCatalog._file_to_json(
                            each_path,
                            DockstoreFileType[app_type]
                        )
                    )

                for each_path in json_files:
                    params.append(
                        DockstoreAppCatalog._file_to_json(
                            each_path,
                            DockstoreJSONFileType[app_type]
                        )
                    )

            finally:
                # Change back to original directory
                os.chdir(current_dir)

            request_url = f"/workflows/hostedEntry/{new_app_id}"

            #  Upload the files
            self._patch(request_url, params)

        # Optionally publish workflow: Dockstore allows to publish only workflows that have parameter files uploaded
        if publish:
            if len(cwl_files) or len(json_files):
                self._publish(new_app_id, publish)

            else:
                raise HostedWorkflowError('Can not publish hosted workflow (id={new_app_id}) as no parameter files have been uploaded')

        return self.application(new_app_id)

    def uploadParameterFile(self, application, param_filename: str):
        """
        Upload local workflow parameter file "param_filename" to the hosted by Dockstore workflow.

        To remove the file from the registered application just upload file of empy content to the Dockstore.
        """
        # Create JSON dictionary of parameters for the file
        params = [DockstoreAppCatalog._file_to_json(
                param_filename,
                DockstoreFileType[application.workflow_type]
            )
        ]

        request_url = f"/workflows/hostedEntry/{application.id}"

        self._patch(request_url, params)

    def uploadJSONFile(self, application, param_filename: str):
        """
        Upload local JSON file "param_filename" to the hosted by Dockstore workflow.

        To remove the file from the registered application just upload file of empy content to the Dockstore.
        """
        # Create JSON dictionary of parameters for the file
        params = [DockstoreAppCatalog._file_to_json(
                param_filename,
                DockstoreJSONFileType[application.workflow_type]
            )
        ]

        request_url = f"/workflows/hostedEntry/{application.id}"

        self._patch(request_url, params)

    def publish(self, application):
        """
        Publish the worksflow.
        """
        self._publish(application.id, publish=True)

    def unpublish(self, application):
        """
        Unpublish the worksflow.

        Dockstore does not allow to delete a hosted workflow, so we can only remove/add parameter files and
        publish/unpublish hosted workflows within Dockstore.
        """
        self._publish(application.id, publish=False)
