.. _Development:continous-integration:

Continuous Integration (CI)
###########################

.. NOTE::
   At the moment, there is no triggering mechanism set up between different GitHub repositories.
   All the workflows in this repo are triggered by push events, CRON jobs, or manually.

.. _Development:continous-integration:status:

Status
======

.. include:: ../CIStatus.inc

.. _Development:continous-integration:structure:

Structure
=========

The continuous integration in this repository is based on commands ``pull`` and ``build`` provided by the Python utils
(see :ref:`Development:utils:pyHDLC:Reference`); so, contributors can execute exactly the same commands locally, for
debugging and development.
However, there are several layers of complexity around those commands, in order to precisely decide which images to
build in each workflow/job execution.

.. figure:: ../_static/img/continuous_integration.svg
  :name: img-ci
  :alt: Structure of the Continuous Integration (CI)
  :width: 100%
  :align: center

  Structure of the Continuous Integration (CI) in this repository.

As shown in :numref:`img-ci`, the following wrappers are used:

.. TIP::
  In :gh:`pyTooling/Actions: Context <pyTooling/Actions/#context>`, details about Action and Workflow kinds supported in
  GitHub Actions are explained.
  See also `Workflow syntax for GitHub Actions <https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions>`__.

* :ghsrc:`build-test-release <utils/build-test-release/action.yml>` is a local Composite Action with three steps,
  including setup, pulling/building/testing and releasing.
* :ghsrc:`Common <.github/workflows/common.yml>` is a Reusable Workflow with two jobs.
  The first job, named *matrix*, uses ``pyHDLC jobs`` to generate a list of tasks to be used in the second job, named
  *jobs* (see `docs.github.com: Workflow syntax for GitHub Actions » jobs.<job_id>.outputs <https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idoutputs>`__).
  Then, the Composite Action is used in each of the dynamically generated jobs.
* :ghsrc:`Dispatch <.github/workflows/dispatch.yml>` is a Dispatchable Workflow, which calls the Reusable Workflow.
  In practice, *Dispatch* documents the internal triggering interface, but it is not used explicitly.
  There are dozens of workflows (one per tool or group) which are equivalent to *Dispatch* with some hardcoded inputs.
  Those are triggered through scheduled (CRON) events, by pushes, by Pull Requests or manually.

Since most of the complexity of the orchestration is defined in the YAML configuration file used by pyHDLC, reading
:ref:`Development:configuration` is strongly recommended.
As shown in :numref:`img-ci`, data from the configuration file is used in the Reusable Workflow *Common* and in the
build step of the Composite Action *build-test-release*.
