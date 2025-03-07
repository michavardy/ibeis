# Changelog

We are currently working on porting this changelog to the specifications in
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Version 2.3.1]  - Released 2023-01-29

### Changed
* Ported some utool code to ibeis.util for more direct coupling with this
  library.
* ibeis will no longer prompt you for a workdir if one is not set. It will just use `ibeis_default_workdir` in the current directory. Old behavior can be restored by setting the `LEGACY_WORKDIR_BEHAVIOR` environment variable.

### Fixed
* Fixed issue with numpy 1.24
* Numpy dtype issues
* Fixed 3.11 change with random.Random

### Changed
* Added 3.11 support
* Added loose / strict dependency versioning


## [Version 2.2.6]  - Released 2020-July-4

### Fixed
* Fix np.float, np.bool, and np.int issue
* Fixed distutils version issue

## [Version 2.2.5]  - Released 2020-July-4

### Fixed

* Warnings about "is" instead of "==" for integer comparisons in web stuff.
* Update to `dtool_ibeis` 1.0.2, which fixes the issue with dumping CSV tables.


### Changed
* `dump_database_csv` now returns the dump directory. 


## [Version 2.2.4]  - Released 2020 Jan 25

### Fixed
* pypi deps should now be fixed


## [Version 2.1.0]

### Added
    * First semi-usable pip release

