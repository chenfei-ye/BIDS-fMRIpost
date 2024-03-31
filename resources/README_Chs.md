

# BIDS-fMRIpost

`BIDS-fmripost`是基于[fMRIPrep](https://fmriprep.org/en/stable/installation.html) 的后处理分析流程，基于[nilearn](https://nilearn.github.io)开发。分析功能包括：

- 协变量回归（confound regression）
- 空间平滑（spatial smoothing）
- 基于脑区的BOLD信号提取 (BOLD signal extraction)
- 功能连接网络计算 （FC network）

目前主要用于静息态功能磁共振影像数据的脑网络分析。该脚本的输入数据需符合[BIDS格式](https://bids.neuroimaging.io/)，输入模态需包括3D-T1w和fMRI。目前支持的图谱包括：
`AAL1_MNI`, `AAL1ctx_MNI`, `AAL2_MNI`, `AAL3_MNI`, `JHUwm48_MNI`,  `desikan_T1w`,  `destrieux_T1w`,  `hcpmmp_T1w` , `schaefer100x7_T1w`,  `schaefer200x7_T1w` , `schaefer400x7_T1w`, `schaefer100x7_MNI`,  `schaefer200x7_MNI` , `schaefer400x7_MNI`,  `schaefer1000x7_MNI`, `schaefer100x17_T1w`,  `schaefer200x17_T1w` , `schaefer400x17_T1w`, `schaefer100x17_MNI`,  `schaefer200x17_MNI` , `schaefer400x17_MNI`,  `schaefer1000x17_MNI`, `PD25_MNI`

[图谱说明](atlases.md)

[版本历史](CHANGELOG.md)

## 本页内容
* [数据准备](#数据准备)
* [安装](#安装)
* [运行前准备](#运行前准备)
* [运行](#运行)
* [参数说明](#参数说明)
* [输出结果](#输出结果)

## 数据准备
数据需要符合[Brain Imaging Data Structure](http://bids.neuroimaging.io/) (BIDS)格式。对于`DICOM`数据文件，建议使用[dcm2bids](https://unfmontreal.github.io/Dcm2Bids)工具进行转档，参考[dcm2bids 转档中文简易使用说明](dcm2bids.md)



## 安装
本地需安装[docker](https://docs.docker.com/engine/install)，具体可参考[步骤](docker_install.md)

### 方式一：拉取镜像
```
docker pull mindsgo-sz-docker.pkg.coding.net/neuroimage_analysis/base/bids-fmripost:latest
docker tag  mindsgo-sz-docker.pkg.coding.net/neuroimage_analysis/base/bids-fmripost:latest  bids-fmripost:latest
```

### 方式二：镜像创建
```
# git clone下载代码仓库
cd BIDS-fmripost
docker build -t bids-fmripost:latest .
```
## 运行前准备
使用[fMRIPrep](https://fmriprep.org/en/stable/installation.html) 进行预处理
```
docker run -it --rm -v <local_bids_dir>:/bids_dataset \
-v <local_license_dir>/freesurfer_license.txt:/opt/freesurfer/license.txt \
-v <local_working_dir>:/working_dir nipreps/fmriprep:latest \
/bids_dataset /bids_dataset/derivatives/fmriprep participant \ 
--participant_label 01 02 03 --skip-bids-validation --ignore fieldmaps \
--md-only-boilerplate --output-spaces MNI152NLin2009cAsym:res-2 T1w \
--nthreads 20 --stop-on-first-crash --mem_mb 5000 \
--use-syn-sdc --fd-spike-threshold 0.5 -v -w /working_dir
```
**NOTE: 有关fmri数据预处理的[补充说明](fmriprep.md)**

## 运行
### 标准运行
示例：针对`sub-01`, `sub-02`, `sub-03`被试，分析图谱同时包括`AAL3_MNI`和`desikan_T1w`。采用`basic18`策略进行协变量回归，高斯平滑核为6mm。
```
## 定义脑图谱配置信息atlas_config_docker.json
docker run -it --rm -v <local_bids_dir>:/dataio -v <local_scripts_dir>/atlases:/atlases bids-fmripost:latest /dataio --participant_label 01 02 03 -atlases AAL3_MNI desikan_T1w -atlas_config /atlases/atlas_config_docker.json -clean_type basic18 -sm 6
```

### 自定义图谱运行
示例：修改自定义脑图谱配置信息brain_nodes_cye3.csv（文件名可自定义修改）
```
docker run -it --rm -v <local_bids_dir>:/dataio -v <local_scripts_dir>/atlases:/atlases bids-fmripost:latest /dataio  -customized_atlas /atlases/brain_nodes_cye3.csv -atlas_config /atlases/atlas_config_docker.json 
```
## 参数说明
####   固定参数说明：
-   `/bids_dataset`: 容器内输入BIDS路径，通过本地路径挂载（-v）


####   可选参数说明：
-   `--participant_label [str]`：指定分析某个或某几个被试。比如`--participant_label 01 03 05`。否则默认按顺序分析所有被试。
-   `--session_label [str]`：指定分析同一个被试对应的某个或某几个session。比如`--session_label 01 03 05`。否则默认按顺序分析所有session。
- `-scripts_dir [path]`：容器中的代码路径，默认为`/pipeline`。
- `-atlas_config [path]`：容器中的图谱路径，默认为`/pipeline/atlases/atlas_config.json`。
- `-clean_type ["compcor", "simple",  "basic18", "basic18-cs","basic36", "basic36-cs"]`：协变量回归策略选择。
- `-clean_mode ["clean_signal", "clean_img"]`：协变量回归算法，具体[见此说明](clean_mode.md)。
- `-customized_atlas [path]`: 自定义图谱csv文件路径。可以由预定义的图谱中选取感兴趣脑区拼接成新图谱。若定义了`-customized_atlas`参数，则自动忽略`-atlases`参数的内容。
- `-atlases [str]`: 指定分析某个或某几个图谱。如`-atlases AAL3_MNI hcpmmp_T1w`。对于后缀为`T1w`的图谱，需要预先对被试进行FreeSurfer分割。目前预定义的图谱见`atlas_config_docker.json`。
- `-sm [int]`：高斯平滑核大小，默认是6 mm。
- `-no_sample_mask`: 强制使得BOLD信号的输入/输出帧数量相同。只适用于`clean_img`模式以及协变量回归非`motion censoring`的条件。


## 输出结果

- 运行日志：`<local_bids_dir>/derivatives/fmripost/runtime.log`
- 脑区水平BOLD time_series：`<local_bids_dir>/derivatives/fmripost/sub-XX/sub-XX_BOLD_XX.csv`
- 脑区水平FC network：`<local_bids_dir>/derivatives/fmripost/sub-XX/sub-XX_FC_mat_XX.csv`
- 脑分割可视化质控：`<local_bids_dir>/derivatives/fmripost/sub-XX/sub-XX_parc_XX.png`
- FC脑网络可视化质控：`<local_bids_dir>/derivatives/fmripost/sub-XX/sub-XX_FC_mat_XX.png`

## Copyright
Copyright © chenfei.ye@foxmail.com
Please make sure that your usage of this code is in compliance with the code license.


