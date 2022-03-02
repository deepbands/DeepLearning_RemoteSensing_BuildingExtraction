import time
import argparse
import utils
import os
import os.path as osp

try:
    from osgeo import gdal
except ImportError:
    import gdal


parser = argparse.ArgumentParser(description="input parameters")
parser.add_argument("--tif_path", type=str, required=True)
parser.add_argument("--model_path", type=str, required=True)
parser.add_argument("--save_folder", type=str, default="output")
parser.add_argument('--band_list', nargs='+', default=[1, 2, 3])
parser.add_argument("--grid_size", type=int, default=512)
parser.add_argument("--overlap", type=int, default=24)
parser.add_argument("--scale_rate", type=float, default=1.0)


def run(args):
    # Start timing
    time_start = time.time()
    # Get parameters
    print("== Get parameters ==")
    current_raster_layer_name = args.tif_path
    model_path = args.model_path
    save_folder = args.save_folder
    if not osp.exists(save_folder):
        os.makedirs(save_folder)
    band_list = [int(b) for b in args.band_list]
    grid_size = [args.grid_size] * 2
    overlap = [args.overlap] * 2
    scale_rate = args.scale_rate
    file_name = osp.basename(current_raster_layer_name).split(".")[0]
    param_path = model_path.replace(".pdmodel", ".pdiparams")
    infer_worker = utils.InferWorker(model_path, param_path)
    print(f"current_raster_layer_name is {current_raster_layer_name}")
    print(f"param_path is {param_path}")
    print(f"save_folder is {save_folder}, band_list is {band_list}.")
    print(f"grid_size is {grid_size}, overlap is {overlap}, scale_rate is {scale_rate}.")
    # Downsample
    print("== Start downsample ==")
    down_save_path = osp.join(save_folder, (file_name + "_down.tif"))
    layer_path = utils.dowm_sample(current_raster_layer_name, down_save_path, scale_rate)
    print(f"layer_path: {layer_path}")
    # Open tif and start
    ras_ds = gdal.Open(layer_path)
    geot = ras_ds.GetGeoTransform()
    proj = ras_ds.GetProjection()
    xsize = ras_ds.RasterXSize
    ysize = ras_ds.RasterYSize
    ras_ds = None
    grid_count = utils.create_grids(ysize, xsize, grid_size, overlap)
    number = grid_count[0] * grid_count[1]
    print(f"xsize is {xsize}, ysize is {ysize}, grid_count is {grid_count}")
    print("== Start block processing ==")
    geoinfo = {"row": ysize, "col": xsize, "geot": geot, "proj": proj}
    mask_save_path = osp.join(save_folder, (file_name + "_mask.tif"))
    mask = utils.Mask(mask_save_path, geoinfo, grid_size, overlap)
    for i in range(grid_count[0]):
        for j in range(grid_count[1]):
            img = utils.layer2array(layer_path, band_list, \
                                    i, j, grid_size, overlap)
            mask.write_grid(infer_worker.infer(img, True), i, j)
            print(f"-- {i * grid_count[1] + j + 1}/{number} --.")
    print("== Start generating result file ==")
    # Raster to shapefile used GDAL
    save_shp_path = osp.join(save_folder, (file_name + ".shp"))
    utils.polygonize_raster(mask, save_shp_path, proj, geot)
    time_end = time.time()
    print("== Finished ==")
    print("The whole operation is performed in {0} seconds.".format(str(time_end - time_start)))


if __name__ == "__main__":
    args = parser.parse_args()
    run(args)