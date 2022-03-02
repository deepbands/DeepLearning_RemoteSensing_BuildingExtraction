import numpy as np

try:
    from osgeo import gdal
except ImportError:
    import gdal


def create_grids(ysize, xsize, grid_size=[512, 512], overlap=[24, 24]):
    img_size = np.array([ysize, xsize])
    grid_size = np.array(grid_size)
    overlap = np.array(overlap)
    grid_count = np.ceil(img_size / (grid_size - overlap))
    grid_count = grid_count.astype("uint16")
    return list(grid_count)


class Mask(object):
    def __init__(self, file_name, geoinfo, grid_size=[512, 512], overlap=[24, 24]) -> None:
        self.file_name = file_name
        self.raw_size = np.array([geoinfo["row"], geoinfo["col"]])
        self.grid_size = np.array(grid_size)
        self.overlap = np.array(overlap)
        driver = gdal.GetDriverByName("GTiff")
        self.dst_ds = driver.Create(file_name, geoinfo["col"], geoinfo["row"], 1, gdal.GDT_UInt16)
        self.dst_ds.SetGeoTransform(geoinfo["geot"])
        self.dst_ds.SetProjection(geoinfo["proj"])
        self.band = self.dst_ds.GetRasterBand(1)
        self.band.WriteArray(np.zeros((self.raw_size[0], self.raw_size[1]), dtype="uint8"))

    def write_grid(self, grid, i, j):
        h, w = self.grid_size
        start_h = (i * h) if i == 0 else (i * (h - self.overlap[0]))
        end_h = start_h + h
        if end_h > self.raw_size[0]:
            win_ysize = int(self.raw_size[0] - start_h)
        else:
            win_ysize = int(self.grid_size[1])
        start_w = (j * w) if j == 0 else (j * (w - self.overlap[1]))
        end_w = start_w + w
        if end_w > self.raw_size[1]:
            win_xsize = int(self.raw_size[1] - start_w)
        else:
            win_xsize = int(self.grid_size[0])
        over_grid = self.band.ReadAsArray(xoff=int(start_w), yoff=int(start_h), \
                                          win_xsize=win_xsize, win_ysize=win_ysize)
        h, w = over_grid.shape
        over_grid += grid[:h , :w]
        over_grid[over_grid > 0] = 1
        self.band.WriteArray(over_grid, int(start_w), int(start_h))
        self.dst_ds.FlushCache()

    @property
    def gdal_data(self):
        return self.dst_ds

    def close(self):
        self.dst_ds = None