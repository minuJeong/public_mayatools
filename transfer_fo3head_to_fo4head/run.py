# -*- coding: utf-8 -*-

import os
import math
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

        self.gc_assetid_le = QtGui.QLineEdit("4858")
        gc_load_row_layout.addWidget(self.gc_assetid_le)

        self.gc_load_btn = QtGui.QPushButton()
        self.gc_load_btn.setText(u"가져오기")
        self.gc_load_btn.clicked.connect(self.load_gc_asset)
        gc_load_row_layout.addWidget(self.gc_load_btn)

        self.gc_unload_btn = QtGui.QPushButton()
        self.gc_unload_btn.setText(u"지우기")
        self.gc_unload_btn.clicked.connect(self.unload_gc_asset)
        gc_load_row_layout.addWidget(self.gc_unload_btn)

        self.target_object_name_l = QtGui.QLabel()
        self.mainlayout.addWidget(self.target_object_name_l)

        sel_obj_row = QtGui.QWidget()
        self.mainlayout.addWidget(sel_obj_row)

        sel_obj_row_layout = QtGui.QHBoxLayout()
        sel_obj_row_layout.setContentsMargins(0, 0, 0, 0)
        sel_obj_row.setLayout(sel_obj_row_layout)

        self.capture_selected_btn = QtGui.QPushButton()
        self.capture_selected_btn.setText(u"선택된 오브젝트")
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
        self.load_gc_asset()

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
        preview_loaded_layout.setContentsMargins(0, 0, 0, 0)
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

        # Debug
        self.load_base_template()

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
            for node in self.imported_nodes:
                if not cmds.ls(node):
                    continue

                cmds.lockNode(self.imported_nodes, lock=False)


class LerpTool(object):
    """
    leave this class as static
    """

    @staticmethod
    def _get_ignore_list():
        """
        get-only list
         - bottom edge vertices
        """

        return \
            [2, 3, 4, 5, 8, 9, 12, 13, 14, 16, 17, 18, 20, 22, 24, 26, 27, 29,
             31, 32, 36, 38, 40, 42, 44, 45, 48, 49, 55, 57, 179, 180, 184, 187,
             190, 193, 194, 195, 197, 198, 199, 200, 201, 203, 209, 210, 215,
             236, 237, 238, 239, 296, 301, 317, 328, 329, 330, 334]

    fo4_z_offset = 2.78

    @staticmethod
    def get_vtx_pos(object_name, apply_ignore_list=False, with_key=False):
        mesh = cmds.listRelatives(object_name, type="mesh")
        if not mesh:
            return None

        ignore_list = LerpTool._get_ignore_list() if apply_ignore_list else []

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
    def _read_key_feature_data():
        data_file_path = "{}/mapping_table/key_features.json".format(
            Tool.Instance.package_path)

        parsed_data = None
        with open(data_file_path, 'r') as fp:
            parsed_data = json.loads(fp.read())
        return parsed_data

    @staticmethod
    def lerp(src, dst, step):
        """
        wrapping for conveniently change algorithms
        """

        # select algorithm

        # LerpTool._distance_based_lerp(src, dst, step)
        # LerpTool._distance_based_compete_lerp(src, dst, step)
        # LerpTool._relationship_based_lerp_closest_key(src, dst, step)
        # LerpTool._relationship_based_stochastic_spider_lerp(src, dst, step)
        # LerpTool._keymap_based_reactive_lerp(src, dst, step)
        print("DEPRECATED!")

    @staticmethod
    def _distance_based_lerp(src, dst, step):
        """
        dst decides src target by most similar local position
        """

        src_vtx = LerpTool.get_vtx_pos(src, apply_ignore_list=False)
        dst_vtx = LerpTool.get_vtx_pos(dst, apply_ignore_list=True, with_key=True)

        def get_closest_dst_pos(dst_pos):
            closest_pos = src_vtx[0]
            closest_d = LerpTool.distance_sqr(dst_pos, closest_pos)
            for src_pos in src_vtx[1:]:
                d = LerpTool.distance_sqr(dst_pos, src_pos)
                if d < closest_d:
                    closest_d = d
                    closest_pos = src_pos

            return closest_pos

        for idx, dst_pos in dst_vtx.items():
            src_pos = get_closest_dst_pos(dst_pos)
            target_pos = LerpTool.lerp_pos(src_pos, dst_pos, step)

            # translate dst vtx to src vtx
            cmds.xform(
                "{}.vtx[{}]".format(dst, idx),
                t=target_pos,
                relative=False)

    @staticmethod
    def _distance_based_compete_lerp(src, dst, step):
        """
        dst decides src target by most similar local position
        """

        src_vtx = LerpTool.get_vtx_pos(src, apply_ignore_list=False, with_key=True)
        dst_vtx = LerpTool.get_vtx_pos(dst, apply_ignore_list=True, with_key=True)

        # key: src_key
        # value: [dst_key, dst_key, dst_key, ...]
        src_to_dst_compete_map = {}

        def get_closest_keys(dst_pos, pool, count=1):
            if not pool:
                return [None]

            buff = []
            for src_key in pool:
                src_pos = src_vtx[src_key]
                buff.append((src_key, src_pos))

            return map(lambda x: x[0], sorted(
                buff,
                key=lambda x:
                    LerpTool.distance_sqr(dst_pos, x[1]))[:count])

        dst_iter = dst_vtx.items()
        for dst_key, dst_pos in dst_iter:

            # get closest_key
            closest_src_key = get_closest_keys(dst_pos, src_vtx.keys(), 1)[0]

            if closest_src_key not in src_to_dst_compete_map:
                src_to_dst_compete_map[closest_src_key] = []
            src_to_dst_compete_map[closest_src_key].append(dst_key)

        handled_src_keys = []
        while src_to_dst_compete_map:
            unused_keys = list(filter(
                lambda x:
                    x not in src_to_dst_compete_map.keys() and
                    x not in handled_src_keys,
                    src_vtx.keys()))

            keys_to_pop = []
            for src_key, dst_keys in src_to_dst_compete_map.items():
                if not dst_keys:
                    continue

                if len(dst_keys) == 1:
                    cmds.xform(
                        "{}.vtx[{}]".format(dst, dst_keys[0]),
                        t=src_vtx[src_key],
                        relative=False)
                    keys_to_pop.append(src_key)
                    continue

                src_pos = src_vtx[src_key]

                most_dst_key = get_closest_keys(src_pos, dst_keys, 1)[0]

                cmds.xform(
                    "{}.vtx[{}]".format(dst, most_dst_key),
                    t=src_pos,
                    relative=False)

                for dst_key in dst_keys:
                    if dst_key == most_dst_key:
                        continue

                    dst_pos = dst_vtx[dst_key]
                    alt_src_key = get_closest_keys(dst_pos, unused_keys, 1)[0]
                    if not alt_src_key:
                        break

                    if alt_src_key not in src_to_dst_compete_map:
                        src_to_dst_compete_map[alt_src_key] = []
                    src_to_dst_compete_map[alt_src_key].append(dst_key)

            for key in keys_to_pop:
                src_to_dst_compete_map.pop(key, None)
                handled_src_keys.append(key)
                print("  popped key: {}".format(key))

    @staticmethod
    def _relationship_based_lerp_closest_key(src, dst, step):
        """
        [DEPRECATED]
        select closest key feature, and move by key feature delta
        this refers mapping table
        """

        # move key_features
        applied_keys = {}
        key_features = LerpTool._read_key_feature_data()
        ignore_list = LerpTool._get_ignore_list()
        for dst_key, src_key in key_features.items():
            if dst_key in ignore_list:
                continue

            dst_pos = cmds.xform(
                "{}.vtx[{}]".format(dst, dst_key),
                ws=False, q=True, t=True, a=True)
            src_pos = cmds.xform(
                "{}.vtx[{}]".format(src, src_key),
                ws=False, q=True, t=True, a=True)

            target_pos = LerpTool.lerp_pos(src_pos, dst_pos, step)
            target_pos[2] += LerpTool.fo4_z_offset

            # translate dst vtx to src vtx
            cmds.xform(
                "{}.vtx[{}]".format(dst, dst_key),
                t=target_pos,
                relative=False)
            applied_keys[dst_key] = src_pos

        # move others
        dst_vtx = LerpTool.get_vtx_pos(dst, apply_ignore_list=True, with_key=True)
        src_vtx = LerpTool.get_vtx_pos(src, apply_ignore_list=False, with_key=True)

        # calculate based on relationship with key_feature
        for dst_key, dst_pos in dst_vtx.items():

            # skip key_features, since it's already calculated
            if dst_key in applied_keys.keys():
                continue

            closest_dst_key = key_features.keys()[0]
            closest_src_key = key_features.values()[0]
            closest_d = LerpTool.distance_sqr(dst_pos, src_vtx[closest_src_key])
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

    @staticmethod
    def _relationship_based_stochastic_spider_lerp(src, dst, step):
        """
        src: source FO3 mesh
        dst: destination FO4 mesh
        """

        dst_vtx = LerpTool.get_vtx_pos(dst, apply_ignore_list=True, with_key=True)
        src_vtx = LerpTool.get_vtx_pos(src, apply_ignore_list=False, with_key=True)

        dst_keys = dst_vtx.keys()
        src_keys = src_vtx.keys()

        def get_closest_key(pos, pool, count=1):
            return sorted(pool.keys(), key=lambda key: LerpTool.distance_sqr(pos, pool[key]))[:count]

        spider_con = {}
        for dst_key, src_key in zip(dst_keys, src_keys):
            spider_con[dst_key] = src_key

        # Debug
        def evaluate_spider_variance():
            dst_keys = spider_con.keys()
            src_keys = spider_con.values()

            dst_poss = map(lambda x: dst_vtx[x], dst_keys)
            src_poss = map(lambda x: src_vtx[x], src_keys)

            # calculate distances
            distances = []
            for dst_pos, src_pos in zip(dst_poss, src_poss):
                distances.append(LerpTool.distance_sqr(dst_pos, src_pos))

            # return variance
            n = len(distances)
            return (sum([x * x for x in distances]) / n) - \
                math.pow(sum(distances) / n, 2)

        def spider_advance():
            prev_variance = evaluate_spider_variance()

            suggestion = {}
            for dst_key, src_key in spider_con.items():
                dst_pos = dst_vtx[dst_key]
                closest_src_key = get_closest_key(dst_pos, src_vtx)

                if dst_key not in suggestion:
                    suggestion[dst_key] = []
                suggestion[dst_key].append(closest_src_key)

            result_variance = evaluate_spider_variance()
            return prev_variance - result_variance

        print("reduced {} variance".format(spider_advance()))

        # translate
        for dst_key, src_key in spider_con.items():
            cmds.xform(
                "{}.vtx[{}]".format(dst, dst_key),
                t=src_vtx[src_key],
                relative=False)

    @staticmethod
    def reactive_lerp_key_features(src, dst, influence):
        key_features_data = LerpTool._read_key_feature_data()

        dst_vtx = LerpTool.get_vtx_pos(dst, apply_ignore_list=True, with_key=True)
        src_vtx = LerpTool.get_vtx_pos(src, apply_ignore_list=False, with_key=True)

        def get_uri_vtx(obj, idx):
            return "{}.vtx[{}]".format(obj, idx)

        def get_closest_key(pos, vtx, count=1):
            return sorted(
                vtx.keys(),
                key=lambda key:
                    LerpTool.distance_sqr(pos, vtx[key]))[:count]

        for dst_key, src_key in key_features_data.items():
            dst_pos = dst_vtx[dst_key]
            src_pos = src_vtx[src_key]

            dx = dst_pos[0] - src_pos[0]
            dy = dst_pos[1] - src_pos[1]
            dz = dst_pos[2] - src_pos[2]

            cmds.xform(
                get_uri_vtx(dst, dst_key),
                t=src_pos,
                relative=False)

            for inf_key in get_closest_key(dst_pos, dst_vtx, influence):
                inf_pos = dst_vtx[inf_key]

                break


class LerpToolHandler(QtGui.QGroupBox):

    step_sb = None

    @property
    def step(self):
        return 1.0

    def start(self):
        self.setTitle(u"이동")

        self.mainlayout = QtGui.QVBoxLayout()

        self.desc_l = QtGui.QLabel()

        self.desc_l.setText(
            u"가져온 템플릿의 버텍스들을 \n" +
            u"선택된 FO3 소스의 메쉬 모양으로 이동시킵니다.")
        self.mainlayout.addWidget(self.desc_l)

        self.mainlayout.addSpacing(15)

        step_widget = QtGui.QWidget()
        self.mainlayout.addWidget(step_widget)
        step_layout = QtGui.QHBoxLayout()
        step_widget.setLayout(step_layout)

        step_layout.addWidget(QtGui.QLabel(u"영향력 점수"))

        self.key_feature_influence_s = QtGui.QSlider()
        self.key_feature_influence_s.setRange(1, 100)
        self.key_feature_influence_s.setValue(30)
        self.key_feature_influence_s.setOrientation(QtCore.Qt.Horizontal)
        step_layout.addWidget(self.key_feature_influence_s)

        slider_value = QtGui.QLabel("30")
        self.key_feature_influence_s.valueChanged.connect(
            lambda x: slider_value.setText(str(x)))
        step_layout.addWidget(slider_value)

        self.translate_key_features_btn = QtGui.QPushButton()
        self.translate_key_features_btn.setText(u"키 피쳐 이동")
        self.translate_key_features_btn.clicked.connect(self.translate_key_features)
        self.mainlayout.addWidget(self.translate_key_features_btn)

        self.setLayout(self.mainlayout)

    def translate_key_features(self, e=False):
        src = Tool.Instance.source_name
        dst = Tool.Instance.target_name

        LerpTool.reactive_lerp_key_features(
            src, dst,
            self.key_feature_influence_s.value())


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
