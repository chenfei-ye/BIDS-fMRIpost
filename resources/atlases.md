# Brain Atlases

## Standard Atlases
- `AAL1_MNI`：An automated anatomical parcellation of the spatially normalized single-subject high-resolution T1 volume provided by the Montreal Neurological Institute (MNI)
- `AAL2_MNI`：New version of orbital frontal cortex parcelation, released on the 27th of August 2015
- `AAL3_MNI`：New version of anterior cingulate, thalamus and brain nuclei (nucleus accumbens, substantia nigra, ventral tegmental area, red nucleus, locus coeruleus, and raphe nuclei), released on the 30th of August, 2019
-   `schaefer100x7_MNI`: Multiscale local-global functional atlas from Schaefer and colleagues: 100-node resolution with 7 networks
-   `schaefer200x7_MNI`: Multiscale local-global functional atlas from Schaefer and colleagues: 200-node resolution with 7 networks
-   `schaefer400x7_MNI`: Multiscale local-global functional atlas from Schaefer and colleagues: 400-node resolution with 7 networks
-   `schaefer1000x7_MNI`: Multiscale local-global functional atlas from Schaefer and colleagues: 1000-node resolution with 7 networks
-   `schaefer100x17_MNI`: Multiscale local-global functional atlas from Schaefer and colleagues: 100-node resolution with 17 networks
-   `schaefer200x17_MNI`: Multiscale local-global functional atlas from Schaefer and colleagues: 200-node resolution with 17 networks
-   `schaefer400x17_MNI`: Multiscale local-global functional atlas from Schaefer and colleagues: 400-node resolution with 17 networks
-   `schaefer1000x17_MNI`: Multiscale local-global functional atlas from Schaefer and colleagues: 1000-node resolution with 17 networks
- `PD25_MNI`: This set of multi-contrast population-averaged PD brain atlas contains 5 different image contrasts: T1w ( FLASH & MPRAGE), T2 star, T1–T2 star fusion, phase, and an R2 star map. Probabilistic tissue maps of whiter matter, grey matter, and cerebrospinal fluid are provided for the atlas. We also manually segmented eight subcortical structures: caudate nucleus, putamen, globus pallidus internus and externus (GPi & GPe), thalamus, STN, substantia nigra (SN), and the red nucleus (RN).  See details [here](https://nist.mni.mcgill.ca/multi-contrast-pd25-atlas/)
- `JHUwm48_MNI`: 48 white matter tract labels were created by hand segmentation of a standard-space average of diffusion MRI tensor maps from 81 subjects; mean age 39 (18:59), M:42, F: 39. The diffusion data was kindly provided by the ICBM DTI workgroup. kindly provided by Dr. Susumu Mori, [Laboratory of Brain Anatomical MRI](http://cmrm.med.jhmi.edu/), Johns Hopkins University. ref: Hua et al., Tract probability maps in stereotaxic spaces: analysis of white matter anatomy and tract-specific quantification. NeuroImage, 39(1):336-347 (2008)

- `desikan_T1w`：Desikan-Killiany Atlas (?h.aparc.annot) included inside FreeSurfer
- `destrieux_T1w`: Destrieux Atlas (?h.aparc.a2009s.annot) Atlas (?h.aparc.annot) included inside FreeSurfer
- `hcpmmp_T1w` : HCP-MMP1.0 parcellation by [Glasser et al. (Nature)](http://www.nature.com/nature/journal/v536/n7615/full/nature18933.html). See details [here](https://cjneurolab.org/2016/11/22/hcp-mmp1-0-volumetric-nifti-masks-in-native-structural-space/).
-   `schaefer100x7_T1w`: Multiscale local-global functional atlas from Schaefer and colleagues: 100-node resolution with 7 networks
-   `schaefer200x7_T1w`: Multiscale local-global functional atlas from Schaefer and colleagues: 200-node resolution with 7 networks
-   `schaefer400x7_T1w`: Multiscale local-global functional atlas from Schaefer and colleagues: 400-node resolution with 7 networks
-   `schaefer1000x7_T1w`: Multiscale local-global functional atlas from Schaefer and colleagues: 1000-node resolution with 7 networks
-   `schaefer100x17_T1w`: Multiscale local-global functional atlas from Schaefer and colleagues: 100-node resolution with 17 networks
-   `schaefer200x17_T1w`: Multiscale local-global functional atlas from Schaefer and colleagues: 200-node resolution with 17 networks
-   `schaefer400x17_T1w`: Multiscale local-global functional atlas from Schaefer and colleagues: 400-node resolution with 17 networks
-   `schaefer1000x17_T1w`: Multiscale local-global functional atlas from Schaefer and colleagues: 1000-node resolution with 17 networks


## How to add new atlas in bids-fmripost?
1. Before doing this, please make sure your new atlas is in MNI space
2. Create the label image. Usually, the new atlas would be merged from multiple standard atlases. In this case, you can edited the input standard atlases using [ITKSnap](http://itksnap.org/), and merged them using [mrcalc](https://mrtrix.readthedocs.io/en/latest/reference/commands/mrcalc.html). Then move this label image into `atlases` folder. See example in `/atlases/AAL1PD25-woSTN-GPi_MNI.nii.gz`
3. Create the sidecar atlas dictionary file in csv format. Then move this csv file into `atlases` folder. See example in `/atlases/AAL1PD25-woSTN-GPi_MNI.csv`
4. Added atlas information in `/atlases/atlas_config_docker.json`
5. Done.

## How to customize ROI (brain parcels) for FC network creation?
This is easy. 
The only thing you need to do is to create a new atlas dictionary file in `/atlases` folder. See example in `/atlases/brain_nodes_cye3.csv`. Then run bids-fmripost with input argument `-atlases your_atlas_path`. 


## Reference
Automated anatomical labelling atlas 3. Rolls, E. T., Huang, C. C., Lin, C. P., Feng, J., & Joliot, M.,  _Neuroimage,_ 2020,  _206_, 116189, doi:[10.1016/j.neuroimage.2019.116189](https://www.sciencedirect.com/science/article/pii/S1053811919307803)

Implementation of a new parcellation of the orbitofrontal cortex in the automated anatomical labeling atlas. Rolls ET, Joliot M & Tzourio-Mazoyer N.  _NeuroImage_  2015, 122: 1-5.  
[http://dx.doi.org/10.1016/j.neuroimage.2015.07.075](http://dx.doi.org/10.1016/j.neuroimage.2015.07.075)

Automated Anatomical Labeling of Activations in SPM Using a Macroscopic Anatomical Parcellation of the MNI MRI Single-Subject Brain. N. Tzourio-Mazoyer, B. Landeau, D. Papathanassiou, F. Crivello, O. Étard, N. Delcroix, B. Mazoyer, and M. Joliot.  _NeuroImage_  2002, 15 :273-289  
[http://dx.doi.org/10.1006/nimg.2001.0978](http://dx.doi.org/10.1006/nimg.2001.0978)

[An automated labeling system for subdividing the human cerebral cortex on MRI scans into gyral based regions of interest](https://surfer.nmr.mgh.harvard.edu/ftp/articles/desikan06-parcellation.pdf), Desikan et al., (2006).  [NeuroImage](https://surfer.nmr.mgh.harvard.edu/fswiki/NeuroImage), 31(3):968-80.

[Automatically Parcellating the Human Cerebral Cortex](https://surfer.nmr.mgh.harvard.edu/ftp/articles/fischl04-parcellation.pdf), Fischl et al., (2004). Cerebral Cortex, 14:11-22.

Glasser, Matthew F. A multi-modal parcellation of human cerebral cortex. Nature 536, 171–178 (11 August 2016). [http://www.nature.com/nature/journal/vaop/ncurrent/full/nature18933.html](http://www.nature.com/nature/journal/vaop/ncurrent/full/nature18933.html)

Mills, Kathryn (2016): HCP-MMP1.0 projected on fsaverage. figshare. [https://dx.doi.org/10.6084/m9.figshare.3498446.v2](https://dx.doi.org/10.6084/m9.figshare.3498446.v2) Retrieved: 08 57, Nov 22, 2016 (GMT)

Yeo BT, Krienen FM, Sepulcre J, Sabuncu MR, Lashkari D, Hollinshead M, Roffman JL, Smoller JW, Zöllei L, Polimeni JR, Fischl B, Liu H, Buckner RL. The organization of the human cerebral cortex estimated by intrinsic functional connectivity. J Neurophysiol. 2011 Sep;106(3):1125-65. [doi: 10.1152/jn.00338.2011.](https://journals.physiology.org/doi/full/10.1152/jn.00338.2011#) 
