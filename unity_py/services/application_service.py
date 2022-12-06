import json
import requests

from functools import cached_property

from abc import ABC, abstractmethod
from enum import Enum

from attrs import define, field
from giturlparse import parse as parse_giturl


class ApplicationCatalogAccessError(Exception):
    "An error occuring when attempting to access an application catalog"
    pass


class WorkflowType(Enum):
    """
    Encapsulates the types of workflows that Unity supports. This may be a subset of
    what the application catalog supports.
    """
    
    CWL = "CWL"


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
    id: str = None # Not yet commited to catalog
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
    
    def _delete(self, request_url):
        
        request_url = request_url.strip("/")
        
        response = requests.delete(f"{self.api_url}/{request_url}", headers=self._headers)
            
        if response.status_code != 200 and response.status_code != 204:
            raise ApplicationCatalogAccessError(f"DELETE operation to application catalog at {self.api_url}/{request_url} return unexpected status code: {response.status_code} with message: {response.content}")
            
        return response
    
    @cached_property
    def _user_info(self):
        request_url = "/users/user"
        return self._get(request_url).json()
    
    @property
    def _user_id(self):
        return self._user_info['id']
    
    def _application_from_json(self, json_dict):
        
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
    
    def register(self, application, publish=True):
        
        # Parse application source repository into components used for
        # Dockstore /manualRegister
        repo_attrs = parse_giturl(application.source_repository)
        
        git_registry = repo_attrs.host
        git_version_control = DockstoreSourceMethod(repo_attrs.host).name
        organization = repo_attrs.owner
        repository_base = repo_attrs.repo
        
        # Extract other values in the form Dockstore expects
        descriptor_type = application.workflow_type

        workflow_path = application.workflow_path
        workflow_name = application.name

        params = {
            'workflowRegistry': git_version_control,
            'workflowPath': f"{organization}/{repository_base}",
            'defaultWorkflowPath': workflow_path,
            'workflowName': workflow_name,
            'descriptorType': descriptor_type,
            #'defaultTestParameterFilePath':, 
        }

        request_url = "/workflows/manualRegister"
        
        response = self._post(request_url, params)
        
        # Add id to the ApplicationPackage object
        new_app_id = response.json()['id']
        
        # Refresh workflow to pull in CWL files
        self._get(f"/workflows/{new_app_id}/refresh")

        # Optionally publish workflow
        if publish:
            self._post(f"/workflows/{new_app_id}/publish", data={"published": True})
        
        return self.application(new_app_id)

    def unregister(self, application, delete=False):
    
        # Unpublish application
        self._post(f"/workflows/{application.id}/publish", data={"published": False})
        
        # Refresh the application object to consistently remove publish flag
        application = self.application(application.id)
    
        # Optionally completely delete from Dockstore
        if delete:
            # Convert back to stub so it can be removed
            self._get(f"/workflows/{application.id}/restub")
    
            # Parse application source repository into components used for
            # Dockstore /delete
            repo_attrs = parse_giturl(application.source_repository)

            repository_base = repo_attrs.repo
            workflow_name = application.name

            git_registry = repo_attrs.host
            organization = repo_attrs.owner

            # Encode / in name / = %2F
            request_repo = f"{repository_base}%2F{workflow_name}"
            
            request_url = f"/workflows/registries/{git_registry}/organizations/{organization}/repositories/{request_repo}"
            
            self._delete(request_url)
            
            application.id = None
            application.dockstore_info = None
        
        return application