import os
import os.path as osp

try:
    from osgeo import gdal
except ImportError:
    import gdal


def dowm_sample(file_path, down_sample_save, scale=0.5):
    if scale == 1.0:
        return file_path
    dataset = gdal.Open(file_path)
    band_count = dataset.RasterCount
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    if scale < 0 and scale > 1:
        raise (f"scale must in [0, 1], now it is {scale}")
    else:
        scale = float(scale)
    # New cols and rows
    cols = int(cols * scale)
    rows = int(rows * scale)
    geotrans = list(dataset.GetGeoTransform())
    geotrans[1] = geotrans[1] / scale
    geotrans[5] = geotrans[5] / scale
    if osp.exists(down_sample_save):
        os.remove(down_sample_save)
    data_type = dataset.GetRasterBand(1).DataType
    target = dataset.GetDriver().Create(down_sample_save, xsize=cols, ysize=rows, \
                                        bands=band_count, eType=data_type)
    target.SetProjection(dataset.GetProjection())
    target.SetGeoTransform(geotrans)
    total = band_count + 1
    for index in range(1, total):
        data = dataset.GetRasterBand(index).ReadAsArray(buf_xsize=cols, buf_ysize=rows)
        out_band = target.GetRasterBand(index)
        out_band.SetNoDataValue(dataset.GetRasterBand(index).GetNoDataValue())
        out_band.WriteArray(data)
        out_band.FlushCache()
        out_band.ComputeBandStats(False)
    del dataset
    del target
    return down_sample_save


# # Test
# if __name__ == "__main__":
#     ras_path = r"E:\dataFiles\github\buildseg\data\test.tif"
#     dowm_sample(ras_path, 0.5)