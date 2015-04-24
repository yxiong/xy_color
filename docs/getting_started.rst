Getting Started
===============

Install `xy_python_utils` as a prerequisite::

  git clone https://github.com/yxiong/xy_python_utils
  cd xy_python_utils
  python setup.py develop
  cd ..

Install this package in development mode::

  python setup.py develop

Run demos::

  cd xy_color
  python demos.py

Run unit tests::

  cd xy_color
  python -m unittest discover -p "*_test.py"
  cd ..

Generate documentation::

  cd docs
  make html
  cd ..
