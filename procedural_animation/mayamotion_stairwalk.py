
import math

from maya import cmds


# initialize constants
MAX_TIME = 600
jump_width = 4.65
punch_scale_amount = .65
elevation = 17
y_pop_decay = .9993
radius_decay = .9995
looping_count = 2.5
angle_fatigue = .75

# initialize variables
y_pop = 8.
radius = 8.
angle = 0.
prev_x = 0.
prev_y = 0.
prev_z = 0.

# initialize scene
everything = cmds.ls()
undeletables = cmds.ls(readOnly=True)
for i in undeletables:
    if i in everything:
        everything.remove(i)
cmds.delete(everything)
cmds.currentTime(1, edit=True)
target = cmds.polySphere()[0]
cmds.setAttr(target + ".scale", 3., 3., 3.)
cmds.playbackOptions(loop="once")
cmds.playbackOptions(minTime=1, maxTime=MAX_TIME)

# cache useful numbers
vtx_count = cmds.polyEvaluate(target, vertex=True)

# animate
for t in range(MAX_TIME):
    cmds.currentTime(t + 1)

    progress = float(t) / MAX_TIME

    angle = (math.pow(progress, angle_fatigue)) * (math.pi * 2.) * looping_count

    x = math.cos(angle) * radius
    y = abs(math.sin(t / jump_width)) * (y_pop) + progress * elevation
    z = math.sin(angle) * radius

    cmds.setAttr(target + ".translate", x, y, z)
    cmds.setKeyframe(target + ".translateX")
    cmds.setKeyframe(target + ".translateY")
    cmds.setKeyframe(target + ".translateZ")

    cmds.setAttr(target + ".rotateY", - angle * 180 / math.pi)
    cmds.setKeyframe(target + ".rotateY")

    delta_x = (x - prev_x) / 3.
    delta_y = (y - prev_y) / 3.
    delta_z = (z - prev_z) / 3.

    cmds.setAttr(target + ".scaleY", 3. + (delta_y * punch_scale_amount) * 2.)
    cmds.setKeyframe(target + ".scaleY")

    cmds.setAttr(target + ".scaleX", 3. - (delta_y * punch_scale_amount))
    cmds.setKeyframe(target + ".scaleX")

    cmds.setAttr(target + ".scaleZ", 3. - (delta_y * punch_scale_amount))
    cmds.setKeyframe(target + ".scaleZ")

    prev_x = x
    prev_y = y
    prev_z = z

    y_pop *= y_pop_decay
    radius *= radius_decay

    for i in range(vtx_count):
        vtx_id = target + ".vtx[{}]".format(i)
        xyz = cmds.xform(vtx_id, translation=True, worldSpace=True, query=True)
        cmds.polyColorPerVertex(vtx_id, rgb=xyz)
    break

# debug
cmds.currentTime(1, edit=True)
cmds.play()

# clear selection
cmds.select(clear=True)
