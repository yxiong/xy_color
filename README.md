xy_color
========

[<img src="https://api.travis-ci.org/yxiong/xy_color.svg?branch=master"
      alt="Build Status">](https://travis-ci.org/yxiong/xy_color)
[<img src="https://readthedocs.org/projects/xy-color/badge/?version=latest"
            alt="Documentation Status">](https://xy-color.readthedocs.org/)

Utilities and demos for color science in Python.

Author: Ying Xiong.  
Created: Oct 22, 2014.


Usage
-----

Install prerequisites: `pip install numpy scipy matplotlib`

Install `xy_python_utils`:

    git clone https://github.com/yxiong/xy_python_utils
    cd xy_python_utils
    python setup.py develop

Run tests: `cd xy_color; python -m unittest discover -p "*_test.py"`

Run demos: `cd xy_color; python demos.py`



Names and acronyms
------------------

SPD: spectrual power distribution. This is a function of wavelength $\lambda$,
and describes the power per unit area per unit wavelength of an illumination.

CMF: color matching function. This is a function of wavelength $\lambda$
describing the chromatic response of the 'observer'. A function $\bar{x}(\cdot)$
will have response $\bar{x}(\lambda)$ at a unit-power light of single wavelength
$\lambda$, and given a spectral power distribution $I(\lambda)$, the response
will be $$X = \int I(\lambda) \bar{x}(\lambda) d\lambda$$.

Note that SPD and CMF should not be mistaken with each another. For example, the
CIE-RGB color space uses three monochromatic (single-wavelength) primary colors,
which means their SPDs are delta functions, but their CMFs are not.

LMS: a color space represented by the response of three types of cones of the
human eye.

WL: wavelength list. This is a 1D ndarray with equally-spaced entries in
increasing order. The wavelength entries are in unit of nano-meter. A typically
used WL for visible light range is `np.arange(360, 831, 1)`.

FW(s): function(s) of wavelength. For a single function, it is represented as a
1D ndarray of length `N`. For multiple functions, they are represented as a 2D
ndarray of shape `(K, N)`, where `K` is the number of loaded functions, and
`fw[k]` is the `k`-th function, with `0 <= k < K`.
