
"""
handles stage canvas example in Maya gui

author: minu jeong
"""

import math
import random

from PySide import QtGui
from PySide import QtCore


# static class
class FrameUpdater(object):
    """ Calls callback {N} times/sec """

    # static
    FRAME_RATE = 60.
    callbacks = []
    timers = []

    # freeze time for debugging
    timeline = -1

    @staticmethod
    def reset():
        for timer in FrameUpdater.timers:
            timer.stop()

        FrameUpdater.timers = []

    @staticmethod
    def update():
        FrameUpdater.timeline -= 1
        if FrameUpdater.timeline == 0:
            FrameUpdater.stop_all()
            return

        try:
            for callback in FrameUpdater.callbacks:
                callback()
        except Exception as e:
            FrameUpdater.stop_all()
            raise e

    @staticmethod
    def stop_all():
        for timer in FrameUpdater.timers:
            timer.stop()

    @staticmethod
    def resume_all(timeline=-1):
        FrameUpdater.timeline = timeline
        for timer in FrameUpdater.timers:
            timer.start()

    @staticmethod
    def toggle():
        for timer in FrameUpdater.timers:
            if timer.isActive():
                timer.stop()

            else:
                timer.start()

    @staticmethod
    def add_update_listener(callback):
        FrameUpdater.callbacks.append(callback)

        if not FrameUpdater.timers:
            timer = QtCore.QTimer()
            timer.timeout.connect(FrameUpdater.update)
            timer.setInterval(1000. / FrameUpdater.FRAME_RATE)
            timer.start()

            FrameUpdater.timers.append(timer)


class RigidBody(object):
    """ Something with simple physical movement """

    # static
    _rigid_bodies = []
    _wrap_rect = None

    # public
    gravity = 0.98 * .45
    bouncy = 0.7
    floor_friction = 0.99
    collide_popout_exp = 0.5

    _x = 0.
    _y = 0.

    vx = 0.
    vy = 0.

    collision_radius = 0.

    is_active = False

    @staticmethod
    def reset(wrap_rect):
        RigidBody._rigid_bodies = []
        RigidBody._wrap_rect = wrap_rect

    def enable_rigidbody(self):
        RigidBody._rigid_bodies.append(self)
        self.is_active = True

    def disable_rigidbody(self):
        RigidBody._rigid_bodies.remove(self)
        self.is_active = False

    def rigidbody_update(self, progress=1.):
        if not self.is_active:
            return

        # wrap to stage
        self._wrap_test()

        # proceed
        self._x += self.vx * progress
        self._y += self.vy * progress

        # check collisions
        self._hit_test()

        # apply gravity
        self.vy += self.gravity * progress

    def _wrap_test(self):
        if self._y + self.vy > RigidBody._wrap_rect.bottom() - self.collision_radius:
            self.vy *= - self.bouncy
            self.vy *= self.floor_friction
            self.vx *= self.floor_friction
            self._y = RigidBody._wrap_rect.bottom() - self.collision_radius
        elif self._y + self.vy < RigidBody._wrap_rect.top() + self.collision_radius:
            self.vy *= - self.bouncy
            self._y = RigidBody._wrap_rect.top() + self.collision_radius

        if self._x + self.vx < RigidBody._wrap_rect.left() + self.collision_radius:
            self.vx *= - self.bouncy
            self._x = RigidBody._wrap_rect.left() + self.collision_radius
        elif self._x + self.vx > RigidBody._wrap_rect.right() - self.collision_radius:
            self.vx *= - self.bouncy
            self._x = RigidBody._wrap_rect.right() - self.collision_radius

    def _hit_test(self):
        for other in RigidBody._rigid_bodies:
            if self == other:
                continue

            dx = self.x() - other.x()
            dy = self.y() - other.y()
            target_d = self.collision_radius + other.collision_radius

            if (dx * dx + dy * dy) < (target_d * target_d):
                angle = math.atan2(dy, dx)

                self._x = other.x() + math.cos(angle) * target_d
                self._y = other.y() + math.sin(angle) * target_d

                self.vx += math.cos(angle) * self.collide_popout_exp
                self.vy += math.sin(angle) * self.collide_popout_exp

    def push(self, acc_x, acc_y):
        self.vx += acc_x
        self.vy += acc_y


class RenderedEntity(QtGui.QGraphicsItem):
    """ Something rendered """

    # static
    _enterframe_callbacks = []

    def __init__(self, init_x=0, init_y=0):
        super(RenderedEntity, self).__init__()

        self._x = init_x
        self._y = init_y

        self.start()

    def start(self):
        """ override and initialize """

        pass

    def boundingRect(self):
        """
        pure virtual method for QGraphicsItem.
        Do not delete this.
        """

        return QtCore.QRectF(0, 0, 0, 0)

    def _on_enter_frame(self):
        """
        override this to implement enterframe event handler.
        """

        pass


class Ball(RenderedEntity, RigidBody):
    """
    A ball class for debugging
    """

    # public
    radius = None
    brush = None

    def __init__(self, init_x=10, init_y=10, radius=20):
        super(Ball, self).__init__(init_x, init_y)

        self.radius = radius
        self.collision_radius = self.radius
        self.enable_rigidbody()

        self.setAcceptedMouseButtons(
            QtCore.Qt.MouseButton.LeftButton |
            QtCore.Qt.MouseButton.RightButton)

    def paint(self, painter, option, widget):
        """ qt override """

        # draw circle
        painter.setPen(None)
        painter.setBrush(self.brush)
        painter.drawEllipse(
            - self.radius, - self.radius,
            self.radius * 2, self.radius * 2)

    def start(self):
        """ late init """

        self.randomize_brush()
        FrameUpdater.add_update_listener(self._on_enter_frame)

    def randomize_brush(self):
        r = int(random.random() * 255)
        g = int(random.random() * 255)
        b = int(random.random() * 255)
        self.brush = QtGui.QBrush(QtGui.QColor(r, g, b))
        self.update()

    def _on_enter_frame(self):
        self.setPos(self._x, self._y)
        self.rigidbody_update()

    def boundingRect(self):
        return QtCore.QRectF(
            - self.radius, - self.radius,
            self.radius * 2, self.radius * 2)

    def mousePressEvent(self, e):
        """ qt event override """

        pass

    def mouseReleaseEvent(self, e):
        """ qt event override """

        self.randomize_brush()


class Stage(QtGui.QGraphicsScene):
    """ graphics item container """

    WIDTH = 700
    HEIGHT = 700

    scene_rect = None

    _pressed_keys = set()

    frame_updater = None

    balls = []

    def __init__(self):
        super(Stage, self).__init__()

    def start(self):
        self.scene_rect = QtCore.QRectF(0, 0, Stage.WIDTH, Stage.HEIGHT)
        self.setSceneRect(self.scene_rect)

        RigidBody.reset(self.scene_rect)

        self.spawn_new_ball(10)

        FrameUpdater.reset()
        FrameUpdater.add_update_listener(self._on_enter_frame)

        descriptions = [
            "space: continue for 2 seconds",
            "b: Stop all timeline",
            "z: push all balls",
            "x: spawn 5 new balls"
        ]

        for line_idx, t in enumerate(descriptions):
            t_item = self.addText(t)
            t_item.setPos(0, line_idx * 10)

    def spawn_new_ball(self, count=1):
        for _ in range(count):
            init_x = random.random() * self.scene_rect.width()
            init_y = random.random() * self.scene_rect.height()
            radius = random.random() * 5 + 5

            acc_x = random.random() * 100 - 50
            acc_y = random.random() * 100 - 50

            ball = Ball(init_x, init_y, radius)
            ball.push(acc_x, acc_y)
            self.balls.append(ball)
            self.addItem(ball)

    def _on_enter_frame(self):
        self.update()
        self.parse_pressing_keys()

    def parse_pressing_keys(self):
        """ only parsed while time is flowing """

        pass

    def keyPressEvent(self, e):
        self._pressed_keys.add(e.key())

    def keyReleaseEvent(self, e):
        if e.key() in self._pressed_keys:
            self._pressed_keys.remove(e.key())

        def toggle_timeflow():
            FrameUpdater.toggle()

        def expand_timeline(length):
            FrameUpdater.resume_all(length)

        # on release 'space'
        if e.key() == 32:
            toggle_timeflow()

        # on release 'b'
        elif e.key() == 66:
            FrameUpdater.stop_all()

        # on release 'z'
        elif e.key() == 90:
            for ball in self.balls:
                acc_x = random.random() * 100 - 50
                acc_y = random.random() * 100 - 50
                ball.push(acc_x, acc_y)
            expand_timeline(120)

        # on release 'x'
        elif e.key() == 88:
            self.spawn_new_ball(5)

        # read another keys
        else:
            print(e.key())
