skill_tagging
#############################

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

Overview
********

Django app for fetching and verifying tags/skills for video and vertical/unit
XBlocks. It implements two openedx_filters pipelines to inject a form into the end
unit XBlocks and video XBlocks.

.. image:: https://user-images.githubusercontent.com/10894099/210078679-3cbac3d1-55a7-4fba-b841-7fb4468f32c5.png
   :target: https://user-images.githubusercontent.com/10894099/210078679-3cbac3d1-55a7-4fba-b841-7fb4468f32c5.png
   :alt: vertical block verification form

.. image:: https://user-images.githubusercontent.com/10894099/212285572-efa5cfd5-e9c5-411d-8d15-541c43445ec0.png
   :target: https://user-images.githubusercontent.com/10894099/212285572-efa5cfd5-e9c5-411d-8d15-541c43445ec0.png
   :alt: video block verification form

More information about the XBlock skill tagging design can be found in this
`ADR`_.

.. _ADR: https://github.com/openedx/taxonomy-connector/blob/master/docs/decisions/0001-xblock-skill-tagging-design.rst


Getting Started
***************

To install ``skill_tagging`` in `edx-platform`_, run

.. code-block::

   pip install skill_tagging

   # to install a development version locally in devstack
   # clone this repo in `<devstack_base_dir>/src` directory and run
   pip install -e /edx/src/xblock-skill-tagging

.. _edx-platform: https://github.com/openedx/edx-platform

This repo depends on discovery service for fetching skills/tags for a given
XBlock which depends on `taxonomy-connector`_ plugin for generating and serving these
tags. Setup ``taxonomy-connector`` plugin in `course-discovery`_ by installing it
via pip:

.. code-block::

   pip install taxonomy-connector

   # to install a development version locally in devstack
   # clone this repo in `<devstack_base_dir>/src` directory and run
   pip install -e /edx/src/taxonomy_connector

.. _taxonomy-connector: https://github.com/openedx/taxonomy-connector
.. _course-discovery: https://github.com/openedx/course-discovery

Whenever a user verifies tags/skills for an XBlock, ``skill_tagging`` `emits`_ an
openedx_event called ``XBLOCK_SKILL_VERIFIED``. This event needs to be consumed
by course discovery to make sure that the verification count is incremented for
that skill/tag.

To produce and consume this event, setup an implementation of event bus
like `event_bus_kafka`_ or `event_bus_redis`_. `How to start using the Event Bus`_
has detailed information on setting up event bus. The host would be
``edx-platform`` while ``course-discovery`` will be the consumer for the event
bus.

.. _emits: https://github.com/openedx/xblock-skill-tagging/blob/main/skill_tagging/handlers.py
.. _event_bus_kafka: https://github.com/openedx/event-bus-kafka
.. _event_bus_redis: https://github.com/openedx/event-bus-redis
.. _How to start using the Event Bus: https://openedx.atlassian.net/wiki/spaces/AC/pages/3508699151/How+to+start+using+the+Event+Bus

Configuration
=============

Add following configuration values to the host django settings, i.e. LMS
settings: ``lms/envs/common.py``

.. code-block:: python

   from .common import XBLOCK_MIXINS
   # Below mixin adds the ability to fetch skills/tags from discovery and update them.
   XBLOCK_MIXINS += ('skill_tagging.skill_tagging_mixin.SkillTaggingMixin',)
   # Set below url to point to discovery service.
   TAXONOMY_API_BASE_URL='http://edx.devstack.discovery:18381'
   # Configure the maximum number skills/tags to display in the form for a given xblock.
   TAXONOMY_API_SKILL_PAGE_SIZE=20
   # Copy this as is, this configures the required openedx_filters.
   OPEN_EDX_FILTERS_CONFIG = {
       "org.openedx.learning.vertical_block.render.completed.v1": {
           "fail_silently": False,
           "pipeline": [
               "skill_tagging.pipeline.AddVerticalBlockSkillVerificationSection",
           ]
       },
       "org.openedx.learning.vertical_block_child.render.started.v1": {
           "fail_silently": False,
           "pipeline": [
               "skill_tagging.pipeline.AddVideoBlockSkillVerificationComponent",
           ]
       }
   }
   # helps to configure probability of displaying the verification forms. Values in range 0 to 1 are allowed, where 0
   # means never and 1 means always display. Default value is 0.5 i.e. 50% chance of displaying the form.
   SHOW_SKILL_VERIFICATION_PROBABILITY = 0.5
   # Optionally update topic name for verification event emitted when a user verifies tags for an xblock.
   EVENT_BUS_XBLOCK_VERIFICATION_TOPIC = "learning-custom-xblock-skill-verfied"


Developing
==========

One Time Setup
--------------
.. code-block::

  # Clone the repository
  git clone git@github.com:openedx/xblock-skill-tagging.git
  cd xblock-skill-tagging

  # Set up a virtualenv using virtualenvwrapper with the same name as the repo and activate it
  mkvirtualenv -p python3.12 xblock-skill-tagging


Every time you develop something in this repo
---------------------------------------------
.. code-block::

  # Activate the virtualenv
  workon xblock-skill-tagging

  # Grab the latest code
  git checkout main
  git pull

  # Install/update the dev requirements
  make requirements

  # Run the tests and quality checks (to verify the status before you make any changes)
  make validate

  # Make a new branch for your changes
  git checkout -b <your_github_username>/<short_description>

  # Using your favorite editor, edit the code to make your change.
  vim ...

  # Run your new tests
  pytest ./path/to/new/tests

  # Run all the tests and quality checks
  make validate

  # Commit all your changes
  git commit ...
  git push

  # Open a PR and ask for review.


Deploying
=========

This package is automatically published to pypi whenever a new tag is pushed to the repository.

Getting Help
************

Documentation
=============

Published documentation is not available.

More Help
=========

If you're having trouble, we have discussion forums at
https://discuss.openedx.org where you can connect with others in the
community.

Our real-time conversations are on Slack. You can request a `Slack
invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to open an issue in this
repository with as many details about the issue you are facing as you
can provide.

https://github.com/openedx/xblock-skill-tagging/issues

For more information about these options, see the `Getting Help`_ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/
.. _Getting Help: https://openedx.org/getting-help

License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://open-edx-backstage.herokuapp.com/catalog/default/component/xblock-skill-tagging

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@openedx.org.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/skill_tagging.svg
    :target: https://pypi.python.org/pypi/skill_tagging/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/openedx/xblock-skill-tagging/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/openedx/xblock-skill-tagging/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/openedx/xblock-skill-tagging/coverage.svg?branch=main
    :target: https://codecov.io/github/openedx/xblock-skill-tagging?branch=main
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/xblock-skill-tagging/badge/?version=latest
    :target: https://xblock-skill-tagging.readthedocs.io/en/latest/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/skill_tagging.svg
    :target: https://pypi.python.org/pypi/skill_tagging/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/openedx/xblock-skill-tagging.svg
    :target: https://github.com/openedx/xblock-skill-tagging/blob/main/LICENSE.txt
    :alt: License

.. TODO: Choose one of the statuses below and remove the other status-badge lines.
.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
