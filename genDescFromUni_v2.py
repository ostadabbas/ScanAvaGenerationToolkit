# ------------------------------------ USER PARAMS ------------------------------------ #
# This directory should contain augmentation code, and matfiles as a subfolder
blender_folder_path = '/home/sehgal.n/augmentation_code'  # note that the dataset will be output here
py35_package_path = '/home/sehgal.n/miniconda3/envs/py35/lib/python3.5/site-packages'  # py35 packages for blender
degree = 35  # Set to 35 for 35 degrees
Npose = 2000  # Number of poses
# ------------------------------------------------------------------------------------- #

# Include conda packages and other file dependencies
import sys
sys.path.append(py35_package_path)
sys.path.append(blender_folder_path)

# test script for joint control 
import scipy.io as sio
from math import *
import pdb
import numpy as np 
import pickle 
import os
import datetime 
import bpy
import mathutils
import random 
import GenDataFromDesFunV4 as GenData
from functools import reduce


def DegToRad(degrees):  # not used 
    rads = list(radians(degree) for degree in degrees)
    return rads


def GenEulerUni(lmt_joints):
    """
    Generate the 14x3 angles uniformly distributed within the in range of lmb_joitns indicated
    input, lmb_joints 14x6  each row [x_l, x_r, y_l, y_r, z_l,z_r],...
    For joint angle, refer to the our coordinate shematic
    return: a list of 14x3 with the euler angle in each row
    history,  17.10.27  add the z rotation to descriptor, last row becomes [zRot (rad), 0,0]
            Shuangjun
    """

    lmt_jointsArr = np.array(lmt_joints)
    THblock = np.random.uniform(lmt_jointsArr[:2, ::2], lmt_jointsArr[:2, 1::2])

    Lblock = np.random.uniform(lmt_jointsArr[2:, ::2], lmt_jointsArr[2:, 1::2])

    matRflip = np.array([[-1, -1, 1], [1, 1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1]])
    Rblock = np.multiply(np.random.uniform(lmt_jointsArr[2:, ::2], lmt_jointsArr[2:, 1::2]), matRflip)

    eulers_angles = np.concatenate((THblock, Lblock[:3], Rblock[:3], Lblock[3:], Rblock[3:]))  # axis 0 is vertical

    return eulers_angles


# to current dir
os.chdir(blender_folder_path)
cenPhi = pi*degree/180   # view point

# camera control range  here is the spherical coordinates
thetaRg = [0, 2*pi]  # theta range
phiRg = [pi/2 - pi/18 - cenPhi, pi/2+pi/18 - cenPhi]  # phi range nearly horizontal
rhoRg = [2.8, 3.3]
avRho = reduce(lambda x, y: x+y, rhoRg)/len(rhoRg)
rotZrg = [-pi/60, pi/60]   # make it very small one
Ntotal = Npose      # There is only one camera viewpoint per pose, so NTotal = NPose
dsFd = os.getcwd()  # dsFd to current directory

# Generate file path
setSuffix = '_P' + str(Npose)+'_A{:02d}'.format(int(np.rad2deg(cenPhi)))   # even round 45.0
now = datetime.datetime.now()
filePth = bpy.data.filepath
print(filePth)

blFileNm = os.path.splitext(os.path.basename(filePth))[0]
print('generating from blender file {}'.format(blFileNm))

setNm = 'SYN_UNI__' + blFileNm + now.strftime("_G%Y%m%d_%H%M") + setSuffix  # dynamic date setNm
setPath = os.path.join(dsFd, setNm)

if not os.path.exists(setPath):
    os.makedirs(setPath)


# generate bound  torso, head, left arm, right arm , l leg, r leg  14x3 
lmt_joints = [[0, 0, 0, 0, 0, 0],              # torso fixed
              [-10, 10, -10, 10, -10, 10],     # head
              [5, -100, -10, 10, -30, 160],    # shoulder
              [0, 0, 0, 0, 0, 135],            # elbow
              [-10, 10, -10, 10, -10, 10],     # wrist
              [-5, 45, -30, 45, -45, 30],      # hip
              [0, 0, 0, 0, 0, 135],            # knee
              [-10, 10, -10, 10, -10, 10]      # ankle
              ]

# initialize the result array first 
conParFrm = np.zeros((Ntotal, 16, 3))  # first Ncam has same Npos parameters

# just map the image to the descriptor directly
print('generating descriptor for ', setNm)

# Set pose and camera
for idPose in range(Npose):
    # Set joint angles
    eulers = GenEulerUni(lmt_joints)
    conParFrm[idPose:(idPose+1), :14] = np.tile(eulers, (1, 1, 1))

    # Set camera
    theta = np.random.uniform(thetaRg[0], thetaRg[1])
    phi = np.random.uniform(phiRg[0], phiRg[1])
    rho = np.random.uniform(rhoRg[0], rhoRg[1])
    conParFrm[idPose, 14] = np.array([rho, theta, phi])
    conParFrm[idPose, 15, 0] = np.random.uniform(rotZrg[0], rotZrg[1])

# save file to pickle binary file
print('save to set', setPath)

afile = open(os.path.join(setPath, 'conParFrm.pkl'), 'wb')
print('conParFrm has size', conParFrm.size)

pickle.dump(conParFrm, afile)
afile.close()

GenData.GenDataset(setNm, avRho, dsFd)
