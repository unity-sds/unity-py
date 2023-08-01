import json
import os
import requests
from zipfile import ZipFile

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
    # Dockstore hard-codes the primary descriptor path for the hosted workflow
    workflow_path: str = 'Dockstore.cwl'
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

        Args:
            api_url: Dockstore API URL
            token: Token is a string that can be obtained from the Dockstore user Account screen
        """

        self.api_url = api_url
        self.token = token

    @property
    def _headers(self):
        """
        Headers needed by the Dockstore API.
        """
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    @property
    def _zip_headers(self):
        """
        Header used to download ZIP archive of the workflow descriptor and parameter files.
        """
        return {
            "Accept": "application/zip",
            "Authorization": f"Bearer {self.token}"
        }

    def _get(self, request_url, params=None):
        """
        Submit GET request to the Dockstore API.

        Args:
            request_url: String representing request URL
            params: Optional parameters dictionary for the request. Defaults to None.

        Raises:
            ApplicationCatalogAccessError: unexpected status code: XXX with message: YYY

        Returns:
            requests.Response
        """

        request_url = request_url.strip("/")

        response = requests.get(f"{self.api_url}/{request_url}", headers=self._headers, params=params)

        if response.status_code != 200:
            raise ApplicationCatalogAccessError(f"GET operation to application catalog at {self.api_url}/{request_url} return unexpected status code: {response.status_code} with message: {response.content}")

        return response

    def _get_zip(self, request_url):
        """
        Submit GET request to the Dockstore API to download ZIP archive of the workflow descriptor and parameter files.

        Args:
            request_url: String representing request URL

        Raises:
            ApplicationCatalogAccessError: unexpected status code: XXX with message: YYY

        Returns:
            requests.Response
        """
        request_url = request_url.strip("/")

        response = requests.get(f"{self.api_url}/{request_url}", headers=self._zip_headers)

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

        # 204 indicates that no action was taken
        if response.status_code != 200 and response.status_code != 204:
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

        return DockstoreApplicationPackage(
            id=str(json_dict['id']),
            name=name,
            source_repository=json_dict['gitUrl'],
            workflow_path=json_dict['workflow_path'],
            is_published=json_dict['is_published'],
            description=json_dict['description'],
            dockstore_info=json_dict
        )

    @staticmethod
    def _file_to_json(file_path: str, dockstore_path: str, file_format: str):
        """
        Generate JSON format of the file representation for the Dockstore request.

        Args:
            file_path: Path to the file to create JSON format request representation for.
                If None or empty filepath is provided, then "dockstore_path" file will be
                removed from the hosted workflow.
            dockstore_path: Path to the file in the Dockstore.
            file_format: Dockstore file type for the file.
        """
        # Dockstore requires absolute path for the file to be uploaded
        dockstore_file_path = f'/{dockstore_path}' if dockstore_path[0] != '/' else dockstore_path

        # Content of the file: None means to delete the file from the hosted workflow
        data = None
        if file_path is not None and len(file_path):
            # Read contents of the local file
            with open(file_path, 'r') as fhandle:
                data = fhandle.read()

        return {
            'path': dockstore_file_path,
            'absolutePath': dockstore_file_path,
            'content': data,
            'type': file_format
        }

    def application(self, app_id: int):
        """
        Get application information from the Dockstore based on the application ID.

        Args:
            app_id: Application ID.
        """
        request_url = f"/workflows/{app_id}"
        return self._application_from_json(self._get(request_url).json())

    def application_list(self, for_user: bool = False, published: bool = None):
        """
        For Dockstore optionally filter the application list for the user belonging to the token
        as well as restrict to just published applications.

        Unpublished applications can only be seen when using for_user=True.
        """
        request_url = "/workflows/published"

        if for_user or (published is not None and not published):
            request_url = f"/users/{self._user_id}/workflows"

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
        filename_map: dict = {},
        publish: bool = True
    ):
        """
        Register new hosted workflow within the Dockstore, upload workflow parameter files and publish
        the workflow if requested.

        Basename of each parameter file will be used as absolute path of the file within Dockstore. If other than basename
        path is preferred to store the file in the Dockstore, "filename_map" input argument should be used to provide
        preferred path of the file in the Dockstore. For example:
        {
            'local_path/step_one.cwl':    'l1/step_one.cwl',
            'local_path/params_one.json': 'l1_params/params_one.json'
        }

        Args:
            app_name: Application name to register within the Dockstore.
            app_type: Type of the application. Default is 'CWL'.
            cwl_files: List of CWL format parameter file paths to upload to the Dockstore. Default is an empty list.
            json_files: List of JSON format parameter file paths to upload to the Dockstore. Default is an empty list.
            filename_map: Mapping of parameter filenames on local file system vs. filename path as to appear in
                the Dockstore once the file is uploaded. Default is an empty map meaning that each file will be uploaded into
                the Dockstore using its basename.
            publish: Flag if registered application should be published within the Dockstore. Default is True meaning that
                application should be published once it's registered within the Dockstore. Applications that does not have
                any files uploaded to the Dockstore can't be published.
        """
        # Set up request parameters for the Dockstore application as expected for the hosted workflow
        params = {
            'name': app_name,
            'descriptorType': app_type,
        }

        request_url = "/workflows/hostedEntry"

        response = self._post(request_url, params)

        new_app = self._application_from_json(response.json())

        # Dockstore ID of newly registered application
        # new_app_id = response.json()['id']
        new_app_id = new_app.id

        self.upload_files(new_app, cwl_files, json_files, filename_map)

        # Optionally publish workflow: Dockstore allows to publish only workflows that have parameter files uploaded
        if publish:
            if len(cwl_files) or len(json_files):
                self._publish(new_app_id, publish)

            else:
                raise HostedWorkflowError('Can not publish hosted workflow (id={new_app_id}) as no parameter files have been uploaded')

        # Reload application information from the Dockstore
        return self.application(new_app_id)

    def upload_files(
        self,
        application,
        cwl_files: list = [],
        json_files: list = [],
        filename_map: dict = {}
    ):
        """
        Upload workflow parameter files for the workflow.

        Basename of each parameter file will be used as absolute path of the file within the Dockstore. If other
        than basename path is preferred to store the file in the Dockstore, "filename_map" input argument should
        be used to provide mapping of local file vs. preferred path of the file in the Dockstore. For example:
        {
            'local_path/step_one.cwl':    'l1/step_one.cwl',
            'local_path/params_one.json': 'l1_params/params_one.json'
        }

        Inputs:
        application: DockstoreApplicationPackage to upload the files for.
        cwl_files: List of CWL format parameter file paths to upload to the Dockstore. Default is an empty list.
        json_files: List of JSON format parameter file paths to upload to the Dockstore. Default is an empty list.
        filename_map: Mapping of parameter filenames on local file system vs. filename path as to appear in
            the Dockstore once the file is uploaded. Default is an empty map meaning that each file will be uploaded into
            the Dockstore using its basename.
        """
        app_type = application.workflow_type

        if len(cwl_files) or len(json_files):
            # Format contents of the parameter files for the request to upload all CWL and JSON files if any
            params = []

            for each_path in cwl_files:
                dockstore_path = os.path.basename(each_path) if each_path not in filename_map else filename_map[each_path]

                params.append(
                    DockstoreAppCatalog._file_to_json(
                        each_path,
                        dockstore_path,
                        DockstoreFileType[app_type]
                    )
                )

            for each_path in json_files:
                dockstore_path = os.path.basename(each_path) if each_path not in filename_map else filename_map[each_path]

                params.append(
                    DockstoreAppCatalog._file_to_json(
                        each_path,
                        dockstore_path,
                        DockstoreJSONFileType[app_type]
                    )
                )

            request_url = f"/workflows/hostedEntry/{application.id}"

            #  Upload the files
            self._patch(request_url, params)

        return

    def upload_parameter_file(self, application, param_filename: str, dockstore_filename: str = ''):
        """
        Upload local workflow parameter file "param_filename" to the hosted by Dockstore workflow.

        If "dockstore_filename" is an empty string than "param_filename" is uploaded into
        the Dockstore using its basename.

        To remove the file from the registered application just upload file of empy content to the Dockstore.
        """
        dockstore_path = os.path.basename(param_filename) if len(dockstore_filename) == 0 else dockstore_filename

        # Create JSON dictionary of parameters for the file
        params = [DockstoreAppCatalog._file_to_json(
                param_filename,
                dockstore_path,
                DockstoreFileType[application.workflow_type]
            )
        ]

        request_url = f"/workflows/hostedEntry/{application.id}"

        self._patch(request_url, params)

    def upload_json_file(self, application, param_filename: str, dockstore_filename: str = ''):
        """
        Upload local JSON file "param_filename" to the hosted by Dockstore workflow.

        If "dockstore_filename" is an empty string then "param_filename" is uploaded into
        the Dockstore using its basename.

        To remove the file from the registered application just upload file of an empy content to the Dockstore.
        """
        dockstore_path = os.path.basename(param_filename) if len(dockstore_filename) == 0 else dockstore_filename

        # Create JSON dictionary of parameters for the file
        params = [DockstoreAppCatalog._file_to_json(
                param_filename,
                dockstore_path,
                DockstoreJSONFileType[application.workflow_type]
            )
        ]

        request_url = f"/workflows/hostedEntry/{application.id}"

        self._patch(request_url, params)

    def get_application_version_info(self, application):
        """
        Retrieve version information for the workflow. Generated version information is
        a dictionary of the "db_version_id: workflow_version_id" content.
        This method identifies a mapping between database ID and the "name" of the workflow version
        as it appears in the Dockstore UI.
        Docktore uses DB version ID instead of the version ID as it appears in the Dockstore UI for the
        file retrieval.

        Args:
            application: DockstoreApplicationPackage object to retrieve version information for.

        Returns:
            dict
        """
        request_url = f"/workflows/{application.id}"

        params = {
            'include': 'versions'
        }

        response = self._get(request_url, params=params).json()

        application_versions = {}
        for each in response['workflowVersions']:
            application_versions[each['id']] = each['name']

        return application_versions

    def download_files(self, application, output_dir_path: str):
        """
        Download latest version of parameter files for the workflow.
        The method stores ZIP archive of all parameter files as well as
        all extracted files to the "output_dir_path" directory.

        Args:
            application: DockstoreApplicationPackage to download parameter files for.
            output_dir_path: Target directory for the workflow ZIP archive and extracted
                workflow files.
        """
        app_versions = self.get_application_version_info(application)

        # Pick the latest (maximum) workflow version - use DB ID for the version
        latest_version_id = max(app_versions.keys())

        # Create directory to store workflow files to if it does not exist.
        if not os.path.exists(output_dir_path):
            os.mkdir(output_dir_path)

        # Create ZIP filename with the version name as it appears in the Dockstore UI
        zip_file_path = os.path.join(
            output_dir_path,
            f'application_id{application.id}_v{app_versions[latest_version_id]}.zip'
        )

        # Download the zip archive file
        with open(zip_file_path, 'wb') as f:
            request_url = f"/workflows/{application.id}/zip/{latest_version_id}"
            response = self._get_zip(request_url)

            for chunk in response.iter_content(chunk_size=512):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        # Retrieve files from downloaded ZIP archive
        with ZipFile(zip_file_path) as fh:
            fh.extractall(output_dir_path)

        # Keep the ZIP archive in case it's needed

    def publish(self, application):
        """
        Publish the workflow.
        """
        self._publish(application.id, publish=True)

    def unpublish(self, application):
        """
        Unpublish the workflow.

        Dockstore does not allow to delete a hosted workflow, so we can only remove/add parameter files and
        publish/unpublish hosted workflows within Dockstore.
        """
        self._publish(application.id, publish=False)
