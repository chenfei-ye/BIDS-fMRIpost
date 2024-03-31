

# BIDS-fMRIpost

`BIDS-fmripost` is developed based on [nilearn](https://nilearn.github.io), aiming to perform basic fMRI data post-process after [fMRIPrep](https://fmriprep.org/en/stable/installation.html) . Main functions include:
- denoise, including confound regression and spatial smoothing
- BOLD signal extraction
- functional connectivity (FC) network creation

Current version is only for resting-state fMRI data, the input data should be arranged according to [BIDS format](https://bids.neuroimaging.io/). Input image modalities must include 3D-T1w and fMRI data. 

Standard brain atlases supported:
`AAL1_MNI`, `AAL1ctx_MNI`, `AAL2_MNI`, `AAL3_MNI`, `JHUwm48_MNI`, `desikan_T1w`,  `destrieux_T1w`,  `hcpmmp_T1w` , `schaefer100x7_T1w`,  `schaefer200x7_T1w` , `schaefer400x7_T1w`, `schaefer100x7_MNI`,  `schaefer200x7_MNI` , `schaefer400x7_MNI`,  `schaefer1000x7_MNI`, `schaefer100x17_T1w`,  `schaefer200x17_T1w` , `schaefer400x17_T1w`, `schaefer100x17_MNI`,  `schaefer200x17_MNI` , `schaefer400x17_MNI`,  `schaefer1000x17_MNI`, `PD25_MNI`

[BIDS-fMRIpost 中文说明](resources/README_Chs.md)

Check details in bids-fmripost [brain atlases](resources/atlases.md)

Check bids-fmripost version history in [Change Log](resources/CHANGELOG.md)

## Contents
* [Install](#Install)
* [Before Running](#before-running)
* [Running](#running)
* [Input Argument](#input-argument)
* [Output Explanation](#output-explanation)
* [Confound Regression](#confound-regression)

## Install
### install by pulling (recommend)
```
docker pull mindsgo-sz-docker.pkg.coding.net/neuroimage_analysis/base/bids-fmripost:latest
docker tag  mindsgo-sz-docker.pkg.coding.net/neuroimage_analysis/base/bids-fmripost:latest  bids-fmripost:latest
```

### or install by docker build
```
cd BIDS-fmripost
docker build -t bids-fmripost:latest .
```
## Before Running
use [fMRIPrep](https://fmriprep.org/en/stable/installation.html) for fMRI data preprocessing
```
docker run -it --rm -v <bids_root>:/bids_dataset \
-v <local_license_dir>/freesurfer_license.txt:/opt/freesurfer/license.txt \
-v <local_working_dir>:/working_dir nipreps/fmriprep:latest \
/bids_dataset /bids_dataset/derivatives/fmriprep participant \ 
--participant_label 01 02 03 --skip-bids-validation --ignore fieldmaps \
--md-only-boilerplate --output-spaces MNI152NLin2009cAsym:res-2 T1w \
--nthreads 20 --stop-on-first-crash --mem_mb 5000 \
--use-syn-sdc --fd-spike-threshold 0.5 -v -w /working_dir
```

## Running
### default running
```
docker run -it --rm -v <local_bids_dir>:/dataio -v <local_scripts_dir>/atlases:/atlases bids-fmripost:latest /dataio --participant_label 01 02 03 -atlases AAL3_MNI desikan_T1w -atlas_config /atlases/atlas_config_docker.json -clean_type basic18 -sm 6
```

### running with your customized atlas
Example: define your atlas dictionary file in `/atlases/brain_nodes_cye3.csv`.
```
docker run -it --rm -v <local_bids_dir>:/dataio -v <local_scripts_dir>/atlases:/atlases bids-fmripost:latest /dataio  -customized_atlas /atlases/brain_nodes_cye3.csv -atlas_config /atlases/atlas_config_docker.json 
```
## Input Argument
####   positional argument:
-   `/bids_dataset`: The root folder of a BIDS valid dataset (sub-XX folders should be found at the top level in this folder).

####   optional argument:
-   `--participant_label [str]`：A space delimited list of participant identifiers or a single identifier (the sub- prefix can be removed)
-   `--session_label [str]`：A space delimited list of session identifiers or a single identifier (the ses- prefix can be removed)
- `-scripts_dir [path]`：codes path inside docker container: `/pipeline`
- `-atlas_config [path]`：atlas path inside docker container: `/pipeline/atlases/atlas_config.json`.
- `-clean_type ["compcor", "simple",  "basic18", "basic18-cs","basic36", "basic36-cs"]`. See [Confound Regression](#confound-regression) for details.
- `-clean_mode ["clean_signal", "clean_img"]`：confound regression methods. Check details in [clean_img](https://nilearn.github.io/stable/modules/generated/nilearn.image.clean_img.html) and [clean_signal](https://nilearn.github.io/stable/modules/generated/nilearn.signal.clean.html).
- `-customized_atlas [path]`: path of your customized_atlas csv file. See [atlases](resources/atlases.md) for details.
- `-atlases [str]`: A space delimited list of brain atlases. e.g. `-atlases AAL3_MNI hcpmmp_T1w`. FreeSurfer should be ran first for atlases ends with `_T1w`. See `atlases/atlas_config_docker.json` for details. 
- `-sm [int]`：smoothing kernel size (6 mm by default). 
- `-no_sample_mask`: mandatory control to keep input and output BOLD have same time-series dimensions. Only in `clean_img` mode and without `motion censoring`.


## Output explanation

- log: `<local_bids_dir>/derivatives/fmripost/runtime.log`
- parcel-wise BOLD time_series: `<local_bids_dir>/derivatives/fmripost/sub-XX/sub-XX_BOLD_XX.csv`
- parcel-wise FC network: `<local_bids_dir>/derivatives/fmripost/sub-XX/sub-XX_FC_mat_XX.csv`
- brain parcellation visualization: `<local_bids_dir>/derivatives/fmripost/sub-XX/sub-XX_parc_XX.png`
- parcel-wise FC network visualization: `<local_bids_dir>/derivatives/fmripost/sub-XX/sub-XX_FC_mat_XX.png`


## Confound Regression

- simple: Load confounds for a simple denoising strategy commonly used in resting state functional connectivity. Please refer to [doi:10.1073/pnas.0504136102](https://doi.org/10.1073/pnas.0504136102).
-  compcor: CompCor estimates noise through principal component analysis on regions that are unlikely to contain signal. Please refer to [doi:https://doi.org/10.1016/j.neuroimage.2007.04.042](https://doi.org/https://doi.org/10.1016/j.neuroimage.2007.04.042).
- basic18: six head motion parameters, averaged signals from cerebrospinal fluid, white matter, and global brain signal, as well as their temporal derivatives (18 regressors in total). Please refer to [https://doi.org/10.1016/j.neuroimage.2021.117831](https://doi.org/10.1016/j.neuroimage.2021.117831)
- basic18-cs: basic18 with motion censoring. Please refer to [https://doi.org/10.1016/j.neuroimage.2021.117831](https://doi.org/10.1016/j.neuroimage.2021.117831). In details, motion censoring was conducted to control the consequence of frame-wise displacement (FD). Time frames with a FD > 0.5 mm were excluded for further analysis.
- basic36: The 36-parameter confound model includes 6 realignment parameters, mean WM and CSF time series, and global signal regression (9 parameters). Additionally, the 36-parameter model includes temporal derivatives of these 9 time series (+9) and squares of the original 9 parameters and of their temporal derivatives (+18) for a total of 36 parameters. Please refer to [https://xcpengine.readthedocs.io/modules/confound.html](https://xcpengine.readthedocs.io/modules/confound.html)
- basic36-cs: basic36 with motion censoring. Please refer to  [https://xcpengine.readthedocs.io/modules/confound.html](https://xcpengine.readthedocs.io/modules/confound.html)

## Copyright
Copyright © chenfei.ye@foxmail.com
Please make sure that your usage of this code is in compliance with the code license.


