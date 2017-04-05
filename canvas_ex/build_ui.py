
"""
Generate ui elements dynamically.

author: minu jeong
"""

from PySide import QtGui
from PySide import QtCore

from afb_stage import canvas
reload(canvas)


def build_stage():
    stage_view = QtGui.QGraphicsView()
    stage_view.setRenderHints(
        QtGui.QPainter.Antialiasing |
        QtGui.QPainter.SmoothPixmapTransform)
    stage = canvas.Stage()
    stage.start()

    stage_view.setScene(stage)
    return stage_view


def build_mainwin():

    mainwin = QtGui.QWidget()
    mainwin.setWindowTitle("Canvas")
    mainwin.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    mainlayout = QtGui.QHBoxLayout()

    mainlayout.addWidget(build_stage())

    mainwin.setLayout(mainlayout)
    return mainwin
