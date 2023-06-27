# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

--------

## [0.1.1] - 2023-06-27

### Added
* Added pypi repository publication to unity-py repository [[7](https://github.com/unity-sds/unity-py/issues/7)].
* Added to_stac methods for writing STAC from unity-py resources (e.g. collection, dataset, datafiles)
* Added from_stac methods for creating unity-py resources (e.g. collection, dataset, datafiles) from STAC files
* Added capability to add files to published application catalogs
* added dependency on pystac > 1.7.3 to unity-py
* added addition of dataset properties to stac read/write
### Fixed
### Changed
* all assets written out to STAC items are made relative (if they are non-URIs, relative, or exist in the same directory tree of the STAC files)
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
