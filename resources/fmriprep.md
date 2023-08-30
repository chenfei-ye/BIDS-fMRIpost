# fMRIPrep的简单说明

详细说明见官方教程：[https://fmriprep.org/en/stable/installation.html](https://fmriprep.org/en/stable/installation.html)

## 本页内容
* [建议指令](#建议指令)
* [固定参数说明](#固定参数说明)
* [可选参数说明](#可选参数说明)
* [部分结果说明](#部分结果说明)

## 建议指令
1. 首先利用[BIDS-freesurfer](https://github.com/chenfei-ye/BIDS-freesurfer)进行`3D-T1w`的**批量**自动分割（节省时间）。注意`3D-T1w`图像的层厚（Z轴分辨率）约为1mm。
2. 检查`<bids_root>`目录，确认每个待处理被试都同时包含`T1w`和`task-rest_bold`模态。
3. 基于上述分割结果，进行fMRI影像预处理。示例指令：
```
docker run -ti --rm -v <bids_root>:/bids_dataset \
-v <local_license_dir>/freesurfer_license.txt:/opt/freesurfer/license.txt \
-v <bids_root>/derivatives/working:/working nipreps/fmriprep:latest \
/bids_dataset /bids_dataset/derivatives/fmriprep participant \
--skip-bids-validation --md-only-boilerplate \
--output-spaces MNI152NLin2009cAsym:res-2 T1w \
--nthreads 20 --mem_mb 20000 --stop-on-first-crash \
--fd-spike-threshold 0.5 \
--fs-subjects-dir /bids_dataset/derivatives/freesurfer \
--use-syn-sdc --ignore fieldmaps --use-aroma \
-w /working
```
一些经验解释：
- `/working`映射到本地，是为了防止运行是内存不足。运行完毕后可删除`<bids_root>/derivatives/working`路径。
- `--output-spaces`输出空间增加`T1w`是为了后续可能用到的皮层[ciftify](https://github.com/edickie/ciftify)分析
- `--use-aroma`提供了额外的协变量回归的策略，但会增加一些运算时间
- `--nthreads`及`--mem_mb`根据实际服务器资源来确定计算的线程及内存
- `--fd-spike-threshold`会针对头动过大的被试生成`Spike regressors for outlier censoring`，默认是0.5 mm阈值
- `--fs-subjects-dir`指定已经处理完毕的`freesurfer`分割输出结果

## 固定参数说明

-   `/bids_dataset`: 容器内输入BIDS路径，通过本地路径挂载（-v）
-   `/outputs`：容器内输出路径，通过本地路径挂载（-v）。建议本地目录名为`/derivatives/dmri_prep`
-   `{participant, group}`：可选participant或group模式。目前只支持participant，即个体水平分析

## 可选参数说明
详细请参考[官方说明](https://www.fmriprep.org/en/20.1.1/usage.html)
-   `--participant_label [str]`：指定分析某个或某几个被试。比如`--participant_label 01 03 05`。否则默认按顺序分析所有被试。
-   `--session_label [str]`：指定分析同一个被试对应的某个或某几个session。比如`--session_label 01 03 05`。否则默认按顺序分析所有session。
-   `--fs-subjects-dir [path]`：若已经跑过`freesurfer`，可以指定`freesurfer`的生成结果路径。`fMRIPrep`将利用`freesurfer`的T1皮层分割进行预处理。
-   `--fs-no-reconall`：若没有预先跑`freesurfer`，也不想跑`freesurfer`，则开启此选项。否则`fMRIPrep`将默认跑`freesurfer`实现的皮层重建工作。
-   `--mem_mb_single [int]`：给每个被试分配的内存（单位是MB）
-   `--nthreads [int]`：分配的线程数
-   `--output-spaces [str]`: 设置输出图像空间和分辨率，推荐选`MNI152NLin2009cAsym:res-2`，意思是空间标准化模板选择`MNI152NLin2009cAsym`，分辨率是2mm。如不声明，默认为`:res-native`。当使用fsaverage这种皮层表面模板时，可以使用`--output-spaces fsaverage5`这种旧的声明方法，也可以使用`--output-spaces fsaverage:den-10k`这种声明方式。
-   `--stop-on-first-crash`：遇报错即停止运行。
-   `--ignore fieldmaps`：忽略fieldmap场图
-   `--md-only-boilerplate`：计算方法报告以MarkDown文件的形式生成
-   `--use-syn-sdc`：用fieldmap-less的方式做susceptibility distortion correction
-   `-w`: 工作目录，存储中间结果的路径
-   `--skip-bids-validation`：跳过BIDS格式审查步骤

## 部分结果说明
详细请参考[官方说明](https://www.fmriprep.org/en/20.1.1/outputs.html)
-   `func`：BOLD预处理结果路径。
-   `/func/**_desc-preproc_bold.nii.gz`：预处理后的4D-BOLD图像数据。如文件名中带有`MNI152NLin2009cAsym`字段，表示已经做了MNI空间标准化。
-   `anat`：T1预处理结果路径。
-   `/anat/**_desc-preproc_T1w.nii.gz`：预处理后的3D-T1w带头皮图像数据。如文件名中带有`MNI152NLin2009cAsym`字段，表示已经做了MNI空间标准化，否则为T1原始空间。
-   `/anat/**_desc-brain_mask.nii.gz`：预处理后的3D-T1w图像mask。如文件名中带有`MNI152NLin2009cAsym`字段，表示已经做了MNI空间标准化，否则为T1原始空间。


