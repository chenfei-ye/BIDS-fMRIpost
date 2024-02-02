# -*- coding: utf-8 -*-

"""
@author: Chenfei
@contact:chenfei.ye@foxmail.com
@version: 1.4
@file: run.py
@time: 2024/02/02
# postprocess after fmriprep
# added Schaefer100/200/400/1000 T1w space
# added PD25 atlas
# BOLD time_series and FC matrix as csv files would be produced
"""
__version__ = 'v1.3'
from loguru import logger
import argparse
import os
import glob
import time
import datetime
from mrtrix3 import run, path
from mrtrix3 import MRtrixError
from nilearn.interfaces.fmriprep import load_confounds, load_confounds_strategy
from nilearn.maskers import NiftiLabelsMasker
from nilearn.image import clean_img, smooth_img, resample_img, load_img, get_data
from nilearn.signal import clean
from nilearn.masking import apply_mask, unmask
from nilearn_utils import preset_strategies
from nilearn import plotting
from nilearn.connectome import ConnectivityMeasure
import numpy as np
import nibabel as nib
import json
import pandas as pd
from utils import read_json_file


def clean_and_smooth(bold_path, bold_mask_path, bold_img_clean_masked_sm_path, TR):
    """ Confound regression and smooth BOLD 4D niimg. 
        cleaned BOLD 4D niimg would be produced

        Parameters
        ----------
        bold_path : path of BOLD 4D niimg

        bold_mask_path : path of BOLD brain mask 4D niimg

        bold_img_clean_masked_sm_path : path of output cleaned BOLD 4D niimg

        TR: Repetition Time

        Returns
        -------
        sample_mask : None, numpy.ndarray, or list of
            When no volumns require removal, the value is None.
            Otherwise, shape: (number of scans - number of volumes removed, ) 
            The index of the niimgs along time/fourth dimension for valid volumes for subsequent analysis. 
            This attribute should be passed to parameter sample_mask of nilearn.maskers.NiftiMasker or nilearn.signal.clean. 
            Volumns are removed if flagged as following:
            * Non-steady-state volumes (if present)
            * Motion outliers detected by scrubbing

        """
    logger.info('Confound regression and smooth BOLD 4D niimg')
    bold_img = load_img(bold_path)
    bold_img_mask = load_img(bold_mask_path)
    
    num_bold_timeseries = bold_img.get_fdata().shape[3]

    clean_parameters = preset_strategies.get(args.clean_type, False)
    confounds_df, sample_mask = load_confounds(bold_path, **clean_parameters)
    if args.clean_type[-2:] == 'cs' and  type(sample_mask) is np.ndarray:
        logger.info('perform volume censoring for ' + subject_name + ': remove ' + str(num_bold_timeseries - len(sample_mask)) + ' bold timeframes')
        num_bold_timeseries = len(sample_mask)
        
    ## 对BOLD图像进行协变量回归
    if os.path.exists(bold_img_clean_masked_sm_path):
        logger.warning('File exists ' + bold_img_clean_masked_sm_path)
        logger.warning('Will jump confound regression and smoothing')
    else:
        if args.clean_mode == 'clean_img':
            logger.info('using clean_img method')
            # 直接对图像进行协变量回归，保存时不考虑sample_mask的影响
            # 即协变量回归之后，输出帧数与原始BOLD扫描帧数始终一致
            # 后续用masker.fit_transform计算time_series会考虑sample_mask的影响
            # NOTE:clean_img方法比clean_signal方法计算效率更好，但clean_img方法只适用nifti数据，clean_signal方法可通用于gifti/cifti数据
            bold_img_clean_masked = clean_img(bold_img, detrend=True, mask_img = bold_img_mask, standardize=True,  \
                                              confounds=confounds_df, low_pass=0.08, high_pass=0.01, ensure_finite=True, t_r=TR)

        elif args.clean_mode == 'clean_signal':
            logger.info('using clean_signal method')
            # 提取图像信号后，再进行协变量回归
            bold_img_data = bold_img.get_fdata()
            bold_img_data_size =bold_img_data.shape
            origin_shape = (bold_img_data_size[0] * bold_img_data_size[1] * bold_img_data_size[2], bold_img_data_size[3])
            sample_shape = (bold_img_data_size[0], bold_img_data_size[1], bold_img_data_size[2], num_bold_timeseries)

            if args.clean_type[-2:] == 'cs' and  type(sample_mask) is np.ndarray:
                # clean之后，输出帧数可能少于原始BOLD扫描帧数，因为会自动移除头动过大的BOLD图像帧
                bold_img_data_clean_flatten = clean(bold_img_data.reshape(origin_shape).T, detrend=True, sample_mask = sample_mask, \
                    standardize=True,  confounds=confounds_df, low_pass=0.08, high_pass=0.01, ensure_finite=True, t_r=TR)
            else:   
                bold_img_data_clean_flatten = clean(bold_img_data.reshape(origin_shape).T, detrend=True, \
                    standardize=True,  confounds=confounds_df, low_pass=0.08, high_pass=0.01, ensure_finite=True, t_r=TR)

            bold_img_data_clean = np.reshape(bold_img_data_clean_flatten.T, sample_shape)
            bold_img_clean = nib.Nifti1Image(bold_img_data_clean, bold_img.affine, bold_img.header)
            bold_img_clean_masked = apply_mask(bold_img_clean, bold_img_mask)
            bold_img_clean_masked = unmask(bold_img_clean_masked, bold_img_mask)

        ## BOLD图像高斯平滑
        logger.info('perform smoothing using kernei size = ' + str(args.sm))
        bold_img_clean_masked_sm = smooth_img(bold_img_clean_masked, args.sm)

        ## 保存处理后的BOLD图像
        logger.info('Saving nifti images: '+ bold_img_clean_masked_sm_path)
        nib.save(bold_img_clean_masked_sm, bold_img_clean_masked_sm_path)
    return sample_mask



def FC_atlas_calc(args, sub_bold_dir, atlas_config, atlas_name):
    """ Extract BOLD signals from fmriprep 4D niimg and calculate FC matrix. 
        This function will save BOLD time_series and FC matrix as csv files
        QC png will also be produced and saved in output directory 
        NOTE: if missing nodes exist for particular atlas, additional txt including missing nodes would also be saved in output directory 

        Parameters
        ----------
        args : CMD inpout object

        sub_bold_dir : directory of subject bold (/bids_dir/derivatives/fmriprep/sub/func) 

        atlas_config : path of atlas_config.json  

        atlas_name: name of a single brain atlas

        """
    logger.info('Extract BOLD signals from fmriprep 4D niimg and calculate FC matrix')
    # load LUT
    sgm_lut_path = atlas_config[atlas_name]['sgm_lut']
    if not os.path.exists(sgm_lut_path):
        logger.error('The following sgm_lut not exists: ' + sgm_lut_path)
        raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')
    else:
        sgm_lut = pd.read_csv(sgm_lut_path)

    # locate bold_space_T1w
    bold_space_T1w_path_ls = glob.glob(os.path.join(sub_bold_dir, '*space-T1w_desc-preproc_bold.nii.gz'))
    if len(bold_space_T1w_path_ls) ==1:
        bold_space_T1w_path = bold_space_T1w_path_ls[0]
        bold_space_T1w_mask_path = os.path.join(sub_bold_dir, os.path.basename(bold_space_T1w_path).split('preproc_bold.nii.gz')[0] + 'brain_mask.nii.gz')
        bold_space_T1w_ref_path = os.path.join(sub_bold_dir, os.path.basename(bold_space_T1w_path).split('space-T1w')[0] + 'space-T1w_boldref.nii.gz')
    elif len(bold_space_T1w_path_ls) ==0:
        logger.warning('No space-T1w_desc-preproc_bold.nii.gz was found in directory ' + sub_bold_dir)
    else:
        logger.error('Found multiple space-T1w_desc-preproc_bold.nii.gz in directory ' + sub_bold_dir)
        raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')

    # locate bold_space_MNI152NLin2009cAsym
    bold_space_MNI152NLin2009cAsym_path_ls = glob.glob(os.path.join(sub_bold_dir, '*space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz'))
    if len(bold_space_MNI152NLin2009cAsym_path_ls) ==1:
        bold_space_MNI152NLin2009cAsym_path = bold_space_MNI152NLin2009cAsym_path_ls[0]
        bold_space_MNI152NLin2009cAsym_json_path = os.path.join(sub_bold_dir, os.path.basename(bold_space_MNI152NLin2009cAsym_path).split('.')[0] + '.json')
        bold_space_MNI152NLin2009cAsym_json = json.load(open(bold_space_MNI152NLin2009cAsym_json_path))
        bold_space_MNI152NLin2009cAsym_mask_path = os.path.join(sub_bold_dir, os.path.basename(bold_space_MNI152NLin2009cAsym_path).split('preproc_bold.nii.gz')[0] + 'brain_mask.nii.gz')
        bold_space_MNI152NLin2009cAsym_ref_path = os.path.join(sub_bold_dir, os.path.basename(bold_space_MNI152NLin2009cAsym_path).split('res-2')[0] + 'res-2_boldref.nii.gz')
    elif len(bold_space_MNI152NLin2009cAsym_path_ls) ==0:
        logger.warning('No space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz was found in directory ' + sub_bold_dir)
    else:
        logger.error('Found multiple space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz in directory ' + sub_bold_dir)
        raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')
    
    # extract TR
    try:
        TR = bold_space_MNI152NLin2009cAsym_json['RepetitionTime']
    except KeyError:
        logger.warning('failed to find RepetitionTime value in BOLD json, using default RepetitionTime value (TR = 2.0 s)')
        TR = 2.0
    
    if atlas_name.split('_')[-1] == 'T1w':
        bold_path = bold_space_T1w_path
        bold_mask_path = bold_space_T1w_mask_path
        bold_img_ref_path = bold_space_T1w_ref_path
    elif atlas_name.split('_')[-1] == 'MNI':
        bold_path = bold_space_MNI152NLin2009cAsym_path
        bold_mask_path = bold_space_MNI152NLin2009cAsym_mask_path
        bold_img_ref_path = bold_space_MNI152NLin2009cAsym_ref_path

    ## 协变量回归和平滑
    bold_img_clean_masked_sm_path = os.path.join(fmripost_sub_dir, os.path.basename(bold_path).split('.')[0] + '_' + args.clean_type + '_sm' + str(args.sm) + '.nii.gz')
    sample_mask = clean_and_smooth(bold_path, bold_mask_path, bold_img_clean_masked_sm_path, TR)
    
    ## 保存分割图png，用于QC
    parc_nii_path = atlas_config[atlas_name]['parc_nii']
    plotting.plot_roi(parc_nii_path, bg_img=bold_img_ref_path, title="parc", output_file = os.path.join(fmripost_sub_dir, subject_name + '_parc_' + atlas_name + '.png'))    


    ## 计算BOLD time series为csv
    masker = NiftiLabelsMasker(parc_nii_path, standardize=True, verbose=0)
    if args.clean_mode == 'clean_img':
        if args.no_sample_mask:
            time_series = masker.fit_transform(bold_img_clean_masked_sm_path)
        else:
            time_series = masker.fit_transform(bold_img_clean_masked_sm_path, sample_mask=sample_mask)
    elif args.clean_mode == 'clean_signal':
        time_series = masker.fit_transform(bold_img_clean_masked_sm_path)
    if time_series.shape[1] != len(sgm_lut['Name']):
        ## 处理节点missing的情况
        parc_img = load_img(parc_nii_path)
        atlas_values = set(get_data(parc_img).astype(int).ravel())
        logger.warning("empty regions:", set(range(max(atlas_values) + 1)).difference(atlas_values))
        logger.warning('WARNING: parcel number mismatch between time_series with LUT. Maybe after resampling the label image, some labels were removed')
        logger.warning('see ref in https://neurostars.org/t/few-rois-timeseries-are-not-extracted-from-the-schaefer-atlas-using-nilearn/23467')
        parc_nii = nib.load(parc_nii_path)
        bold_img_clean_masked_sm = nib.load(bold_img_clean_masked_sm_path)
        parc_resample_nii = resample_img(parc_nii, interpolation="nearest",target_shape=bold_img_clean_masked_sm.shape[:3],target_affine=bold_img_clean_masked_sm.affine)
        labels_before_resampling = np.unique(parc_nii.get_fdata())[1:]
        labels_after_resampling = np.unique(parc_resample_nii.get_fdata())[1:]
        missing_label_intensity = list(set(labels_before_resampling).difference(set(labels_after_resampling)))
        missing_label_atlas = [atlas_name] * len(missing_label_intensity)
        ## 保存missing节点的信息
        pd.DataFrame({'missing_nodes_intensity':missing_label_intensity, 'source':missing_label_atlas}).to_csv(os.path.join(fmripost_sub_dir, subject_name + '_parc_' + atlas_name + '_missing_nodes.csv'), index=False)
        ## 把0值插入BOLD timeseries
        time_series_new = np.zeros((time_series.shape[0],len(sgm_lut['Name'])))
        ctx = 0
        for idx in labels_after_resampling:
            time_series_new[:,int(idx)-1] = time_series[:,ctx]
            ctx = ctx + 1 
        time_series = time_series_new

    pd.DataFrame(time_series, columns=sgm_lut['Name']).to_csv(os.path.join(fmripost_sub_dir, subject_name + '_BOLD_' + output_str + '.csv'))
    logger.info('BOLD signals saved here ' + os.path.join(fmripost_sub_dir, subject_name + '_BOLD_' + output_str + '.csv'))

    ## 计算FC网络
    cm = ConnectivityMeasure(kind='correlation')
    corr_mat = cm.fit_transform([time_series])  # input = list with single matrix
    corr_mat = corr_mat.squeeze()
    np.fill_diagonal(corr_mat, 0)

    ## 保存FC网络为csv
    pd.DataFrame(corr_mat).to_csv(os.path.join(fmripost_sub_dir, subject_name + '_FC_mat_' + output_str + '.csv'), index=0,header=0)
    logger.info('FC matrix saved here ' + os.path.join(fmripost_sub_dir, subject_name + '_FC_mat_' + output_str + '.csv'))

    ## 保存FC网络为png
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(15, 15))
    display = plotting.plot_matrix(corr_mat,labels=list(sgm_lut['Name']),vmax=0.8, vmin=-0.8,reorder=False,figure=fig)
    plt.savefig(os.path.join(fmripost_sub_dir, subject_name + '_FC_mat_' + output_str + '.png'))
    



parser = argparse.ArgumentParser(description='Extract BOLD signals from fmriprep 4D niimg and calculate parcel-wise FC matrix')
parser.add_argument('bids_dir', help='The directory with the input dataset '
                        'formatted according to the BIDS standard.')
parser.add_argument('--participant_label', help='The label(s) of the participant(s) that should be analyzed. The label '
                    'corresponds to sub-<participant_label> from the BIDS spec '
                    '(so it does not include "sub-"). If this parameter is not '
                    'provided all subjects should be analyzed. Multiple '
                    'participants can be specified with a space separated list.',
                    nargs="+")
parser.add_argument('--session_label', help='The label of the session that should be analyzed. The label '
                    'corresponds to ses-<session_label> from the BIDS spec '
                    '(so it does not include "ses-"). If this parameter is not '
                    'provided, all sessions should be analyzed. Multiple '
                    'sessions can be specified with a space separated list.',
                    nargs="+")
parser.add_argument('-scripts_dir', help="path of current scripts", default='/pipeline')
parser.add_argument('-atlas_config', help="path of atlas_config.json", default='/pipeline/atlases/atlas_config.json')
parser.add_argument('-clean_type', metavar="str", choices=["compcor", "simple", "scrubbing", "basic18", "basic18-cs","basic36", "basic36-cs"],
                        help="Select fmri timeseries coufound regression strategy to use. "
                             "'compcor': A component based noise correction method (compcor) for bold and perfusion based fmri "
                             "'simple': With the global signal regression, this approach can remove confounds without compromising the temporal degrees of freedom. "
                             "'ica_aroma': Load confounds for non-aggresive ICA-AROMA strategy. "
                             "'basic18 (default)': six head motion parameters, averaged signals from cerebrospinal fluid, white matter, and global brain signal, as well as their temporal derivatives (18 regressors in total, (doi.org/10.1016/j.neuroimage.2021.117831)). "
                             "'basic18-cs': basic18 with volume censoring"
                             "'basic36': 36-parameter denoising strategy proposed by [Satterthwaite2013] "
                             "'basic36-cs': basic36 with volume censoring",
                        default="basic18")
parser.add_argument('-clean_mode', metavar="clean_signal|clean_img", choices=["clean_signal", "clean_img"],
                        help="Select fmri timeseries coufound regression strategy to use. "
                             "'clean_signal': using nilearn.signal.clean method (default)"
                             "'clean_img': using nilearn.image.clean_img method ",
                        default="clean_img")
parser.add_argument('-customized_atlas', 
                        help="Customized atlas to use. ",
                        default=False)
parser.add_argument('-atlases', 
                        help="Select predefined atlases to use. ",
                        nargs="+",
                        default="AAL3_MNI")
parser.add_argument("-sm", type=int, help="smooth kernel size", default=6)
parser.add_argument('-no_sample_mask', action="store_true",
                        help="make sure BOLD timepoints keep the same after denoise. ",
                        default=False)
parser.add_argument('-v', '--version', action='version',
                        version='BIDS-App version {}'.format(__version__))



start = time.time()

# define input directory
args = parser.parse_args()

# init config
scripts_dir = args.scripts_dir
atlas_dir = os.path.join(scripts_dir, 'atlases')
mrtrix_lut_dir = os.path.join(scripts_dir, 'mrtrix3', 'labelconvert')

# make output dir
fmripost_dir = os.path.join(args.bids_dir, 'derivatives', 'fmripost')
path.make_dir(fmripost_dir)

timestamp = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
log_path = os.path.join(fmripost_dir, 'runtime_' + timestamp + '.log')
# if os.path.exists(log_path):
#     os.remove(log_path)
logger.add(log_path,backtrace= True, diagnose=True)

## 图谱选择
atlas_config = read_json_file(args.atlas_config)
# atlases_ls = ['AAL3_MNI', 'desikan_T1w']
if args.customized_atlas:
    atlas_df = pd.read_csv(args.customized_atlas)
    atlases_ls = list(pd.unique(atlas_df['Source']))
else:
    atlases_ls = args.atlases

logger.info('Welcome to use fmripost pipeline (in dev)')
logger.info('Please feel free to contact the author (chenfei.ye@foxmail.com) if any bug was detected')
if args.customized_atlas:
    logger.info('The following customized atlas would be created: ' + args.customized_atlas)
logger.info('The following predefined atlases would be applied: ' + ' '.join(atlases_ls))

subjects_to_analyze = []
# only for a subset of subjects
if args.participant_label:
    subjects_to_analyze = args.participant_label
# for all subjects
else:
    subject_dirs = glob.glob(os.path.join(args.bids_dir, "sub-*"))
    subjects_to_analyze = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]

# only use a subset of sessions
if args.session_label:
    session_to_analyze = dict(session=args.session_label)
else:
    session_to_analyze = dict()

subjects_to_analyze.sort()
logger.info(str(len(subjects_to_analyze)) + ' subjects detected to process, including ' + ' '.join(subjects_to_analyze))

# running participant level
fmriprep_dir = os.path.join(args.bids_dir, 'derivatives', 'fmriprep')

for subject_label in subjects_to_analyze:
    subject_name = 'sub-' + subject_label
    sub_bold_dir = os.path.join(fmriprep_dir, subject_name, 'func')
    logger.info('Processing subject: ' + subject_name)

    # 初始化输出路径 
    fmripost_sub_dir = os.path.join(fmripost_dir, subject_name)
    path.make_dir(fmripost_sub_dir)
     
    freesurfer_path = os.path.join(args.bids_dir, 'derivatives', 'freesurfer', subject_name)

    ## 对每个图谱分别计算FC
    output_str_dict = {}
    for atlas_name in atlases_ls:
        # convert from FreeSurfer Space Back to Native Anatomical Space (https://surfer.nmr.mgh.harvard.edu/fswiki/FsAnat-to-NativeAnat)
        if atlas_name == 'desikan_T1w':
            parc_native_path = os.path.join(freesurfer_path, 'mri', 'aparc+aseg.mgz')
            parc_lut_file = os.path.join(mrtrix_lut_dir, 'FreeSurferColorLUT.txt')
            mrtrix_lut_file = os.path.join(mrtrix_lut_dir, 'fs_default.txt')
            parc_T1w_nii_path = os.path.join(fmripost_sub_dir, subject_name + '_T1w_desikan.nii.gz')
        elif atlas_name == 'destrieux_T1w':
            parc_native_path = os.path.join(freesurfer_path, 'mri', 'aparc.a2009s+aseg.mgz')
            parc_lut_file = os.path.join(mrtrix_lut_dir, 'FreeSurferColorLUT.txt')
            mrtrix_lut_file = os.path.join(mrtrix_lut_dir, 'fs_a2009s.txt')
            parc_T1w_nii_path = os.path.join(fmripost_sub_dir, subject_name + '_T1w_destrieux.nii.gz')
        elif atlas_name == 'hcpmmp_T1w':
            parc_native_path = os.path.join(freesurfer_path, 'mri', 'aparc.HCPMMP1+aseg.mgz')
            if not os.path.exists(parc_native_path):
                logger.error('Failed to detect ' + parc_native_path + ', should run docker image bids-freesurfer /hcpmmp_conv.py first')
                raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')

            parc_lut_file = os.path.join(mrtrix_lut_dir, 'hcpmmp1_original.txt')
            mrtrix_lut_file = os.path.join(mrtrix_lut_dir, 'hcpmmp1_ordered.txt')
            parc_T1w_nii_path = os.path.join(fmripost_sub_dir, subject_name + '_T1w_hcpmmp.nii.gz')

        elif atlas_name == 'schaefer100x7_T1w':
            parc_native_path = os.path.join(freesurfer_path, 'mri', 'aparc.schaefer100x7+aseg.mgz')
            if not os.path.exists(parc_native_path):
                logger.error('Failed to detect ' + parc_native_path + ', should run docker image bids-freesurfer /surf_conv.py first')
                raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')
            
            parc_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer100x7_original.txt')
            mrtrix_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer100x7_ordered.txt')
            parc_T1w_nii_path = os.path.join(fmripost_sub_dir, subject_name + '_T1w_schaefer100x7.nii.gz')
        
        elif atlas_name == 'schaefer200x7_T1w':
            parc_native_path = os.path.join(freesurfer_path, 'mri', 'aparc.schaefer200x7+aseg.mgz')
            if not os.path.exists(parc_native_path):
                logger.error('Failed to detect ' + parc_native_path + ', should run docker image bids-freesurfer /surf_conv.py first')
                raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')
            
            parc_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer200x7_original.txt')
            mrtrix_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer200x7_ordered.txt')
            parc_T1w_nii_path = os.path.join(fmripost_sub_dir, subject_name + '_T1w_schaefer200x7.nii.gz')
        
        elif atlas_name == 'schaefer400x7_T1w':
            parc_native_path = os.path.join(freesurfer_path, 'mri', 'aparc.schaefer400x7+aseg.mgz')
            if not os.path.exists(parc_native_path):
                logger.error('Failed to detect ' + parc_native_path + ', should run docker image bids-freesurfer /surf_conv.py first')
                raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')
            
            parc_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer400x7_original.txt')
            mrtrix_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer400x7_ordered.txt')
            parc_T1w_nii_path = os.path.join(fmripost_sub_dir, subject_name + '_T1w_schaefer400x7.nii.gz')
        
        elif atlas_name == 'schaefer1000x7_T1w':
            parc_native_path = os.path.join(freesurfer_path, 'mri', 'aparc.schaefer1000x7+aseg.mgz')
            if not os.path.exists(parc_native_path):
                logger.error('Failed to detect ' + parc_native_path + ', should run docker image bids-freesurfer /surf_conv.py first')
                raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')
            
            parc_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer1000x7_original.txt')
            mrtrix_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer1000x7_ordered.txt')
            parc_T1w_nii_path = os.path.join(fmripost_sub_dir, subject_name + '_T1w_schaefer1000x7.nii.gz')
        
        elif atlas_name == 'schaefer100x17_T1w':
            parc_native_path = os.path.join(freesurfer_path, 'mri', 'aparc.schaefer100x17+aseg.mgz')
            if not os.path.exists(parc_native_path):
                logger.error('Failed to detect ' + parc_native_path + ', should run docker image bids-freesurfer /surf_conv.py first')
                raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')
            
            parc_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer100x17_original.txt')
            mrtrix_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer100x17_ordered.txt')
            parc_T1w_nii_path = os.path.join(fmripost_sub_dir, subject_name + '_T1w_schaefer100x17.nii.gz')
        
        elif atlas_name == 'schaefer200x17_T1w':
            parc_native_path = os.path.join(freesurfer_path, 'mri', 'aparc.schaefer200x17+aseg.mgz')
            if not os.path.exists(parc_native_path):
                logger.error('Failed to detect ' + parc_native_path + ', should run docker image bids-freesurfer /surf_conv.py first')
                raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')
            
            parc_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer200x17_original.txt')
            mrtrix_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer200x17_ordered.txt')
            parc_T1w_nii_path = os.path.join(fmripost_sub_dir, subject_name + '_T1w_schaefer200x17.nii.gz')
        
        elif atlas_name == 'schaefer400x17_T1w':
            parc_native_path = os.path.join(freesurfer_path, 'mri', 'aparc.schaefer400x17+aseg.mgz')
            if not os.path.exists(parc_native_path):
                logger.error('Failed to detect ' + parc_native_path + ', should run docker image bids-freesurfer /surf_conv.py first')
                raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')
            
            parc_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer400x17_original.txt')
            mrtrix_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer400x17_ordered.txt')
            parc_T1w_nii_path = os.path.join(fmripost_sub_dir, subject_name + '_T1w_schaefer400x17.nii.gz')
        
        elif atlas_name == 'schaefer1000x17_T1w':
            parc_native_path = os.path.join(freesurfer_path, 'mri', 'aparc.schaefer1000x17+aseg.mgz')
            if not os.path.exists(parc_native_path):
                logger.error('Failed to detect ' + parc_native_path + ', should run docker image bids-freesurfer /surf_conv.py first')
                raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')
            
            parc_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer1000x17_original.txt')
            mrtrix_lut_file = os.path.join(mrtrix_lut_dir, 'schaefer1000x17_ordered.txt')
            parc_T1w_nii_path = os.path.join(fmripost_sub_dir, subject_name + '_T1w_schaefer1000x17.nii.gz')

        if atlas_name.split('_')[1] == 'T1w':
            if not os.path.exists(freesurfer_path):
                logger.error("Failed to detect /derivatives/freesurfer for subject " + subject_name)
                raise MRtrixError('Failed to complete, please see fmripost_dir/runtime.log for details')
            if os.path.exists(parc_T1w_nii_path):
                logger.warning("found results of freesurfer post-processing, jump this step")
            else:
                logger.info("start running freesurfer post-processing")
                run.command('labelconvert ' + parc_native_path + ' ' + parc_lut_file + ' ' + mrtrix_lut_file + ' ' + parc_T1w_nii_path)
            atlas_config[atlas_name]['parc_nii'] = parc_T1w_nii_path

        output_str = atlas_name + '_' + args.clean_type + '_sm' + str(args.sm)
        FC_atlas_calc(args, sub_bold_dir, atlas_config, atlas_name)
        output_str_dict[atlas_name] = output_str
        logger.info('finished fmripost processing ' + subject_name + ' for ' + atlas_name)
    
    ## 对自定义图谱，汇总脑区BOLD信号，计算FC
    BOLD_dict = {}
    for atlas_name in atlases_ls:
        BOLD_csv = os.path.join(fmripost_sub_dir, subject_name + '_BOLD_' + output_str_dict[atlas_name] + '.csv')
        BOLD_dict[atlas_name] = pd.read_csv(BOLD_csv, index_col=0)

    # 重组BOLD
    if args.customized_atlas:
        BOLD_mat = np.zeros((len(BOLD_dict[atlas_name]), len(atlas_df)))
        for id in atlas_df['Index']:
            node = atlas_df.loc[lambda x: x['Index'] == id]['Node']
            source = atlas_df.loc[lambda x: x['Index'] == id]['Source']
            BOLD_mat[:,id-1] = BOLD_dict[source.values[0]][node.values[0]]

        ## 保存BOLD为csv
        BOLD_csv_path = subject_name + '_BOLD_' + output_str_dict[atlas_name] + '.csv'
        BOLD_csv_path = BOLD_csv_path.replace(atlas_name, os.path.basename(args.customized_atlas).split('.')[0], 1)
        pd.DataFrame(BOLD_mat, columns=list(atlas_df['Node'])).to_csv(os.path.join(fmripost_sub_dir, BOLD_csv_path))

        ## 计算FC网络
        cm = ConnectivityMeasure(kind='correlation')
        corr_mat = cm.fit_transform([BOLD_mat])  # input = list with single matrix
        corr_mat = corr_mat.squeeze()
        np.fill_diagonal(corr_mat, 0)

        ## 保存FC网络为csv
        FC_csv_path = subject_name + '_FC_mat_' + output_str_dict[atlas_name] + '.csv'
        FC_csv_path = FC_csv_path.replace(atlas_name, os.path.basename(args.customized_atlas).split('.')[0], 1)
        pd.DataFrame(corr_mat).to_csv(os.path.join(fmripost_sub_dir, FC_csv_path), index=0,header=0)

        ## 保存FC网络为png
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(15, 15))
        display = plotting.plot_matrix(corr_mat,labels=list(atlas_df['Node']),vmax=0.8, vmin=-0.8,reorder=False,figure=fig)
        FC_png_path = subject_name + '_FC_mat_' + output_str_dict[atlas_name] + '.png'
        FC_png_path = FC_png_path.replace(atlas_name, os.path.basename(args.customized_atlas).split('.')[0], 1)
        plt.savefig(os.path.join(fmripost_sub_dir, subject_name + '_FC_mat_' + output_str + '.png'))
        logger.info('finished fmripost processing ' + subject_name + ' for the customized brain atlas')

    
end = time.time()
running_time = end - start
logger.info('running time: {:.0f}min {:.0f}sec'.format(running_time//60, running_time % 60))
logger.info('Successfully finished')

    