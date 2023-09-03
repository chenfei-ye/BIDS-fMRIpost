# dcm2bids
详细说明见官方教程：[https://unfmontreal.github.io/Dcm2Bids](https://unfmontreal.github.io/Dcm2Bids)

推荐使用3.0.0以上版本（和2.X版本不兼容）。

## 本页内容
* [安装](#安装)
* [定义配置文件](#定义配置文件)
* [运行](#运行)


## 安装
经测试，`binary executables`在Ubuntu18.04中运行，缺少必要的glib库。故推荐使用`conda`安装

`conda`的安装方式[点此](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)

1. 新建一个`environment.yml`文件，在里面写入以下内容：
```
name: dcm2bids
channels:
  - conda-forge
dependencies:
  - python>=3.7
  - dcm2niix
  - dcm2bids
```

2. 创建`conda`环境：
```
conda env create --file environment.yml
``` 

3. 激活`conda`环境：
```
conda activate dcm2bids
``` 
4. 测试是否安装成功：
```
dcm2bids  --help
``` 
## 定义配置文件
配置文件`dcm2bids_config.json`的意义是根据`DICOM`头文件信息，查询匹配正确的序列名`SeriesDescription`。

`dcm2bids_config.json`需要根据实际的`DICOM`序列名进行修改。

[查看dcm2bids_config样例](dcm2bids_config.json)



## 运行
1. 初始化输出目录（也叫BIDS根目录`bids_root`）:
```
dcm2bids_scaffold -o bids_root
```
- `-o [str]`: 输出目录的路径，可自行命名

2. 将**单个被试的**输入`DICOM`文件目录`input_dir`中的影像数据，转档到临时目录`tmp_dcm2bids/helper`:
```
dcm2bids_helper  -d  input_dir 
```
3. 查看`nifti`文件包含的所有序列名：
```
grep  "SeriesDescription"  tmp_dcm2bids/helper/*.json
```
基于返回的序列名，**手动修改`dcm2bids_config.json`内容**。

部分常用MRI影像模态的序列名，可能包含的字符串：
> T1w: *mpr*|.*mp-rage*|.*T1W*|.*SPGR*|.*3D BRAVO*|.*T1W_3D_TFE*
> 
> T2w: T2w | *dual*
> 
> FLAIR: *FLAIR*| *T2Flair*
> 
> dwi: ep2d_diff_*|.*ep2d_DTI
> 
> bold: ep2d_bold*|.*bold

4. 根据配置文件，对每个被试的数据进行转档（以`sub-001`为例）：
```
dcm2bids -d input_dir -p 001 -c code/dcm2bids_config.json --auto_extract_entities
```
5. 对下个被试数据重复步骤2 ~ 步骤4

6. 删掉临时文件目录
```
rm -rf bids_root/tmp_dcm2bids
```

7. 检验是否通过BIDS标准，根据报错信息进行修改
```
docker run -ti --rm -v bids_root:/data:ro bids/validator /data
```
