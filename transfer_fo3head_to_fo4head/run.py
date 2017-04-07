# -*- coding: utf-8 -*-

import os
import json

from maya import cmds

from PySide import QtGui
from PySide import QtCore


class FO3_SourceHandler(QtGui.QGroupBox):

    imported_nodes = None
    gc_assetid_le = None
    target_object_name_l = None

    _is_hidden = False

    @property
    def gc_assetid(self):
        if not self.gc_assetid_le:
            return None

        return self.gc_assetid_le.text()

    @gc_assetid.setter
    def gc_assetid(self, value):
        if not self.gc_assetid_le:
            return None

        self.gc_assetid_le.setText(value)

    @property
    def source_name(self):
        if not self.target_object_name_l:
            return None

        return self.target_object_name_l.text()

    @source_name.setter
    def source_name(self, value):
        if not self.target_object_name_l:
            return

        self.target_object_name_l.setText(value)

    def start(self):

        self.setTitle(u"FO3 소스")

        self.mainlayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainlayout)

        desc_l = QtGui.QLabel()
        desc_l.setText(
            u"GC에서 에셋을 가져오거나, \n" +
            u"씬에서 선택된 오브젝트를 타겟으로 설정합니다.")
        self.mainlayout.addWidget(desc_l)

        self.mainlayout.addSpacing(15)

        # GC asset Loader
        gc_load_row = QtGui.QWidget()
        gc_load_row_layout = QtGui.QHBoxLayout()
        gc_load_row_layout.setContentsMargins(0, 0, 0, 0)
        gc_load_row.setLayout(gc_load_row_layout)
        self.mainlayout.addWidget(gc_load_row)

        gc_l = QtGui.QLabel()
        gc_l.setText(u"pid")
        gc_load_row_layout.addWidget(gc_l)

        self.gc_assetid_le = QtGui.QLineEdit("51")
        gc_load_row_layout.addWidget(self.gc_assetid_le)

        self.gc_load_btn = QtGui.QPushButton()
        self.gc_load_btn.setText(u"가져오기")
        self.gc_load_btn.clicked.connect(self.load_gc_asset)
        gc_load_row_layout.addWidget(self.gc_load_btn)

        self.gc_unload_btn = QtGui.QPushButton()
        self.gc_unload_btn.setText(u"지우기")
        self.gc_unload_btn.clicked.connect(self.unload_gc_asset)
        gc_load_row_layout.addWidget(self.gc_unload_btn)

        # Selected scene entity capturer
        sel_obj_row = QtGui.QWidget()
        self.mainlayout.addWidget(sel_obj_row)

        sel_obj_row_layout = QtGui.QHBoxLayout()
        sel_obj_row_layout.setContentsMargins(0, 0, 0, 0)
        sel_obj_row.setLayout(sel_obj_row_layout)

        sel_l = QtGui.QLabel()
        sel_l.setText(u"선택")
        sel_obj_row_layout.addWidget(sel_l)

        self.target_object_name_l = QtGui.QLabel()
        sel_obj_row_layout.addWidget(self.target_object_name_l)

        self.capture_selected_btn = QtGui.QPushButton()
        self.capture_selected_btn.setText(u"업데이트")
        self.capture_selected_btn.clicked.connect(self.update_selected)
        sel_obj_row_layout.addWidget(self.capture_selected_btn)

        self.select_something_btn = QtGui.QPushButton()
        self.select_something_btn.setText(u"아무거나 선택")
        self.select_something_btn.clicked.connect(self.select_something)
        sel_obj_row_layout.addWidget(self.select_something_btn)

        self.toggle_hide_source_btn = QtGui.QPushButton()
        self.toggle_hide_source_btn.setText(u"보이기/숨기기")
        self.toggle_hide_source_btn.clicked.connect(self.toggle_hide_source)
        self.mainlayout.addWidget(self.toggle_hide_source_btn)

        # update current selection as default
        self.update_selected()

    def load_gc_asset(self, e=False):
        if not self.gc_assetid:
            print(u"에셋 아이디를 입력하세요.")
            return

        self.unload_gc_asset()

        pid = str(self.gc_assetid)
        gc_root_path = "Y:/GC/FIFA17_Mobile_FO3/character/player"

        found_asset_dir = None
        for category in os.listdir(gc_root_path):
            if "common" in category:
                continue

            concat_path = "{}/{}".format(gc_root_path, category)
            for dirname in os.listdir(concat_path):
                if dirname.split("_")[-1] == pid:
                    found_asset_dir = "{}/{}".format(concat_path, dirname)
                    break

            if found_asset_dir:
                break

        if not found_asset_dir:
            print(u"pid {}를 찾지 못했습니다.".format(pid))
            return

        result_gc_asset_path = "{}/model/scene/head_{}_0.ma".format(found_asset_dir, pid)
        self.imported_nodes = cmds.file(result_gc_asset_path, i=True, rnn=True)
        for node in self.imported_nodes:
            if "head" in node:
                cmds.select(node)
                self.update_selected()
                break

    def unload_gc_asset(self, e=False):
        if self.imported_nodes:
            cmds.lockNode(self.imported_nodes, lock=False)
            cmds.delete(self.imported_nodes)
            self.imported_nodes = None
            self.source_name = None

        cmds.select(cl=True)
        self.update_selected()

    def update_selected(self, e=False):
        selection = cmds.ls(sl=True)
        if not selection:
            if self.source_name:
                cmds.lockNode(self.source_name, lock=False)
                self.source_name = None
            return

        selected_item = selection[0]
        connected_meshes = cmds.listRelatives(selected_item, type="mesh")
        if not connected_meshes:
            print(u"메쉬를 가진 트랜스폼을 선택해야 합니다.")
            if self.source_name:
                cmds.lockNode(self.source_name, lock=False)
            self.source_name = None
            return

        self.source_name = selected_item
        cmds.lockNode(self.source_name, lock=True)

    def select_something(self, e=False):
        everything = cmds.ls(type="transform")
        if not everything:
            print(u"씬에 오브젝트가 없습니다.")
            return

        found_something = False
        for something in everything:
            connected_meshes = cmds.listRelatives(something, type="mesh")
            if connected_meshes:
                cmds.select(something)
                found_something = True
                break

        if not found_something:
            print(u"씬에서 메쉬를 가진 오브젝트를 찾지 못했습니다.")
            return

        self.update_selected()

    def toggle_hide_source(self, e=False):
        if not cmds.ls(self.source_name):
            return

        self._is_hidden = not self._is_hidden

        if self._is_hidden:
            cmds.hide(self.source_name)
        else:
            cmds.showHidden(self.source_name)
            cmds.select(self.source_name)

    def ensure_unlock_source(self):
        if self.source_name and cmds.ls(self.source_name):
            cmds.lockNode(self.source_name, lock=False)


class FO4_TemplateHandler(QtGui.QGroupBox):

    imported_nodes = None

    template_object_name = None
    _is_hidden = False

    @property
    def target_name(self):
        return self.template_object_name

    @target_name.setter
    def target_name(self, value):
        self.template_object_name = value

        if self.preview_loaded_l:
            self.preview_loaded_l.setText(value)

    def start(self):

        self.setTitle(u"FO4 타겟")

        self.mainlayout = QtGui.QVBoxLayout()

        self.desc_l = QtGui.QLabel()
        self.desc_l.setText(u"FO4 템플릿 헤드를 가져와서 수정합니다.")
        self.mainlayout.addWidget(self.desc_l)

        self.mainlayout.addSpacing(15)

        # preview loaded template
        preview_loaded_widget = QtGui.QWidget()
        self.mainlayout.addWidget(preview_loaded_widget)

        preview_loaded_layout = QtGui.QHBoxLayout()
        preview_loaded_widget.setLayout(preview_loaded_layout)

        self.preview_loaded_l = QtGui.QLabel()
        preview_loaded_layout.addWidget(self.preview_loaded_l)

        # load/unload buttons
        self.load_unload_widget = QtGui.QWidget()
        self.mainlayout.addWidget(self.load_unload_widget)
        load_unload_layout = QtGui.QHBoxLayout()
        load_unload_layout.setContentsMargins(0, 0, 0, 0)
        self.load_unload_widget.setLayout(load_unload_layout)

        self.load_template_btn = QtGui.QPushButton()
        self.load_template_btn.setText(u"가져오기")
        self.load_template_btn.clicked.connect(self.load_base_template)
        load_unload_layout.addWidget(self.load_template_btn)

        self.delete_loaded_template_btn = QtGui.QPushButton()
        self.delete_loaded_template_btn.setText(u"지우기")
        self.delete_loaded_template_btn.clicked.connect(self.delete_base_template)
        load_unload_layout.addWidget(self.delete_loaded_template_btn)

        # toggle show/hide
        self.toggle_hide_template_btn = QtGui.QPushButton()
        self.toggle_hide_template_btn.setText(u"보이기/숨기기")
        self.toggle_hide_template_btn.clicked.connect(self.toggle_hide_target)
        self.mainlayout.addWidget(self.toggle_hide_template_btn)

        self.setLayout(self.mainlayout)

    def load_base_template(self, e=False):
        current_selection = cmds.ls(sl=True)

        self.delete_base_template()

        template_path = Tool.Instance.fo4_template_path
        self.imported_nodes = cmds.file(template_path, i=True, returnNewNodes=True)
        for node in self.imported_nodes:
            if "template_geo_head" in node and "shape" not in node:
                self.target_name = node
                break

        if not self.target_name:
            print(
                u"씬 또는 템플릿 파일이 손상되었습니다." +
                u"새 씬을 열고 다시 시도해보세요.")
            return

        cmds.lockNode(self.imported_nodes, lock=True)

        cmds.select(current_selection)

    def delete_base_template(self, e=False):
        if not self.target_name:
            return

        cmds.lockNode(self.imported_nodes, lock=False)
        cmds.delete(self.imported_nodes)
        self.target_name = None

    def toggle_hide_target(self, e=False):
        if not self.target_name:
            return

        self._is_hidden = not self._is_hidden
        if self._is_hidden:
            cmds.hide(self.imported_nodes)
        else:
            cmds.showHidden(self.imported_nodes)

    def ensure_unlock_target(self):
        if self.imported_nodes:
            cmds.lockNode(self.imported_nodes, lock=False)


class LerpTool(object):
    """
    leave this class as static
    """

    bottom_vtx_list = \
        [2, 3, 4, 5, 8, 9, 12, 13, 14, 16, 17, 18, 20, 22, 24, 26, 27, 29] + \
        [31, 32, 36, 38, 40, 42, 44, 45, 48, 49, 55, 57, 179, 180, 184, 187] + \
        [190, 193, 194, 195, 197, 198, 199, 200, 201, 203, 209, 210, 215] + \
        [236, 237, 238, 239, 296, 301, 317, 328, 329, 330, 334]

    @staticmethod
    def get_ignore_list():
        return LerpTool.bottom_vtx_list

    @staticmethod
    def get_vtx_pos(object_name, apply_ignore_list=False, with_key=False):
        mesh = cmds.listRelatives(object_name, type="mesh")
        if not mesh:
            return None

        ignore_list = LerpTool.get_ignore_list() if apply_ignore_list else []

        result = [] if not with_key else {}
        mesh = mesh[0]
        vtx_count = cmds.polyEvaluate(object_name, vertex=True)
        for idx in range(vtx_count):
            if int(idx) in ignore_list:
                continue

            vtx_pos = cmds.xform(
                "{}.vtx[{}]".format(object_name, idx),
                ws=False, q=True, t=True, a=True)

            if not with_key:
                result.append(vtx_pos)
            else:
                result[str(idx)] = vtx_pos
        return result

    @staticmethod
    def lerp_pos(pos_1, pos_2, step):
        return [
            pos_1[0] + (pos_2[0] - pos_1[0]) * (1 - step),
            pos_1[1] + (pos_2[1] - pos_1[1]) * (1 - step),
            pos_1[2] + (pos_2[2] - pos_1[2]) * (1 - step)
        ]

    @staticmethod
    def distance_sqr(pos_1, pos_2):
        dx = pos_1[0] - pos_2[0]
        dy = pos_1[1] - pos_2[1]
        dz = pos_1[2] - pos_2[2]
        return dx * dx + dy * dy + dz * dz

    @staticmethod
    def element_calc(pos_1, pos_2, operation):
        dx = operation(pos_1[0], pos_2[0])
        dy = operation(pos_1[1], pos_2[1])
        dz = operation(pos_1[2], pos_2[2])
        return [dx, dy, dz]

    @staticmethod
    def lerp(src, dst, step):
        """
        wrapping for conveniently change algorithms
        """

        # LerpTool._simple_index_based_lerp(src, dst, step)
        # LerpTool._distance_based_lerp(src, dst, step, tolerance=0.001)
        LerpTool._relationship_based_lerp(src, dst, step)

    @staticmethod
    def _simple_index_based_lerp(src, dst, step):
        """
        dst decides src target by simple index
        """

        src_vtx = LerpTool.get_vtx_pos(src)
        dst_vtx = LerpTool.get_vtx_pos(dst, True)

        for idx, src_pos in enumerate(src_vtx):
            dst_pos = dst_vtx[int(idx)]

            # translate dst vtx to src vtx
            cmds.xform(
                "{}.vtx[{}]".format(dst, idx),
                t=LerpTool.lerp_pos(src_pos, dst_pos, step),
                relative=False)

    @staticmethod
    def _distance_based_lerp(src, dst, step, tolerance):
        """
        dst decides src target by most similar local position
        """

        src_vtx = LerpTool.get_vtx_pos(src)
        dst_vtx = LerpTool.get_vtx_pos(dst)

        def get_closest_dst_pos(pos):
            closest_vt = dst_vtx[0]
            closest_d = LerpTool.distance_sqr(pos, closest_vt)
            for idx, dst_vt in enumerate(src_vtx):
                d = LerpTool.distance_sqr(pos, dst_vt)
                if d < closest_d:
                    closest_d = d
                    closest_vt = dst_vt

            return closest_vt, closest_d

        for idx, dst_pos in enumerate(dst_vtx):
            src_pos, sqr_d = get_closest_dst_pos(dst_pos)

            # skip if already close enough
            if sqr_d < tolerance * tolerance:
                continue

            # translate dst vtx to src vtx
            cmds.xform(
                "{}.vtx[{}]".format(dst, idx),
                t=LerpTool.lerp_pos(src_pos, dst_pos, step),
                relative=False)

    @staticmethod
    def _relationship_based_lerp(src, dst, step):
        def read_key_feature_data():
            data_file_path = "{}/mapping_table/key_features.json".format(
                Tool.Instance.package_path)

            parsed_data = None
            with open(data_file_path, 'r') as fp:
                parsed_data = json.loads(fp.read())
            return parsed_data

        # move key_features
        applied_keys = {}
        key_features = read_key_feature_data()
        ignore_list = LerpTool.get_ignore_list()
        for dst_key, src_key in key_features.items():
            if dst_key in ignore_list:
                continue

            dst_pos = cmds.xform(
                "{}.vtx[{}]".format(dst, dst_key),
                ws=False, q=True, t=True, a=True)
            src_pos = cmds.xform(
                "{}.vtx[{}]".format(src, src_key),
                ws=False, q=True, t=True, a=True)

            # translate dst vtx to src vtx
            cmds.xform(
                "{}.vtx[{}]".format(dst, dst_key),
                t=LerpTool.lerp_pos(src_pos, dst_pos, step),
                relative=False)
            applied_keys[dst_key] = dst_pos

        # move others
        dst_vtx = LerpTool.get_vtx_pos(dst, apply_ignore_list=True, with_key=True)
        src_vtx = LerpTool.get_vtx_pos(src, with_key=True)

        # calculate based on relationship with key_feature
        for dst_key, dst_pos in dst_vtx.items():

            # skip key_features, since it's already calculated
            if dst_key in applied_keys.keys():
                continue

            closest_dst_key = None
            closest_src_key = None
            closest_d = None
            for feat_dst_key, feat_src_key in key_features.items():
                calc_feat_src_pos = src_vtx[feat_src_key]
                dist_sqr = LerpTool.distance_sqr(dst_pos, calc_feat_src_pos)
                if not closest_dst_key or dist_sqr < closest_d:
                    closest_dst_key = feat_dst_key
                    closest_src_key = feat_src_key
                    closest_d = dist_sqr

            feat_dst_pos = applied_keys[closest_dst_key]
            feat_src_pos = src_vtx[closest_src_key]

            delta_feat = LerpTool.element_calc(
                dst_pos,
                feat_dst_pos,
                lambda x, y: x - y)

            target_pos = LerpTool.element_calc(
                feat_src_pos,
                delta_feat,
                lambda x, y: x + y)

            # translate dst vtx to src vtx
            cmds.xform(
                "{}.vtx[{}]".format(dst, dst_key),
                t=target_pos,
                relative=False)


class LerpToolHandler(QtGui.QGroupBox):

    step_sb = None

    @property
    def step(self):
        if not self.step_sb:
            return None
        return float(self.step_sb.value()) / 1000.

    def start(self):
        self.setTitle(u"이동")

        self.mainlayout = QtGui.QVBoxLayout()

        self.desc_l = QtGui.QLabel()
        self.desc_l.setText(
            u"가져온 템플릿의 버텍스들을 \n" +
            u"선택된 FO3 소스의 메쉬 모양으로 조금씩 이동시킵니다.")
        self.mainlayout.addWidget(self.desc_l)

        self.mainlayout.addSpacing(15)

        # progress bar
        step_widget = QtGui.QWidget()
        self.mainlayout.addWidget(step_widget)

        step_layout = QtGui.QHBoxLayout()
        step_widget.setLayout(step_layout)

        step_layout.addWidget(QtGui.QLabel(u"스텝"))

        self.step_sb = QtGui.QSlider()
        self.step_sb.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.step_sb.setRange(1, 1000)
        self.step_sb.setValue(1000)
        step_layout.addWidget(self.step_sb)

        self.preview_value_l = QtGui.QLabel(
            "{:.3f}".format(self.step))
        self.step_sb.valueChanged.connect(
            lambda v: self.preview_value_l.setText(
                "{:.3f}".format(self.step)
            ))
        step_layout.addWidget(self.preview_value_l)

        self.exec_btn = QtGui.QPushButton()
        self.exec_btn.setText(u"실행")
        self.exec_btn.clicked.connect(self.run)
        self.mainlayout.addWidget(self.exec_btn)

        self.setLayout(self.mainlayout)

    def run(self, e=False):
        src = Tool.Instance.source_name
        dst = Tool.Instance.target_name

        if not src:
            print(u"FO3 소스가 필요합니다.")
            return

        if not dst:
            print(u"FO4 템플릿이 필요합니다.")
            return

        LerpTool.lerp(src, dst, self.step)


class Tool(object):

    # static
    Instance = None

    # public
    fo3_source_handler = None
    fo4_template_handler = None
    lerp_tool_hanlder = None

    @property
    def package_path(self):
        return os.path.dirname(__file__)

    @property
    def fo4_template_path(self):
        return "{}/res/fo4_template.ma".format(self.package_path)

    @property
    def source_name(self):
        if not self.fo3_source_handler:
            return None
        return self.fo3_source_handler.source_name

    @property
    def target_name(self):
        if not self.fo4_template_handler:
            return None
        return self.fo4_template_handler.target_name

    def start(self):

        # static accessable
        Tool.Instance = self

        self.mainwin = QtGui.QWidget()
        self.mainwin.setWindowTitle(u"Transfer 도구")
        self.mainwin.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.mainwin.closeEvent = self.closeEvent

        self.mainlayout = QtGui.QVBoxLayout()

        self.fo3_source_handler = FO3_SourceHandler()
        self.fo3_source_handler.start()
        self.mainlayout.addWidget(self.fo3_source_handler)

        self.fo4_template_handler = FO4_TemplateHandler()
        self.fo4_template_handler.start()
        self.mainlayout.addWidget(self.fo4_template_handler)

        self.lerp_tool_hanlder = LerpToolHandler()
        self.lerp_tool_hanlder.start()
        self.mainlayout.addWidget(self.lerp_tool_hanlder)

        self.exit_btn = QtGui.QPushButton()
        self.exit_btn.setText(u"종료")
        self.exit_btn.clicked.connect(self.close)
        self.mainlayout.addWidget(self.exit_btn)

        self.mainwin.setLayout(self.mainlayout)
        self.mainwin.show()

    def close(self, e=False):
        self.mainwin.close()

    def closeEvent(self, e=None):
        self.fo3_source_handler.ensure_unlock_source()
        self.fo4_template_handler.ensure_unlock_target()

if __name__ == '__main__':
    tool = Tool()
    tool.start()
