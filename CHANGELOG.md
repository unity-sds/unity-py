# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## Unreleased [0.3.0]
### Added
### Fixed
* fixed an issue with encoding a json deploy request twice [71](https://github.com/unity-sds/unity-py/issues/71)
### Changed
* We now use the asset filename as the key into the assets, and use the "metadata" and "data" types as asset-roles: [69](https://github.com/unity-sds/unity-py/issues/69)
### Removed
### Security
### Deprecated


## [0.2.2] - 2024-01-03 
### Added
* Added project/venue support [5](https://github.com/unity-sds/unity-py/issues/58)
### Fixed 
### Changed
### Removed
### Security
### Deprecated

## [0.2.1] - 2023-11-29
### Added
* python code coverage via coveralls
### Fixed 
### Changed
* updated install to support python 3.8 and above.
### Removed
### Security
### Deprecated

## [0.2.1] - 2023-11-29
### Added
* python code coverage via coveralls
### Fixed 
### Changed
* updated install to support python 3.8 and above.
### Removed
### Security
### Deprecated


## [0.2.0] - 2023-08-10
### Added
* Added parsing of collection in stac items 
### Fixed
* fixed release workflow to test against `unity-sds-client` not `unity_py` 
### Changed
* updated package name so that imports reference `unity_sds_client` not `unity_py`
### Removed
### Security
### Deprecated

## [0.1.2] - 2023-06-28

### Added
* added method for retrieving datasets `Collection.datasets` from a collection
### Fixed
* Added some directory slash stripping to ensure no trailing slash when specifying "to_stac" output director
### Changed
* Changed name of package from unity-py to unity-sds-client

## [0.1.1] - 2023-06-27

### Added
* Added pypi repository publication to unity-py repository [[7](https://github.com/unity-sds/unity-py/issues/7)].
* Added to_stac methods for writing STAC from unity-py resources (e.g. collection, dataset, datafiles)
* Added from_stac methods for creating unity-py resources (e.g. collection, dataset, datafiles) from STAC files
* Added capability to add files to published application catalogs
* added dependency on pystac > 1.7.3 to unity-py
* added addition of dataset properties to stac read/write
* Added functionality to download latest available version of the application parameter files stored in the Dockstore [[30](https://github.com/unity-sds/unity-py/issues/30)]
### Fixed
* Added some directory slash stripping to ensure no trailing slash when specifying "to_stac" output director
### Changed
* all assets written out to STAC items are made relative (if they are non-URIs, relative, or exist in the same directory tree of the STAC files)
* Changed name of package from unity-py to unity-sds-client
### Removed
* Removed support for python 3.8

## [0.1.0] - 2023-04-17

### Added

#### Unity-Py Updates

* Added Services and Classes to ecapsulate funcionality per Unity Service Area
    1. Process Service & Class — Deploy a process, List processes, get metadata about a processes, query jobs per process, execute a job
    2. Job Class — Facilitate API calls to U-SPS to monitor jobs, get job results, or dismiss jobs.
    3. Application Service — Courtesy of U-ADS (James and Masha) (See Application Registry below).
* Mercury Dashboard Example
* Miscellaneous quality of life improvements to ease code developing (type hinting, annotations, etc)

#### Application Registry
* [unity-ads-deployment #79](https://github.com/unity-sds/unity-ads-deployment/issues/79) Add Dockstore API access to Unity.py
* [unity-ads-deployment #87](https://github.com/unity-sds/unity-ads-deployment/issues/87) Convert Unity.py Application Package API to use Hosted Workflows
