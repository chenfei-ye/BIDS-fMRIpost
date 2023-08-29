# import vtk
import os
from mrtrix3 import MRtrixError
from mrtrix3 import app
import nibabel as nib
import numpy as np
import json


def read_json_file(json_file):
    """
    read json file
    :param json_file:
    :return:
    """
    if not json_file or not os.path.exists(json_file):
        print('json file %s not exist' % json_file)
        return None

    with open(json_file, 'r', encoding='utf-8') as fp:
        out_dict = json.load(fp)

    return out_dict


def write_json_file(file, content, ensure_ascii=True, sort_keys=True):
    """
    write dictionary into a json file
    :param file:
    :param content:
    :param ensure_ascii:
    :param sort_keys:
    :return:
    """
    with open(file, 'w+', encoding='utf-8') as fp:
        try:
            fp.write(json.dumps(content, indent=2, ensure_ascii=ensure_ascii, sort_keys=sort_keys))
        except TypeError:
            use_content = dict()
            for key, value in content.items():
                use_content[str(key)] = value

            fp.write(json.dumps(use_content, indent=2, ensure_ascii=ensure_ascii, sort_keys=sort_keys))

# def MarchingCubes(image,threshold): 
#     mc = vtk.vtkMarchingCubes()
#     mc.SetInputData(image)
#     # mc.ComputeNormalsOn()
#     # mc.ComputeGradientsOn()
#     mc.SetValue(0, threshold)
#     mc.Update()
#     return mc.GetOutput()
    

# def Smooth_vtk_data(stl, smoothing_iterations = 15,pass_band = 0.001,feature_angle = 120.0):
#     smoother = vtk.vtkWindowedSincPolyDataFilter()
#     smoother.SetInputData(stl)
#     smoother.SetNumberOfIterations(smoothing_iterations)
#     smoother.BoundarySmoothingOff()
#     smoother.FeatureEdgeSmoothingOff()
#     smoother.SetFeatureAngle(feature_angle)
#     smoother.SetPassBand(pass_band)
#     smoother.NonManifoldSmoothingOn()
#     smoother.NormalizeCoordinatesOn()
#     smoother.Update()
#     return smoother.GetOutput()
    

# def DoGaussSmooth(input_data):
#     # Gaussian smoothing of surface rendering for aesthetics
#     # Adds significant delay to rendering
#     smoother = vtk.vtkImageGaussianSmooth()
#     smoother.SetDimensionality(3)    
#     #smoother.SetRadiusFactors(0.5,0.5,0.5)
#     smoother.SetRadiusFactors(0.05,0.05,0.05)
#     smoother.SetInputData(input_data)
#     smoother.Update()
#     return smoother.GetOutput()
    


# def GetNormalsPolyData(input_data):
#     normalGenerator = vtk.vtkPolyDataNormals()
#     normalGenerator.SetInputData(input_data)
#     normalGenerator.ComputePointNormalsOn()
#     normalGenerator.ComputeCellNormalsOn()
#     normalGenerator.Update()
#     return normalGenerator.GetOutput()
    
  
# def NIFTItoVTKandVTP(niftiFilePath, VTKFilePath=None, VTPFilePath=None):
#     reader = vtk.vtkNIFTIImageReader()
#     reader.SetFileName(niftiFilePath)
#     reader.SetFileLowerLeft(0)
#     reader.Update()
#     im = reader.GetOutput()
#     # image_origin = reader.GetDataOrigin()
#     # nifti_header = reader.GetNIFTIHeader()
#     # qoffset_x = nifti_header.GetQOffsetX()
#     # qoffset_y = nifti_header.GetQOffsetY()
#     # qoffset_z = nifti_header.GetQOffsetZ()

    
#     # do marching cubes for raw nifti data  
#     gauss_out=DoGaussSmooth(im)
#     poly = MarchingCubes(gauss_out,0.1)
#     smooth_data = Smooth_vtk_data(poly, smoothing_iterations = 10,pass_band = 0.02,feature_angle = 120.0)
#     normal_data = GetNormalsPolyData(smooth_data)

#     # save as vtk
#     if VTKFilePath:
#         writer = vtk.vtkPolyDataWriter()
#         writer.SetInputData(normal_data)
#         writer.SetFileName(VTKFilePath)
#         writer.Write()
#         if not os.path.exists(VTKFilePath):
#             raise MRtrixError('Failed to run nii2vtk')


#     # save as vtp
#     if VTPFilePath:
#         writer = vtk.vtkXMLPolyDataWriter()
#         writer.SetInputData(normal_data)
#         writer.SetFileName(VTPFilePath)
#         writer.Write()
#         if not os.path.exists(VTPFilePath):
#             raise MRtrixError('Failed to run nii2vtp')


# def ROI_VIS_ALL(niftiFilePath, output_dir):
#     niftiFile = nib.load(niftiFilePath)
#     niftiIMG = niftiFile.get_fdata()
#     roi = np.unique(niftiIMG)
#     roi_num = len(roi)
#     progress = app.ProgressBar('RUN NII to VTP', roi_num)
#     for item in range(roi_num):
#         output_vtp = os.path.join(output_dir, 'ROI_' + str(int(roi[item]))+ '.vtp')
#         NIFTItoVTKandVTP(niftiFilePath, VTKFilePath=None, VTPFilePath=output_vtp)
#         progress.increment()
#     progress.done()
