# ------------------------------------ USER PARAMS ------------------------------------ #
# This directory should contain augmentation code, and matfiles as a subfolder
blender_folder_path = '/home/sehgal.n/augmentation_code'  # note that the dataset will be output here
py35_package_path = '/home/sehgal.n/miniconda3/envs/py35/lib/python3.5/site-packages'  # py35 packages for blender
degree = 0  # Set to 35 for 35 degrees
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


# to current dir
os.chdir(blender_folder_path)
print('checkpoint 2')
matContents = sio.loadmat('matFiles/jointsR_tar_Ry.mat')  # for AR
jointsR_tar = matContents['jointsR_tar']
print('loaded total poses: ', jointsR_tar.shape[3])  # 3x3x14xN

cenPhi = pi*degree/180   # view point

# camera control range  here is the spherical coordinates
thetaRg = [0, 2*pi]  # theta range
phiRg = [pi/2 - pi/18 - cenPhi, pi/2+pi/18 - cenPhi]  # phi range nearly horizontal
rhoRg = [2.8, 3.3]
avRho = reduce(lambda x, y: x+y, rhoRg)/len(rhoRg)
rotZrg = [-pi/60, pi/60]   # make it very small one

print('checkpoint 2')

if not Npose == jointsR_tar.shape[3]:
    print('random pick ', Npose, 'poses')
    randFlg = 1
    idSeq = random.sample(range(jointsR_tar.shape[3]),Npose)

else:
    print('general all in order')
    idSeq = np.arange(Npose)

if Npose > jointsR_tar.shape[3]:
    print("Pose needed is over the jointsR_tar contents")
    quit()

Ntotal = Npose      # version two
dsFd = os.getcwd()  # dsFd to current directory

# Generate file path
setSuffix = '_P' + str(Npose)+'_A{:02d}'.format(int(np.rad2deg(cenPhi)))   # even round 45.0
now = datetime.datetime.now()
filePth = bpy.data.filepath
print(filePth)

blFileNm = os.path.splitext(os.path.basename(filePth))[0]
print('generating from blender file {}'.format(blFileNm))

setNm = 'SYN_RR_' + blFileNm + now.strftime("_G%Y%m%d_%H%M") + setSuffix  # dynamic date setNm
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

for i in range(Npose):
    eulers = np.zeros((14, 3))   # initialization

    for idJt in range(14):
        jointR = jointsR_tar[:, :, idJt, idSeq[i]]
        conParFrm[i, idJt, :] = np.rad2deg(mathutils.Matrix(jointR).to_euler())
        # for cam

        theta = np.random.uniform(thetaRg[0], thetaRg[1])
        phi = np.random.uniform(phiRg[0], phiRg[1])
        rho = np.random.uniform(rhoRg[0], rhoRg[1])
        conParFrm[i, 14] = np.array([rho, theta, phi])
        conParFrm[i, 15, 0] = np.random.uniform(rotZrg[0], rotZrg[1])

# save file to pickle binary file
print('save to set', setPath)

afile = open(os.path.join(setPath, 'conParFrm.pkl'), 'wb')
print('conParFrm has size', conParFrm.size)

pickle.dump(conParFrm, afile)
afile.close()

GenData.GenDataset(setNm, avRho, dsFd)
