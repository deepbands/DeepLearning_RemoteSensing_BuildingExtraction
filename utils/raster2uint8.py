import numpy as np
import cv2
import operator
from functools import reduce


def raster_to_uint8(image: np.array, dtype: str="uint8") -> np.array:
    """ Convert raster to uint8.
    Args:
        image (np.array): image.
        dtype (str): type of image.
    Returns:
        np.array: image on uint8.
    """
    dtypes = ["uint8", "uint16", "float32"]
    if dtype not in dtypes:
        raise ValueError(f"The 'dtype' must be uint8/uint16/float32, not {dtype}.")
    if dtypes == "uint8":
        return image
    else:
        if dtypes == "float32":
            image = __sample_norm(image)
        return __two_percentLinear(image)


# 2% linear stretch
def __two_percentLinear(image: np.array, max_out: int=255, min_out: int=0) -> np.array:
    def __gray_process(gray, maxout=max_out, minout=min_out):
        # Get the corresponding gray level at 98% histogram
        high_value = np.percentile(gray, 98)
        low_value = np.percentile(gray, 2)
        truncated_gray = np.clip(gray, a_min=low_value, a_max=high_value)
        processed_gray = ((truncated_gray - low_value) / (high_value - low_value)) * (maxout - minout)
        return processed_gray
    if len(image.shape) == 3 and image.shape[-1] == 3:
        b, g, r = cv2.split(image)
        r_p = __gray_process(r)
        g_p = __gray_process(g)
        b_p = __gray_process(b)
        result = cv2.merge((b_p, g_p, r_p))
    elif len(image.shape) == 2:
        result = __gray_process(image)
    else:
        raise ValueError(f"Image.shape[-1] must be 1 or 3, but {image.shape[-1]}.")
    return np.uint8(result)


# Simple image standardization
def __sample_norm(image: np.array, NUMS: int=65536) -> np.array:
    if NUMS == 256:
        return np.uint8(image)
    if len(image.shape) == 3 and image.shape[-1] == 3:
        stretched_r = __stretch(image[:, :, 0], NUMS)
        stretched_g = __stretch(image[:, :, 1], NUMS)
        stretched_b = __stretch(image[:, :, 2], NUMS)
        stretched_img = cv2.merge([
                stretched_r / float(NUMS),
                stretched_g / float(NUMS),
                stretched_b / float(NUMS)])
    elif len(image.shape) == 2:
        stretched_img = __stretch(image, NUMS)
    else:
        raise ValueError(f"Image.shape[-1] must be 1 or 3, but {image.shape[-1]}.")
    return np.uint8(stretched_img * 255)


# Histogram equalization
def __stretch(ima: np.array, NUMS: int) -> np.array:
    hist = __histogram(ima, NUMS)
    lut = []
    for bt in range(0, len(hist), NUMS):
        # Step size
        step = reduce(operator.add, hist[bt : bt + NUMS]) / (NUMS - 1)
        # Create balanced lookup table
        n = 0
        for i in range(NUMS):
            lut.append(n / step)
            n += hist[i + bt]
        np.take(lut, ima, out=ima)
        return ima


# Calculate histogram
def __histogram(ima: np.array, NUMS: int) -> np.array:
    bins = list(range(0, NUMS))
    flat = ima.flat
    n = np.searchsorted(np.sort(flat), bins)
    n = np.concatenate([n, [len(flat)]])
    hist = n[1:] - n[:-1]
    return hist


# # Test
# if __name__ == "__main__":
#     try:
#         import gdal
#     except:
#         from osgeo import gdal

#     tif_u8_path = r"raster_type\test_data\tif_u8.tif"
#     tif_u16_path = r"raster_type\test_data\tif_u16.tif"
#     tif_f32_path = r"raster_type\test_data\tif_f32.tif"
#     for tif_path, dtype in zip([tif_u8_path, tif_u16_path, tif_f32_path], 
#                                ["uint8", "uint16", "float32"]):
#         ima = gdal.Open(tif_path).ReadAsArray()
#         if len(ima.shape) != 2:
#             ima = ima.transpose((1, 2, 0))
#         ima = raster_to_uint8(ima, dtype)
#         cv2.imshow("ima", ima)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()