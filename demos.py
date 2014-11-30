#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Oct 23, 2014.

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from xy_python_utils.matplotlib_utils import *
from data import *
from utils import *

def display_cmfs(wl, cmfs):
    plt.plot(wl, cmfs[0,:], 'r', lw=2)
    plt.plot(wl, cmfs[1,:], 'g', lw=2)
    plt.plot(wl, cmfs[2,:], 'b', lw=2)

def demo_show_spectral_functions():
    fig = plt.figure()
    # Plot CIE-XYZ color matching functions.
    ax = fig.add_subplot(121)
    xyz_cmfs, wl = load_fw("xyz-cmfs")
    display_cmfs(wl, xyz_cmfs)
    ax.set_title("CIE-XYZ color matching functions.")
    # Plot spectral power distribution (D65, blackbody radiations, etc.).
    ax = fig.add_subplot(122)
    d65_spd, wl = load_fw("d65-spd")
    ax.plot(wl, d65_spd / np.sum(d65_spd), lw = 2, label="CIE D65")
    for t in (1500, 3000, 6000, 10000):
        blackbody_spd = get_blackbody_spd(t, wl)
        ax.plot(wl, blackbody_spd, lw = 2, label="Blackbody T=%dK" % t)
    ax.legend(loc="lower right", fontsize="small")
    ax.set_xlim(np.min(wl), np.max(wl))
    ax.set_ylim(0, 0.003)
    ax.set_title("Spectral power distributions")

    plt.show()
    # TODO: make more subplots, say LMS, CIE-RGB, etc.

def demo_show_monochromatic_3d():
    ax = plt.figure().gca(projection="3d")

    # Plot the 3D curve of monochromatic colors.
    xyz_cmfs, wl = load_fw("xyz-cmfs")
    for i in xrange(xyz_cmfs.shape[1]-1):
        color = xyz_cmfs[:, i] / np.sum(xyz_cmfs[:, i])
        ax.plot(xyz_cmfs[0, i:i+2], xyz_cmfs[1, i:i+2], xyz_cmfs[2, i:i+2],
                color = color, linewidth = 3)

    # Plot the intersection of $$X + Y + Z = 1$$ plane with axes.
    ax.plot(np.array([1.0, 0.0, 0.0, 1.0]),
            np.array([0.0, 1.0, 0.0, 0.0]),
            np.array([0.0, 0.0, 1.0, 0.0]),
            color='k', label="X+Y+Z=1")

    # Plot the projection of monochromatic colors onto the $$X + Y + Z = 1$$
    # plane.
    xyz_cmfs = normalize_columns(xyz_cmfs)
    ax.scatter(xyz_cmfs[0,:], xyz_cmfs[1,:], xyz_cmfs[2,:],
               s = 3, color = xyz_cmfs.T)

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

def draw_horseshoe_colors(ax, mono_xy):
    """Draw the horseshoe colors."""
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
    inside = xy_inside_horseshoe(xx, yy, mono_xy.T)
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

    # Draw the horseshoe colors.
    ax.imshow(horseshoe_srgb[::-1, :, :], extent=[0,1,0,1])
    impixelinfo()

def plot_horseshoe_curve_with_ticks(ax, mono_xy, wl):
    """Plot the horseshoe curve with wavelength ticks alongside."""
    ax.plot(mono_xy[0,:], mono_xy[1,:], color='k', linewidth=3)
    small_ticks = np.arange(400, 700, 5)
    large_ticks = np.arange(460, 640, 20)
    small_tick_size = 0.01
    large_tick_size = 0.02
    text_distance = 0.04
    tick_indices = [i for i in xrange(len(wl)) \
                    if (wl[i] in small_ticks) or (wl[i] in large_ticks)]
    for i in tick_indices:
        # Compute tick direction.
        x,y = mono_xy[0,i], mono_xy[1,i]
        xp,yp = mono_xy[0,i-1], mono_xy[1,i-1]
        xn,yn = mono_xy[0,i+1], mono_xy[1,i+1]
        angle = np.arctan2(yn-yp, xn-xp) + np.pi / 2
        # Plot tick according to tick size.
        ts = (wl[i] in large_ticks) and large_tick_size or small_tick_size
        ax.plot([x, x + ts*np.cos(angle)], [y, y + ts*np.sin(angle)], 'k')
        # Draw texts.
        if wl[i] in large_ticks:
            td = text_distance
            ax.text(x+td*np.cos(angle), y+td*np.sin(angle), str(int(wl[i])),
                    ha="center", va="center")

def plot_color_temperature_curve(ax, xyz_cmfs, wl):
    """Plot the color temperature curve."""
    # Compute the color for blackbody radiation of a range of temperatures.
    temperatures = np.arange(1000, 15000, 50)
    color_curve = np.zeros((2, len(temperatures)))
    for i,t in enumerate(temperatures):
        spd = get_blackbody_spd(t, wl)
        xyz = np.dot(xyz_cmfs, spd)
        color_curve[:,i] = (xyz / np.sum(xyz))[:2]
    ticks = np.array([1500, 3000, 6000, 10000])
    tick_indices = [i for i in xrange(len(temperatures)) \
                    if temperatures[i] in ticks]
    ax.plot(color_curve[0,:], color_curve[1,:], lw=2, color="k")
    # Draw texts.
    text_distance = 0.03
    for i in tick_indices:
        x,y = color_curve[0,i], color_curve[1,i]
        xp,yp = color_curve[0,i-1], color_curve[1,i-1]
        xn,yn = color_curve[0,i+1], color_curve[1,i+1]
        angle = np.arctan2(yn-yp, xn-xp) - np.pi / 2
        ax.plot(x, y, 'wo')
        ax.text(x - text_distance*np.cos(angle), y - text_distance*np.sin(angle),
                str(int(temperatures[i])) + "K", ha="center", va="center")

def demo_show_horseshoe():
    # Load the CMFs of monochromatic colors.
    xyz_cmfs, wl = load_fw("xyz-cmfs")
    mono_xy = normalize_columns(xyz_cmfs)[:2, :]
    ax = plt.figure().gca()

    draw_horseshoe_colors(ax, mono_xy)
    plot_horseshoe_curve_with_ticks(ax, mono_xy, wl)
    plot_color_temperature_curve(ax, xyz_cmfs, wl)

    # Plot the sRGB triangle.
    srgb_triangle_srgb_linear = np.array([[1,0,0], [0,1,0], [0,0,1]]).T
    srgb_triangle_xyz = color_space_transform(
        srgb_triangle_srgb_linear, "sRGB-linear", "CIE-XYZ")
    srgb_triangle_xy = normalize_columns(srgb_triangle_xyz)[:2, :]
    plot_triangle(ax, srgb_triangle_xy, color="b", linewidth=2)
    ax.annotate("sRGB", xy=srgb_triangle_xy[:,1], color="b")

    # Plot CIE Illuminant D65.
    d65_spd, _ = load_fw("d65-spd", wl)
    d65_xyz = np.dot(xyz_cmfs, d65_spd)
    d65_xy = (d65_xyz / np.sum(d65_xyz))[:2]
    ax.plot(d65_xy[0], d65_xy[1], 'ko')
    ax.text(d65_xy[0]-0.03, d65_xy[1]+0.03, 'D65', ha="center", va="center")

    # TODO: plot the black body radiation temperature curve, etc.

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_aspect("equal")
    ax.set_xlim(-0.07, 0.75)
    ax.set_ylim(-0.03, 0.9)
    plt.show()

def main():
    """Run all the demos. The demos will be run one by one, paused with a window
    showing up. To continue to the next demo, simply close the current window.

    """
    demo_show_spectral_functions()
    demo_show_monochromatic_3d()
    demo_show_horseshoe()

if __name__ == "__main__":
    main()
