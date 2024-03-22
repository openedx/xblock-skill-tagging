Change Log
##########

..
   All enhancements and patches to skill_tagging will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
**********


[0.1.10] - 2024-03-22
************************************************

Changed
=======

* Remove log statement


[0.1.9] - 2024-03-20
************************************************

Changed
=======

* Pass course key as query param to taxonomy skills api


[0.1.8] - 2024-03-14
************************************************

Changed
=======

* Verification pipeline filter not run for proctored exam units


[0.1.7] - 2024-01-31
************************************************

Changed
=======

* Removed temporary logs


[0.1.6] - 2024-01-29
************************************************

Changed
=======

* Refactored logging and default run probability


[0.1.5] - 2024-01-25
************************************************

Changed
=======

* Logging aborted runs of the filter


[0.1.4] - 2024-01-22
************************************************

Changed
=======

* Added debug logs for filter runs


[0.1.3] - 2023-09-27
************************************************

Changed
=======

* Gate skills API call behind probablity check to reduce traffic.


[0.1.2] - 2023-08-18
************************************************

Added
=====

* Define Metaclass for XblockSkillTagging Mixin


[0.1.1] - 2023-06-14
************************************************

Added
=====

* Add temporary option to configure topic name for skill-verified event.

[0.1.0] - 2022-12-01
************************************************

Added
=====

* First release on PyPI.
