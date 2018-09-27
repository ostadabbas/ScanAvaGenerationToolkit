# test script for joint control 
import bpy
import mathutils
from math import *
import pdb
import scipy.io as sio
import os
import random 


def DegToRad(degrees):  # not used 
    rads = list(radians(degree) for degree in degrees)
    return rads


def pause():
    programPause = input("Press the <ENTER> key to continue...")


# path to current 
os.chdir(bpy.path.abspath('//'))

# offset of two feet 
offsetFtL = degrees(bpy.data.objects['Armature'].data.bones['foot.L'].matrix.to_euler().z+ pi/2)
offsetFtR = degrees(bpy.data.objects['Armature'].data.bones['foot.R'].matrix.to_euler().z+ pi/2)


# global, define the joint list, must set in predefined sequence
# as we need to give in the target rotations, 
eulerStdDic = {'root': mathutils.Euler((pi/2, 0, 0)),
               'head': mathutils.Euler((0, 0, 0)),
               'upperArm.L': mathutils.Euler((pi, pi/2, 0)),
               'lowerArm.L': mathutils.Euler((0, 0, 0)),
               'palm.L': mathutils.Euler((0, 0, 0)),
               'upperArm.R': mathutils.Euler((pi, pi/2, 0)),
               'lowerArm.R': mathutils.Euler((0, 0, 0)),
               'palm.R': mathutils.Euler((0, 0, 0)),
               'upperLeg.L': mathutils.Euler((pi, -pi/2, 0)),
               'lowerLeg.L': mathutils.Euler((0, 0, 0)),
               'foot.L': mathutils.Euler((0, 0, -pi/2)),
               'upperLeg.R': mathutils.Euler((pi, -pi/2, 0)),
               'lowerLeg.R': mathutils.Euler((0, 0, 0)),
               'foot.R': mathutils.Euler((0, 0, -pi/2))
               }

# partsList for limb part iteration 
partsList = ['root', 'head', 'upperArm.L', 'lowerArm.L', 'palm.L', 'upperArm.R', 'lowerArm.R', 'palm.R',
             'upperLeg.L', 'lowerLeg.L', 'foot.L', 'upperLeg.R', 'lowerLeg.R', 'foot.R']


def SetPose(poseBone, eulerStd, tarEuler):
    """ set the poseBone to the local orientation tarEuler
    eulerStd is euler rotation relative to parent coordinates
    tarEuler is the euler angle description (45,0,0) to rotate along x axis 45 degrees
    poseBone the bone needed to be rotated  
    """

    # check mode 
    if 'POSE' != bpy.context.active_object.mode:
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.posemode_toggle()

    tarEulerList = list(tarEuler)   # test the list setting

    # check the bone name if foot update the rotation angle
    if not -1 == poseBone.name.find('foot.L'):
        tarEulerList[2] += offsetFtL
    elif not -1 == poseBone.name.find('foot.R'):
        tarEulerList[2] += offsetFtR
    else:
        pass

    headTransl = poseBone.head
    R_tar = mathutils.Euler(DegToRad(tarEulerList)).to_matrix().to_4x4()
    R_transl = mathutils.Matrix.Translation(headTransl)

    # get parent rotation 
    if poseBone.parent:
        loc, rot, sca = poseBone.parent.matrix.decompose()
        R_prt = rot.to_matrix().to_4x4() # get rid of translation
    else:
        R_prt = mathutils.Matrix().Identity(4)

    R_std = eulerStd.to_matrix().to_4x4()
    R_tarLoc = R_transl * R_prt * R_std * R_tar
    poseBone.matrix = R_tarLoc

    return R_tarLoc
    

if __name__ == '__main__':

    jointR_file = 'jointsR_tar_02_01_Ra.mat'
    matContents = sio.loadmat(os.path.join('matFiles', jointR_file))
    jointsR_tar = matContents['jointsR_tar']

    numFrames = jointsR_tar.shape[3]    # last dimension 
    ind = random.sample(range(numFrames), 1)
    print(ind)

    for idFrame in ind:

        print('processing frame ', idFrame)
        R_tar = jointsR_tar[:, :, :, idFrame]  # 3x3x14

        for i in range(14):
            partNm = partsList[i]
            tarEuler = mathutils.Matrix(R_tar[:,:,i]).to_euler()    # rad need to be degrees
            tarEulerDeg = []

            for j in range(3):
                tarEulerDeg.append(degrees(tarEuler[j]))

            # get bone
            poseBone = bpy.context.object.pose.bones[partNm]

            # get eulerStd
            eulerStd = eulerStdDic.get(partNm)
            R_tarLoc = SetPose(poseBone, eulerStd, tarEulerDeg)
