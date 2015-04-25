Lenna or Lena is a standard test image widely used in the field of image
processing. See the following links for more details.
https://en.wikipedia.org/wiki/Lenna
http://www.cs.cmu.edu/~chuck/lennapg/


original.png:
Accessed from: https://upload.wikimedia.org/wikipedia/en/2/24/Lenna.png.
Accessed on: Apr 24, 2015.


sRGB.png:
The same as `original.png`, i.e. we assume the original image is in sRGB color
space. This is a groundless assumption though, because the image is digitized by
scanning, whose nonlinearity is not clear. We use this assumption for test and
demonstration purpose only.


sRGB-linear.png, CIE-XYZ.png, CIE-Lab.png:
The same image transformed into other color spaces:

  >>> srgb = imread("sRGB.png", np.float32)

  >>> srgblin = color_space_transform(srgb, "sRGB", "sRGB-linear")
  >>> imsave("sRGB-linear.png", srgblin, np.uint8)

  >>> xyz = color_space_transform(srgb, "sRGB", "CIE-XYZ")
  >>> imsave("CIE-XYZ.png", xyz, np.uint8)

  >>> lab = color_space_transform(srgb, "sRGB", "CIE-L*a*b*")
  >>> imsave("CIE-LAB.png", lab, np.uint8, "CIE-L*a*b*")
