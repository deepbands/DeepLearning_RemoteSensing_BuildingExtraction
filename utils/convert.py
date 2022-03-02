import numpy as np
from .raster2uint8 import raster_to_uint8

try:
    from osgeo import gdal
except ImportError:
    import gdal


def layer2array(sample_path, band_list, row=None, col=None, grid_size=[512, 512], overlap=[24, 24]):
    gd = gdal.Open(sample_path)
    width = gd.RasterXSize
    height = gd.RasterYSize
    if gd.RasterCount != 1:
        array_list = []
        for b in band_list:
            band = gd.GetRasterBand(b)
            array_list.append(raster_to_uint8(__get_grid(band, row, col, \
                                                         width, height, grid_size, overlap)))
        array = np.stack(array_list, axis=2)
    else:
        array = raster_to_uint8(__get_grid(gd, row, col, \
                                           width, height, grid_size, overlap))
    del gd
    return array


def __get_grid(gd, row, col, width, height, grid_size, overlap):
    grid_size = np.array(grid_size)
    overlap = np.array(overlap)
    if row is not None and col is not None:
        grid_idx = np.array([row, col])
        ul = grid_idx * (grid_size - overlap)
        lr = ul + grid_size
        xoff, yoff, xsize, ysize = ul[1], ul[0], (lr[1] - ul[1]), (lr[0] - ul[0])
        if xoff + xsize > width:
            xsize = width - xoff
        if yoff + ysize > height:
            ysize = height - yoff
        result = gd.ReadAsArray(xoff=int(xoff), yoff=int(yoff), \
                                win_xsize=int(xsize), win_ysize=int(ysize))
    else:
        result = gd.ReadAsArray()
    return result


def convert_coord(point, tform):
    olp = np.ones((1, 3))
    olp[0, :2] = point
    nwp = np.dot(tform, olp.T)
    return nwp.T[0, :2]