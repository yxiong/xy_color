#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Oct 23, 2014.

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from xy_python_utils.matplotlib_utils import *
from data import *
from utils import *

def display_cmfs(cmfs):
    plt.plot(cmfs[:,0], cmfs[:,1], 'r')
    plt.plot(cmfs[:,0], cmfs[:,2], 'g')
    plt.plot(cmfs[:,0], cmfs[:,3], 'b')

def demo_show_spectral_functions():
    fig = plt.figure()
    # Plot CIE-XYZ color matching functions.
    ax = fig.add_subplot(121)
    xyz_cmfs = load_xyz_cmfs()
    display_cmfs(xyz_cmfs)
    ax.set_title("CIE-XYZ color matching functions.")
    # Plot D65 spectral power distribution.
    ax = fig.add_subplot(122)
    d65_spd = load_d65_spd()
    ax.plot(d65_spd[:,0], d65_spd[:,1])
    ax.set_title("CIE Standard Illuminant D65")

    plt.show()
    # TODO: make more subplots, say LMS, CIE-RGB, etc.

def demo_show_monochromatic_3d():
    ax = plt.figure().gca(projection="3d")

    # Plot the 3D curve of monochromatic colors.
    xyz_cmfs = load_xyz_cmfs()
    for i in xrange(xyz_cmfs.shape[0]-1):
        color = xyz_cmfs[i, 1:] / np.sum(xyz_cmfs[i, 1:])
        ax.plot(xyz_cmfs[i:i+2,1], xyz_cmfs[i:i+2,2], xyz_cmfs[i:i+2,3],
                color = color, linewidth = 3)

    # Plot the intersection of $$X + Y + Z = 1$$ plane with axes.
    ax.plot(np.array([1.0, 0.0, 0.0, 1.0]),
            np.array([0.0, 1.0, 0.0, 0.0]),
            np.array([0.0, 0.0, 1.0, 0.0]),
            color='k', label="X+Y+Z=1")

    # Plot the projection of monochromatic colors onto the $$X + Y + Z = 1$$
    # plane.
    xyz_cmfs_proj = np.zeros(xyz_cmfs.shape)
    xyz_cmfs_proj[:,0] = xyz_cmfs[:,0]
    s = np.sum(xyz_cmfs[:, 1:], 1)
    for c in xrange(1, 4):
        xyz_cmfs_proj[:,c] = xyz_cmfs[:,c] / s
    ax.scatter(xyz_cmfs_proj[:,1], xyz_cmfs_proj[:,2], xyz_cmfs_proj[:,3],
               s = 3, color = xyz_cmfs_proj[:, 1:])

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.legend()
    axes_equal_3d(ax)
    plt.show()

def normalize_image_by_max_color(image):
    """Normalize each pixel of an image by the maximum color channel. The input
    image will be modified in place."""
    image_max = np.max(image[:,:,:3], axis = 2)
    for c in xrange(3):
        image_c = image[:,:,c]
        image_c[image_max>0] = image_c[image_max>0] / image_max[image_max>0]
        image[:,:,c] = image_c
    return image

def plot_triangle(ax, tri, *args, **kw):
    """Plot a triangle in the axis."""
    assert tri.shape == (2,3)
    ax.plot((tri[0,0], tri[0,1], tri[0,2], tri[0,0]),
            (tri[1,0], tri[1,1], tri[1,2], tri[1,0]), *args, **kw)

def integrate_spd_with_cmfs(spd, cmfs):
    """Integrate an SPD with a set of CMFs."""
    assert len(spd.shape) == 2 and spd.shape[1] == 2
    assert len(cmfs.shape) == 2 and cmfs.shape[1] == 4
    assert np.all(np.abs(spd[:,0] - cmfs[:,0]) < 1.0e-6)
    return np.array([np.sum(spd[:,1] * cmfs[:,1]),
                     np.sum(spd[:,1] * cmfs[:,2]),
                     np.sum(spd[:,1] * cmfs[:,3])])

def demo_show_horseshoe():
    # Load the CMFs of monochromatic colors.
    xyz_cmfs = load_xyz_cmfs()
    xy_wavelength = np.zeros((xyz_cmfs.shape[0], 3))
    xy_wavelength[:, :2] = normalize_rows(xyz_cmfs[:, 1:])[:, :2]
    xy_wavelength[:, 2] = xyz_cmfs[:, 0]

    # Create a horseshoe image with unit luminance. We first create the image in
    # CIE xyY color space, where the luminance component Y = 1.0. The image also
    # has a alpha channel marking valid v.s. invalid pixels.
    num_samples = 1001
    horseshoe_xyy = np.zeros((num_samples, num_samples, 4))
    (xx,yy) = np.meshgrid(np.linspace(0,1,num_samples),
                          np.linspace(0,1,num_samples))
    horseshoe_xyy[:,:,0] = xx
    horseshoe_xyy[:,:,1] = yy
    horseshoe_xyy[:,:,2] = 1.0
    horseshoe_xyy[:,:,3] = 1.0

    # Keep colors that are inside the horseshoe only.
    inside = xy_inside_horseshoe(xx, yy, xy_wavelength[:, :2])
    for c in xrange(4):
        horseshoe_c = horseshoe_xyy[:,:,c]
        horseshoe_c[~inside] = 0.0
        horseshoe_xyy[:,:,c] = horseshoe_c

    # Convert the image into linear sRGB color space.
    horseshoe_xyz = color_space_transform(horseshoe_xyy, "CIE-xyY", "CIE-XYZ")
    horseshoe_srgb_linear = color_space_transform(
        horseshoe_xyz, "CIE-XYZ", "sRGB-linear")

    # Normalizing the image by the maximum color component, and remove negative
    # values.
    horseshoe_srgb_linear = normalize_image_by_max_color(horseshoe_srgb_linear)
    horseshoe_srgb_linear[horseshoe_srgb_linear<0] = 0.0

    # Convert to nonlinear sRGB data.
    horseshoe_srgb = color_space_transform(
        horseshoe_srgb_linear, "sRGB-linear", "sRGB")

    # Plot the horseshoe colors and outer curve.
    ax = plt.figure().gca()
    ax.imshow(horseshoe_srgb[::-1, :, :], extent=[0,1,0,1])
    impixelinfo()
    ax.plot(xy_wavelength[:,0], xy_wavelength[:,1], color='k', linewidth=3)

    # Plot the sRGB triangle.
    srgb_triangle_srgb_linear = np.array([[1,0,0], [0,1,0], [0,0,1]]).T
    srgb_triangle_xyz = color_space_transform(
        srgb_triangle_srgb_linear, "sRGB-linear", "CIE-XYZ")
    srgb_triangle_xy = normalize_columns(srgb_triangle_xyz)[:2, :]
    plot_triangle(ax, srgb_triangle_xy, color="b", linewidth=2)
    ax.annotate("sRGB", xy=srgb_triangle_xy[:,1], color="b")

    # Plot CIE Illuminant D65.
    # TODO: do the integration on corresponding wavelength properly.
    d65_spd = read_cvrl_csv("cvrl-data/Illuminantd65.csv")[60:,:]
    d65_xyz = integrate_spd_with_cmfs(d65_spd, xyz_cmfs)
    d65_xy = (d65_xyz / np.sum(d65_xyz))[:2]
    plt.plot(d65_xy[0], d65_xy[1], 'ko')
    ax.annotate("D65", xy=d65_xy)

    # TODO: plot the black body radiation temperature curve, etc.

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.show()

def main():
    """Run all the demos. The demos will be run one by one, paused with a window
    showing up. To continue to the next demo, simply close the current
    window.

    """
    demo_show_spectral_functions()
    demo_show_monochromatic_3d()
    demo_show_horseshoe()

if __name__ == "__main__":
    main()
