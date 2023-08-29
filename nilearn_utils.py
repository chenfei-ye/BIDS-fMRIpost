# -*- coding: utf-8 -*-

"""
@author: Chenfei
@contact:chenfei.ye@foxmail.com
@version: 1.0
@file: nilearn_utils.py
@time: 2023/03/22
# utilities for nilearn process
"""

preset_strategies = {
    "simple": {
        "strategy":
            ("high_pass", "motion", "wm_csf"),
        "motion": "full",
        "wm_csf": "basic",
        "global_signal": None,
        "demean": True
    },
    "compcor": {
        "strategy":
            ("high_pass", "motion", "compcor"),
        "motion": "full",
        "n_compcor": "all",
        "compcor": "anat_combined",
        "demean": True
    },
    "ica_aroma": {
        "strategy":
            ("high_pass", "wm_csf", "ica_aroma"),
        "wm_csf": "basic",
        "ica_aroma": "full",
        "global_signal": None,
        "demean": True
    },
    "basic18": {
        "strategy":
            ('motion', 'wm_csf', 'global_signal'),
        "motion": "derivatives",
        "wm_csf": "derivatives",
        "global_signal": "derivatives",
        "demean": True
    },
    # cs: censoring for bold timeframes 
    "basic18-cs": {
        "strategy":
            ('motion', 'wm_csf', 'global_signal', 'scrub'),
        "motion": "derivatives",
        "wm_csf": "derivatives",
        "global_signal": "derivatives",
        "scrub": 0, 
        "fd_threshold": 0.5, 
        # "std_dvars_threshold": 1.5,
        "demean": True
    },
    "basic36": {
        "strategy":
            ('motion', 'wm_csf', 'global_signal'),
        "motion": "full",
        "wm_csf": "full",
        "global_signal": "full",
        "demean": True
    },
    # cs: censoring for bold timeframes 
    "basic36-cs": {
        "strategy":
            ('motion', 'wm_csf', 'global_signal', 'scrub'),
        "motion": "full",
        "wm_csf": "full",
        "global_signal": "full",
        "scrub": 0, 
        "fd_threshold": 0.5, 
        # "std_dvars_threshold": 1.5,
        "demean": True
    }
}