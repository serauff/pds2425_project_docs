Template for the Read the Docs tutorial
=======================================

This GitHub template includes fictional Python library
with some basic Sphinx docs.

Read the tutorial here:

https://docs.readthedocs.io/en/stable/tutorial/


HOW TO USE
==========

`Link to the documentation <https://pds2425-project-docs.readthedocs.io/en/latest/index.html>`_

For commiting, select 'create a branch' when committing and create a pull request. Readthedocs will attempt to build the docs from the request. If it fails, close the pull request and read the build log from ReadTheDocs.
Otherwise, merge pull request.


For creating a new module, create module_name.py in docs/source
For creating a new page, create page_name.rst in docs/source
For adding the module to the Modules list, add the name of the module to the api.rst file (note: .. autofunction:: module_name.function_name has to be called somewhere for the module to appear)

quick reference to a function: "py:func:`function_module.function_name`

posting the function documentation to a rst document: ".. autofunction:: function_module.function_name"

reference to a document: ":doc:`doc_name`"

reference to a section within a doc ":ref:`ref_name`"

generate a reference label within a doc ".. _Reference Label"

generate a Heading -> "=" below the heading according to the heading length

generate a subheading -> "-" below the subheading accoring to the subheading length

