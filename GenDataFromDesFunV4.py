# test script for joint control 
"""
read in the low dimension descriptor for object rendering, 
It includes the pose descriptor and camera descriptor 
iterate the whole descriptor files, render image and save the mat files. 
history:  1. memory leak issue, but works under limited images, last time is 8923 images.
2. add in auto save prevention mechanism. Exception handle such as the none descriptor issue
modify image index from 1 (ind+1) so the autosave id match image exactly
3. modify the bg under S drive. Resolution set to 512 with 100% resolution instead of 1080 with 50%.
4. write into function format,
5. ignore extension of png, see what we get
"""

import bpy
import mathutils
import bpy_extras
from math import *
import pdb
import numpy as np
import os
import pickle
import sys
import scipy.io as sio
from utilsGenPose import *

# to current dir
os.chdir(bpy.path.abspath('//'))
wkPath = bpy.path.abspath('//')
if wkPath not in sys.path:		# add current to system  path
    sys.path.append(wkPath)


# save current annotation joints_gt without number
def GenDataset(setNm, avRho,dsFd, ifLb=True, ifRd=True, ifAR =1):
    # generate SYN dataset.  Can continue from last position. All is based on joints_gt 2d labeling
    # input: avRho, average distance of the camera
    # pathData, where the SYN dataset locates, put data there then
    # ifLb, if label the dataset, both 2d and 3d
    # ifRd, if render image out
    # ifAR, if this code is used on AR computer
    # initial settings

    setPath = os.path.join(dsFd, setNm)
    shfZ_arm = 0.2 	# shift z bias

    # get descriptor
    if not os.path.isfile(os.path.join(setPath,'conParFrm.pkl')):
        print("conParFrm descriptor not found")
        quit()

    file2 = open(os.path.join(setPath,'conParFrm.pkl'),'rb')
    conParFrm = pickle.load(file2)
    file2.close()

    # choose the Frs you want to generate
    numFrs = conParFrm.shape[0]
    print('Total {} data images to be rendered'.format(numFrs))

    # set autosave step
    autoStp = 50		# auto save steps

    if numFrs>conParFrm.shape[0]:
        print('data size out of the descriptor')

    # get objects handle
    camNm = 'Camera'
    scene = bpy.data.scenes['Scene']
    obj_camera = bpy.data.objects[camNm]
    obj_other = bpy.data.objects["Armature"]
    w = bpy.data.worlds['World']
    cam = obj_camera   # the camera is named Camera
    arm_ob = bpy.data.objects['Armature']
    scene.camera = cam 		# set cam
    scene.render.image_settings.file_format = 'PNG'
    obj_other.animation_data_clear()	# get rid of animation

    # bg settings
    flgWdTexture = 0
    shfRg = [-0.3,0.3]    # the shift range to render the bg image
    scalRg = [1,1]
    flgVerbose = 0

    absPath = '/gss_gpfs_scratch/ACLab/LSUN_large'
    nmLst = [os.path.join(path, file) for path, subdirs, files in os.walk(absPath) for file in files if
             file.endswith(".jpg")]
    print(absPath)
    print(nmLst[:5])
    print('length of nmLst is', len(nmLst))

    # annotation setting
    # fileName
    annoFileNm =os.path.join(setPath,'annotations.pkl')

    limbNamesLSB = ('foot.R', 'lowerLeg.R', 'upperLeg.R', 'upperLeg.L', 'lowerLeg.L', 'foot.L', 'palm.R',
                    'lowerArm.R', 'upperArm.R', 'upperArm.L', 'lowerArm.L', 'palm.L', 'head')

    # check if there is joint_gt#.pkl ( save later, so if joint_gt, must there is annotations.pkl)
    nmLst_joint= [file for file in os.listdir(setPath) if 'joints_gt' in file and len(file)>13 ]  # only annotations, intermediate version

    # if there is ,check the last #  %06d
    joints = np.zeros((14,3,numFrs))   # clean for new image 0 for visible, we set all to zero here
    joints3d = np.zeros((14,3,numFrs))

    # this is for the LEEDS mat raw data
    if not nmLst_joint:
        indSt = 0
        # label data initialization
        annotations = {}  # should be read in, for our version data format data
        annotations['setNm'] = setNm

    else:
        print('previous label exist', nmLst_joint)
        print('read in the previous label')
        indices = [int(name[-10:-4]) for name in nmLst_joint]
        indSt = max(indices)	# largest saved version

        # read in saved annotations and joints
        # largest index joint file name and annotation name the prefix + indSt
        afile = open(os.path.join(setPath,'annotations{:06d}.pkl'.format(indSt)),'rb')
        annotations = pickle.load(afile)
        afile.close()

        # load in joints_gt.mat file
        mat_contents = sio.loadmat(os.path.join(setPath,'joints_gt{:06d}.mat'.format(indSt)))
        joints_gtT = mat_contents['joints_gt']	# 3x14xN

        # change order to get joints
        jointsT = np.swapaxes(joints_gtT,0,1)	# record joints position in blender, use the 14x3xN eahc row a coordinate

        mat_contents = sio.loadmat((os.path.join(setPath,'joint_gt3d{:06d}.mat'.format(indSt))))	# 2d 3d should be labeled together, or continue mechanism is pointless
        joints3dT = np.swapaxes(mat_contents['joints_gt3d'])

        if jointsT.shape[2] < numFrs:	 # dynamic array size to cooperate with numFrs
            joints[:, :, :jointsT.shape[2]] = jointsT.copy()
            joints3d[:, :, :joints3dT.shape[2]] = joints3dT.copy()
        else:
            joints = jointsT[:, :, :numFrs]
            joints3d = joints3dT[:, :, :numFrs]

        del jointsT, joints_gtT, joints3dT  # clean the memory

    # set render resolution
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100 # 50 percent

    # If you want pixel coords
    render_scale = scene.render.resolution_percentage / 100
    render_size = (
        int(scene.render.resolution_x * render_scale),
        int(scene.render.resolution_y * render_scale),
    )

    # my parts list
    partsList = ['root', 'head', 'upperArm.L', 'lowerArm.L', 'palm.L', 'upperArm.R', 'lowerArm.R', 'palm.R',
                 'upperLeg.L', 'lowerLeg.L', 'foot.L', 'upperLeg.R', 'lowerLeg.R', 'foot.R']

    # global, define the joint list, must set in predefined sequence
    # as we need to give in the target rotations,
    eulerStdDic = {
        'head':mathutils.Euler((0, 0, 0)),
        'upperArm.L':mathutils.Euler((pi, pi/2, 0)),
        'lowerArm.L':mathutils.Euler((0, 0, 0)),
        'palm.L':mathutils.Euler((0, 0, 0)),
        'upperArm.R':mathutils.Euler((pi, pi/2, 0)),
        'lowerArm.R':mathutils.Euler((0, 0, 0)),
        'palm.R':mathutils.Euler((0, 0, 0)),
        'upperLeg.L':mathutils.Euler((pi, -pi/2, 0)),
        'lowerLeg.L':mathutils.Euler((0, 0, 0)),
        'foot.L':mathutils.Euler((0, 0, -pi/2)),
        'upperLeg.R':mathutils.Euler((pi, -pi/2, 0)),
        'lowerLeg.R':mathutils.Euler((0, 0, 0)),
        'foot.R':mathutils.Euler((0, 0, -pi/2)),
        'root': mathutils.Euler((pi/2, 0, 0))
    }

    # get FOV and calculate the shift along Z
    h = obj_camera.data.sensor_width  # the height of the camera
    f = obj_camera.data.lens  # focal length in mm
    fov = 2 *  atan(h/2/f)

    # get phi
    idxs_bar = findOccurences(setNm, '_')
    phi_cen = np.deg2rad(int(setNm[idxs_bar[-1]+2:]))	 # rad

    # random pick up the ind
    # distance is random , I set it  to 2.5 the mean of 2 to 3
    horz_dist = avRho * cos(phi_cen)
    up = horz_dist * tan(phi_cen) - horz_dist * tan(phi_cen - fov/2)
    down = horz_dist * tan(phi_cen + fov/2)- horz_dist * tan(phi_cen)
    sftZ = (down- up)/3
    print('shift Z is',sftZ )

    # for sampleInd in range(indSt,conParFrm.shape[0]):
    for idxSamp in range(indSt,numFrs):		# only 2 image test
        eulers = conParFrm[idxSamp,:14]
        rho, theta, phi = conParFrm[idxSamp,14]   # camera parameters
        rotZ = conParFrm[idxSamp,15,0]    # rotation parameters

        # set the pose
        for i in range(14):
            partNm = partsList[i]
            tarEulerDeg = mathutils.Euler(eulers[i])
            poseBone = bpy.data.objects['Armature'].pose.bones[partNm]
            # get eulerStd
            eulerStd = eulerStdDic.get(partNm)

            # make sure in pose mode
            if not scene.objects['Armature']:	# if not in scene
                scene.objects.link(arm_ob)	# link and set active, already in
            bpy.context.scene.objects.active = arm_ob
            arm_ob.hide = False
            bpy.ops.object.mode_set(mode='POSE', toggle=False)

            # set pose
            R_tarLoc  = SetPose(poseBone,eulerStd,tarEulerDeg,'YXZ')  # bone, rad, angles

        # set camera
        # this is setting from world, armature not move, except we focus on the root bone
        locCar = (rho*sin(phi)*cos(theta),rho*sin(phi)*sin(theta),rho*cos(phi))

        # Test
        obj_camera.location = locCar
        aimCen = obj_other.matrix_world.to_translation() + mathutils.Vector((0,0,shfZ_arm))	# add bias to it
        look_at(obj_camera, aimCen,rotZ)

        # adjust camera height
        if not 0 == phi_cen:
            obj_camera.location[2] = sftZ + obj_camera.location[2]

        for tex in bpy.data.textures:
            if 'wdTexture' == tex.name:
                print('test texture existis')
                flgWdTexture = 1
                texOn = tex

        if not flgWdTexture:
            texOn = bpy.ops.texture.new('wdTexture',type = 'IMAGE')  # same name, can over write?
            bpy.ops.textures[-1].name = "wdTexture"  # rename the texture name


        fileName = np.random.choice(nmLst)
        if flgVerbose:
            print(fileName)

        # get in new bg
        texOn.image = bpy.data.images.load(fileName)
        w.active_texture = texOn

        w.use_sky_paper = True
        w.texture_slots[0].use_map_horizon = True

        # random the position
        w.texture_slots[0].offset= mathutils.Vector(np.random.uniform(shfRg[0],shfRg[1],3))

        scale = np.random.uniform(scalRg[0],scalRg[1])
        w.texture_slots[0].scale= mathutils.Vector((scale,scale,1)) # x,y same scale

        # change the view mode to render shading
        for area in bpy.context.screen.areas: # iterate through areas in current screen
            if area.type == 'VIEW_3D':
                for space in area.spaces: # iterate through spaces in current VIEW_3D area
                    if space.type == 'VIEW_3D': # check if space is a 3D view
                        space.viewport_shade = 'RENDERED' # set the viewport shading to rendered

        # render images
        imgNm = "image_{:06d}".format(idxSamp + 1)  # ignore the extension name
        if ifRd:
            imgsFd = os.path.join(setPath,'images')

            if not os.path.exists(imgsFd):
                os.makedirs(imgsFd)

            outNm = os.path.join(imgsFd,imgNm)
            print('save name is ', outNm)
            bpy.data.scenes['Scene'].render.filepath = outNm
            bpy.ops.render.render( write_still=True )

        # update the coordinate result
        for idx,limbNm in enumerate(limbNamesLSB):  # loop limbs
            poseBone = bpy.data.objects['Armature'].pose.bones[limbNm]
            co = arm_ob.matrix_world * poseBone.head	# coord in world
            co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, co) # co vector, assign one by one
            M_w2c = cam.matrix_world.inverted() # c to w
            co_cam = M_w2c * co
            joints[idx,0,idxSamp]= co_2d.x * render_size[0]
            joints[idx,1,idxSamp]=(1- co_2d.y) * render_size[1]+1
            # 3d coordinates
            joints3d[idx,0, idxSamp] =co_cam.x
            joints3d[idx, 1, idxSamp] = co_cam.y
            joints3d[idx, 2, idxSamp] = co_cam.z

        # for the additional head position which use the tail information
        poseBone = bpy.data.objects['Armature'].pose.bones['head']
        co = arm_ob.matrix_world * poseBone.tail
        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, co) # co vector, assign one by one
        M_w2c = cam.matrix_world.inverted()  # c to w
        co_cam = M_w2c * co  # co_3d in cam		# update for head

        joints[13,0,idxSamp]= co_2d.x * render_size[0]
        joints[13,1,idxSamp]= (1-co_2d.y) * render_size[1]+1 # matlab format top left origin
        annotations[imgNm] = joints[:,:,idxSamp]   # only gives a name, because the path is not guaranteed
        joints3d[13, 0, idxSamp] = co_cam.x
        joints3d[13, 1, idxSamp] = co_cam.y
        joints3d[13, 2, idxSamp] = co_cam.z

        # auto save the temporary result
        # every autoStp image
        # dir all pkl and joints list.
        # save current annotation with # ind+1 ,joints_gt  to annotation_curr#.pkl and joints.
        # means this ind has been saved, start from next ind.
        # delete all the listed one

        if (idxSamp+1) % autoStp == 0: # list old first, then gen new one
            oldAutoNms = [nm for nm in os.listdir(setPath) if 'joints_gt' in nm or 'annotations' in nm]
            matNmT = os.path.join(setPath,'joints_gt{:06d}.mat'.format(idxSamp+1))
            joints_gt = np.swapaxes(joints,0,1)
            sio.savemat(matNmT,{'joints_gt':joints_gt})
            annoNmT = os.path.join(setPath,'annotations{:06d}.pkl'.format(idxSamp+1))
            fileHdl = open(annoNmT,'wb')
            pickle.dump(annotations,fileHdl,protocol =2)
            fileHdl.close()
            matNmT = os.path.join(setPath, 'joints_gt3d{:06d}.mat'.format(idxSamp+1))
            joints_gt3d = np.swapaxes(joints3d,0,1)
            sio.savemat(matNmT,{'joints_gt3d':joints_gt3d})

            for nm in oldAutoNms:
                os.remove(os.path.join(setPath,nm))

    # show the joints result
    joints_gt =  np.swapaxes(joints,0,1)
    joints_gt3d = np.swapaxes(joints3d,0,1)
    if flgVerbose:
        print('joints coordinates gotten')
        print('original')
        print(joints[:,:,0])
        print(joints[:,:,1])
        print('after swap')
        print(joints_gt[:,:,0])
        print(joints_gt[:,:,1])
        print('annotation is')
        print(annotations)		# seems all right

    # save data to pkl and mat
    if ifLb:
        print('All data generated, save data to files')
        matNm = os.path.join(setPath,'joints_gt.mat')
        sio.savemat(matNm,{'joints_gt':joints_gt})

        fileHdl = open(annoFileNm,'wb')	# open as bype
        pickle.dump(annotations,fileHdl,protocol = 2)
        fileHdl.close()
        matNm = os.path.join(setPath, 'joints_gt3d.mat')

        print('saving 3d infor to {}'.format(matNm))

        sio.savemat(matNm,{'joints_gt3d':joints_gt3d})
