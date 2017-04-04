
import math

from maya import cmds


# initialize scene
everything = cmds.ls()
undeletables = cmds.ls(readOnly=True)
for i in undeletables:
    if i in everything:
        everything.remove(i)
cmds.delete(everything)
cmds.currentTime(1, edit=True)
cube = cmds.polyCube()[0]
cmds.setAttr(cube + ".scale", 3., 3., 3.)

# initialize constants
MAX_TIME = 550
jump_width = 4.65
punch_scale_amount = .665
elevation = 17
y_pop_decay = .998
radius_decay = .998
looping_count = 2.5

# initialize variables
y_pop = 11.
radius = 12.
angle = 0.
prev_y = 0.

cmds.playbackOptions(loop="continuous")
cmds.playbackOptions(minTime=1, maxTime=MAX_TIME)

# animate
for t in range(MAX_TIME):
    cmds.currentTime(t + 1, edit=True, update=True)

    progress = float(t) / MAX_TIME

    angle = (progress) * (math.pi * 2.) * looping_count

    x = math.cos(angle) * radius
    y = abs(math.sin(t / jump_width)) * (y_pop) + progress * elevation
    z = math.sin(angle) * radius

    cmds.setAttr(cube + ".translate", x, y, z)
    cmds.setKeyframe(cube + ".translateX")
    cmds.setKeyframe(cube + ".translateY")
    cmds.setKeyframe(cube + ".translateZ")

    cmds.setAttr(cube + ".rotateY", - angle * 180 / math.pi)
    cmds.setKeyframe(cube + ".rotateY")

    delta_y = (y - prev_y) / 3.
    cmds.setAttr(cube + ".scaleY", 3. + (delta_y * punch_scale_amount) / 2.)
    cmds.setKeyframe(cube + ".scaleY")

    cmds.setAttr(cube + ".scaleX", 3. - (delta_y * punch_scale_amount))
    cmds.setAttr(cube + ".scaleZ", 3. - (delta_y * punch_scale_amount))
    cmds.setKeyframe(cube + ".scaleX")
    cmds.setKeyframe(cube + ".scaleZ")

    prev_y = y

    y_pop *= y_pop_decay
    radius *= radius_decay

# debug
cmds.currentTime(1, edit=True)
cmds.play()

cmds.select(clear=True)
