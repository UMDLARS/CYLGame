Building the docs
=================

Setup
-----

This is a one time setup to install the required tools to build the
documentation into a virtual environment using pipenv.

1. Navigate to root directory of CYLGame repo.
2. ``pipenv install --dev``

Simple rebuild
--------------

Will rebuild html from ``.rst`` files but will not add newly created
Classes, Methods or Modules.

1. ``cd docs``
2. ``pipenv run make html``

Full rebuild
------------

A complete rebuild.

1. ``cd docs``
2. ``pipenv run sphinx-apidoc -f -o . ../CYLGame``
3. ``pipenv run make html``