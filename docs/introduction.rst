Introduction
============

Names and acronyms
------------------

`SPD`: spectrual power distribution. This is a function of wavelength
:math:`\lambda`, and describes the power per unit area per unit wavelength of an
illumination.

`CMF`: color matching function. This is a function of wavelength :math:`\lambda`
describing the chromatic response of the "observer". A `CMF`
:math:`\bar{x}(\cdot)` will have response :math:`\bar{x}(\lambda)` at a
unit-power light of single wavelength :math:`\lambda`, and given a spectral
power distribution :math:`I(\lambda)`, the response will be :math:`X = \int
I(\lambda) \bar{x}(\lambda) d\lambda`.

Note that `SPD` and `CMF` should not be mistaken with each another. For example,
the CIE-RGB color space uses three monochromatic (single-wavelength) primary
colors, which means their `SPD`\s are delta functions, but their `CMF`\s are
not.

`LMS`: a color space represented by the response of three types of cones of the
human eye.

`WL`: wavelength list. This is a 1D ndarray with equally-spaced entries in
increasing order. The wavelength entries are in unit of nano-meter. A typically
used `WL` for visible light range is `np.arange(360, 831, 1)`.

`FW`: function of wavelength. For a single function, it is represented as a 1D
ndarray of length `N`. For multiple functions, they are represented as a 2D
ndarray of shape `(K, N)`, where `K` is the number of loaded functions, and
`fw[k]` is the `k`-th function, with `0 <= k < K`.
