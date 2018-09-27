"""
This module includes the function needed for blender operation for data generation.
Shuangjun Liu
"""
import bpy
import mathutils
import bpy_extras
from math import *
import numpy as np
import sys

# offset of two feet 
offsetFtL = degrees(bpy.data.objects['Armature'].data.bones['foot.L'].matrix.to_euler().z + pi/2)
offsetFtR = degrees(bpy.data.objects['Armature'].data.bones['foot.R'].matrix.to_euler().z + pi/2)


def DegToRad(degrees):  # not used 
    rads = list(radians(degree) for degree in degrees)
    return rads


def look_at(obj_camera, point, rotZ=0):
    """
    set the camera to point to the point location 
    input: obj_camera, camera object 
    point, object location vector 
    rotZ, the rotation in rad 
    history, 17.10.26 add rotZ to control the camera rotation, Shuangjun Liu, 
    """

    # loc_camera = obj_camera.matrix_world.to_translation()
    rotZ = mathutils.Euler((0,0,rotZ))
    loc_camera = obj_camera.location

    direction = point - loc_camera  # from cam point to point
    rot_quat = direction.to_track_quat('-Z', 'Y')

    rot_euler = rot_quat.to_euler()
    rotZ.rotate(rot_euler)
    obj_camera.rotation_euler = rotZ


def SetPose(poseBone, eulerStd, tarEuler, axisOrd):
    """ set the poseBone to the local orientation tarEuler
    eulerStd is euler rotation (rads) relative to parent coordiates
    tarEuler is the euler angle (degrees) description (45,0,0) to rotate along x axis 45 degrees
    poseBone the bone needed to be rotated  
    axisOrd is a string to specify the rotation order eg, 'XYZ', 'ZXY'. 
    history: 17.10.26 speicfy the euler order  by Shuangjun
    """

    tarEulerList = list(tarEuler)   # test the list setting

    # check the bone name if foot update the rotation angle
    if not -1 == poseBone.name.find('foot.L'):
        tarEulerList[2] += offsetFtL
    elif not -1 == poseBone.name.find('foot.R'):
        tarEulerList[2] += offsetFtR
    else:
        pass

    headTransl = poseBone.head
    R_tar = mathutils.Euler(DegToRad(tarEulerList),axisOrd).to_matrix().to_4x4()
    R_transl = mathutils.Matrix.Translation(headTransl)

    # get parent rotation 
    if poseBone.parent:
        loc, rot, sca = poseBone.parent.matrix.decompose()
        R_prt = rot.to_matrix().to_4x4() # get rid of translation
    else:
        R_prt= mathutils.Matrix().Identity(4)

    R_std = eulerStd.to_matrix().to_4x4()
    R_tarLoc = R_transl * R_prt * R_std * R_tar

    poseBone.matrix = R_tarLoc

    return R_tarLoc


def add_background(filepath):
    img = bpy.data.images.load(filepath)
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space_data = area.spaces.active
            bg = space_data.background_images.new()
            bg.image = img
            space_data.show_background_images = True
            break


def findOccurences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]





