# DeepLearning_RemoteSensing_BuildingExtraction
docker test

## how to use

1. download test [data](https://next.a-boat.cn:2021/s/Kxgxite5Mb7nFfJ) and [model](https://next.a-boat.cn:2021/s/Mwp4eYEYFATpXNX).
2. download [docker desktop](https://www.docker.com/products/docker-desktop).
3. `win+R` and input this code in CMD:

```shell
cd DeepLearning_RemoteSensing_BuildingExtraction\
docker compose up --build
```

4. test:

```shell
python demo.py --tif_path data/test.tif --model_path bisenet_v2_512x512/model.pdmodel
```

