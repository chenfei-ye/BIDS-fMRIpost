## 协变量回归
###  协变量回归算法：
- clean_img: 对BOLD图像进行协变量回归后，输出nifti图像不考虑motion censoring的影响，即输出图像帧数与原始BOLD扫描帧数始终一致。后续BOLD信号提取及功能连接矩阵FC计算则考虑了motion censoring的作用，即输出BOLD time_series 帧数与原始BOLD扫描帧数可能不一致。仅支持nifti数据处理。计算效率较高，默认推荐。

- clean_signal: 支持nifti/gifti/cifti数据处理。

###  协变量回归策略：
- simple: Load confounds for a simple denoising strategy commonly used in resting state functional connectivity. Please refer to [doi:10.1073/pnas.0504136102](https://doi.org/10.1073/pnas.0504136102).
-  compcor: CompCor estimates noise through principal component analysis on regions that are unlikely to contain signal. Please refer to [doi:https://doi.org/10.1016/j.neuroimage.2007.04.042](https://doi.org/https://doi.org/10.1016/j.neuroimage.2007.04.042).
- basic18: six head motion parameters, averaged signals from cerebrospinal fluid, white matter, and global brain signal, as well as their temporal derivatives (18 regressors in total). Please refer to [https://doi.org/10.1016/j.neuroimage.2021.117831](https://doi.org/10.1016/j.neuroimage.2021.117831)
- basic18-cs: basic18 with motion censoring. Please refer to [https://doi.org/10.1016/j.neuroimage.2021.117831](https://doi.org/10.1016/j.neuroimage.2021.117831). In details, motion censoring was conducted to control the consequence of frame-wise displacement (FD). Time frames with a FD > 0.5 mm were excluded for further analysis.
- basic36: The 36-parameter confound model includes 6 realignment parameters, mean WM and CSF time series, and global signal regression (9 parameters). Additionally, the 36-parameter model includes temporal derivatives of these 9 time series (+9) and squares of the original 9 parameters and of their temporal derivatives (+18) for a total of 36 parameters. Please refer to [https://xcpengine.readthedocs.io/modules/confound.html](https://xcpengine.readthedocs.io/modules/confound.html)
- basic36-cs: basic36 with motion censoring. Please refer to  [https://xcpengine.readthedocs.io/modules/confound.html](https://xcpengine.readthedocs.io/modules/confound.html)
