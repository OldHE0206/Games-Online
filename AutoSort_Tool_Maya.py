# _*_ coding:utf-8 _*_
__author__ = 'Old_He'
################################################################################
# AutoSort V3.0是一款为Autodesk Maya 2024设计的专业资产管理插件，
# 旨在提升3D资产管理的效率和规范性。该插件集成了文件管理、自动命名、材质创建、文件转换、
# 项目管理等多项功能，适用于游戏开发、影视制作、三维动画等领域的资产管理工作。
################################################################################

import os
import sys
import time
from PySide2 import QtCore, QtGui, QtWidgets
import maya.cmds as cmds
import csv

class AutoSortV03(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(AutoSortV03, self).__init__(parent)
        
        self.setWindowTitle("AutoSort")
        self.setObjectName("AutoSortV03")
        
        # 存储Company和Personnel信息
        self.company_code = ""
        self.personnel_code = ""

        # 存储Manager信息
        self.manager_code = ""

        # 存储Project和Asset信息
        self.project_code = ""
        self.project_start_time = ""
        self.project_end_time = ""
        self.asset_code = ""
        self.asset_type = ""
        self.asset_start_time = ""
        self.asset_end_time = ""
        
        # 存储新的资产信息
        self.phase_of_production = ""
        self.version = ""
        self.asset_file_type = ""

        # 存储当前角色类型
        self.current_role = None  # "auditor" 或 "supplier"
        
        # 设置窗口大小
        self.resize(791, 599)
        
        # 设置Maya风格样式
        self.set_maya_style()
        
        # 创建中央部件
        self.centralwidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralwidget)
        
        self.setup_ui()
        self.setup_menus()
        self.setup_connections()
        
        # 设置窗口标志，使其成为独立窗口
        self.setWindowFlags(QtCore.Qt.Window)
        
    def set_maya_style(self):
        """设置Maya风格的样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #333333;
            }
            QWidget {
                background-color: #333333;
                color: #cccccc;
                font-family: "Arial";
                font-size: 15px;
            }
            QLineEdit {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                padding: 3px;
                border-radius: 2px;
                selection-background-color: #4a6a9c;
            }
            QLineEdit:focus {
                border: 1px solid #6a8ab9;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555555;
                padding: 5px 10px;
                border-radius: 2px;
                min-height: 20px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #666666;
            }
            QPushButton:pressed {
                background-color: #353535;
                border: 1px solid #444444;
            }
            QListView {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 2px;
                alternate-background-color: #363636;
            }
            QListView::item {
                padding: 3px;
            }
            QListView::item:selected {
                background-color: #4a6a9c;
                color: white;
            }
            QListView::item:hover {
                background-color: #454545;
            }
            QTextBrowser {
                background-color: transparent;
                border: none;
            }
            QMenuBar {
                background-color: #353535;
                border-bottom: 1px solid #555555;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 10px;
                border-radius: 2px;
            }
            QMenuBar::item:selected {
                background-color: #4a4a4a;
            }
            QMenu {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                padding: 2px;
            }
            QMenu::item {
                padding: 4px 20px 4px 20px;
                font-size: 14px;
            }
            QMenu::item:selected {
                background-color: #4a6a9c;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555555;
                margin: 2px 5px;
            }
            QLabel {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 2px;
                padding: 5px;
            }
            QStatusBar {
                background-color: #353535;
                border-top: 1px solid #555555;
            }
            QPushButton#pin_button {
                background-color: #404040;
                border: 1px solid #555555;
                padding: 5px 10px;
                border-radius: 2px;
                min-height: 20px;
                min-width: 80px;
            }
            QPushButton#pin_button:checked {
                background-color: #4a6a9c;
                border: 1px solid #6a8ab9;
            }
            QPushButton#pin_button:hover {
                background-color: #4a4a4a;
                border: 1px solid #666666;
            }
            QPushButton#pin_button:checked:hover {
                background-color: #5a7aac;
                border: 1px solid #7a9ac9;
            }
            /* 供应商必填项样式 */
            QMenu::item[supplier_required="true"] {
                color: #4CAF50;
                font-weight: bold;
            }
            /* 审核人员必填项样式 */
            QMenu::item[auditor_required="true"] {
                color: #2196F3;
                font-weight: bold;
            }
        """)
        
    def setup_ui(self):
        # 创建主布局
        main_layout = QtWidgets.QHBoxLayout(self.centralwidget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 左侧布局
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setSpacing(10)
        
        # 文件地址部分
        file_layout = QtWidgets.QHBoxLayout()
        
        file_label = QtWidgets.QLabel("File Address:")
        file_label.setFixedWidth(100)
        
        self.file_path_edit = QtWidgets.QLineEdit()
        self.file_path_edit.setPlaceholderText("Select or enter file directory...")
        
        self.browse_button = QtWidgets.QPushButton("Browse")
        self.browse_button.setFixedWidth(80)
        
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.browse_button)
        
        left_layout.addLayout(file_layout)
        
        # 文件列表
        self.file_list = QtWidgets.QListWidget()
        left_layout.addWidget(self.file_list)
        
        # 底部信息 - 修改这里，添加Clear按钮
        bottom_layout = QtWidgets.QHBoxLayout()
        
        author_label = QtWidgets.QLabel("Old_He")
        version_label = QtWidgets.QLabel("ver.2025.12.06.01")
        version_label.setAlignment(QtCore.Qt.AlignRight)
        
        # 添加Clear按钮
        self.clear_button = QtWidgets.QPushButton("Clear All")
        self.clear_button.setFixedWidth(80)
        
        self.refresh_button = QtWidgets.QPushButton("Refresh")
        self.refresh_button.setFixedWidth(80)
        
        # 添加按钮到布局中，顺序为：作者信息 -> 版本信息 -> Clear按钮 -> Refresh按钮
        bottom_layout.addWidget(author_label)
        bottom_layout.addWidget(version_label)
        bottom_layout.addStretch()  # 添加弹簧，将按钮推到右侧
        bottom_layout.addWidget(self.clear_button)
        bottom_layout.addWidget(self.refresh_button)
        
        left_layout.addLayout(bottom_layout)
        
        # 右侧布局
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setSpacing(10)
        
        # 详情标题行 - 改为水平布局
        details_header_layout = QtWidgets.QHBoxLayout()
        
        details_label = QtWidgets.QLabel("Details")
        details_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 15px;
                padding: 5px;
                border: none;
                background-color: transparent;
            }
        """)
        
        # 添加置顶按钮
        self.pin_button = QtWidgets.QPushButton("Pin Window")
        self.pin_button.setObjectName("pin_button")
        self.pin_button.setCheckable(True)  # 设置为可勾选状态
        self.pin_button.setFixedWidth(150)
        self.pin_button.setToolTip("Keep window on top of other windows")
        
        # 设置按钮图标
        pin_icon = self.style().standardIcon(QtWidgets.QStyle.SP_TitleBarNormalButton)
        self.pin_button.setIcon(pin_icon)
        
        details_header_layout.addWidget(details_label)
        details_header_layout.addStretch()  # 添加弹簧将按钮推到右侧
        details_header_layout.addWidget(self.pin_button)
        
        right_layout.addLayout(details_header_layout)
        
        self.details_list = QtWidgets.QListWidget()
        right_layout.addWidget(self.details_list)
        
        # 预览部分
        preview_label = QtWidgets.QLabel("Preview")
        preview_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 15px;
                padding: 5px;
                border: none;
                background-color: transparent;
            }
        """)
        right_layout.addWidget(preview_label)
        
        # 使用QTextEdit代替QLabel，以便更好地显示文本内容
        self.preview_text = QtWidgets.QTextEdit()
        self.preview_text.setReadOnly(True)  # 设置为只读
        self.preview_text.setMinimumHeight(200)
        self.preview_text.setText("Preview area\n\nSelect an item to preview")
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 10px;
                color: #cccccc;
                font-family: "Arial";
                font-size: 12px;
            }
        """)
        right_layout.addWidget(self.preview_text)
        
        # 添加到主布局
        main_layout.addLayout(left_layout, 3)  # 左侧占3份
        main_layout.addLayout(right_layout, 2)  # 右侧占2份
        
    def setup_menus(self):
        # Asset Management Menu
        asset_menu = self.menuBar().addMenu("Asset Management")
        
        # Categorized Search Submenu
        search_menu = asset_menu.addMenu("Categorized Search")
        
        # File Format Submenu
        format_menu = search_menu.addMenu("File Format")
        
        self.action_fbx = QtWidgets.QAction(".fbx", self)
        format_menu.addAction(self.action_fbx)
        
        self.action_obj = QtWidgets.QAction(".obj", self)
        format_menu.addAction(self.action_obj)
        
        self.action_ma = QtWidgets.QAction(".ma", self)
        format_menu.addAction(self.action_ma)
        
        self.action_mb = QtWidgets.QAction(".mb", self)
        format_menu.addAction(self.action_mb)
        
        self.action_usd = QtWidgets.QAction(".usd", self)
        format_menu.addAction(self.action_usd)
        
        self.action_abc = QtWidgets.QAction(".abc", self)
        format_menu.addAction(self.action_abc)
        
        self.action_png = QtWidgets.QAction(".png", self)
        format_menu.addAction(self.action_png)
        
        self.action_jpeg = QtWidgets.QAction(".jpeg", self)
        format_menu.addAction(self.action_jpeg)
        
        self.action_EXR = QtWidgets.QAction(".EXR", self)
        format_menu.addAction(self.action_EXR)
        
        self.action_tga = QtWidgets.QAction(".tga", self)
        format_menu.addAction(self.action_tga)
        
        # File Type Submenu
        type_menu = search_menu.addMenu("File Type")
        
        # Model Submenu
        model_menu = type_menu.addMenu("Model")
        
        self.action_character_model = QtWidgets.QAction("Character Models", self)
        model_menu.addAction(self.action_character_model)
        
        self.action_scene_model = QtWidgets.QAction("Scene Models", self)
        model_menu.addAction(self.action_scene_model)
        
        self.action_other_models = QtWidgets.QAction("Other Models", self)
        model_menu.addAction(self.action_other_models)
        
        # Rigging Submenu
        rigging_menu = type_menu.addMenu("Rigging")
        
        self.action_character_rigging = QtWidgets.QAction("Character Rigging", self)
        rigging_menu.addAction(self.action_character_rigging)
        
        self.action_scene_rigging = QtWidgets.QAction("Scene Rigging", self)
        rigging_menu.addAction(self.action_scene_rigging)
        
        self.action_other_rigging = QtWidgets.QAction("Other Rigging", self)
        rigging_menu.addAction(self.action_other_rigging)
        
        self.action_animation = QtWidgets.QAction("Animation", self)
        type_menu.addAction(self.action_animation)
        
        self.action_texture = QtWidgets.QAction("Texture", self)
        type_menu.addAction(self.action_texture)
        
        # Import/Export Submenu
        import_menu = asset_menu.addMenu("Import/Export")
        
        self.action_import_selection = QtWidgets.QAction("Import Selection", self)
        import_menu.addAction(self.action_import_selection)
        
        self.action_import_all = QtWidgets.QAction("Import All", self)
        import_menu.addAction(self.action_import_all)
        
        # Export Selection Submenu
        export_menu = import_menu.addMenu("Export Selection")
        
        self.action_combined_export = QtWidgets.QAction("Combined Export", self)
        export_menu.addAction(self.action_combined_export)
        
        self.action_individual_export = QtWidgets.QAction("Individual Export", self)
        export_menu.addAction(self.action_individual_export)
        
        # Auto Import Submenu
        auto_import_menu = import_menu.addMenu("Auto Import")

        self.action_compliance_check = QtWidgets.QAction("Compliance Check", self)
        auto_import_menu.addAction(self.action_compliance_check)

        self.action_import_all_2 = QtWidgets.QAction("Auto Import All", self)
        auto_import_menu.addAction(self.action_import_all_2)
        
        self.action_auto_export = QtWidgets.QAction("Auto Export", self)
        import_menu.addAction(self.action_auto_export)
        
        # File Processing Menu
        file_menu = self.menuBar().addMenu("File Processing")
        
        # File Conversion Submenu
        conversion_menu = file_menu.addMenu("File Conversion")
        
        self.action_obj_fbx = QtWidgets.QAction("OBJ → FBX", self)
        conversion_menu.addAction(self.action_obj_fbx)
        
        self.action_fbx_obj = QtWidgets.QAction("FBX → OBJ", self)
        conversion_menu.addAction(self.action_fbx_obj)
        
        # Automation Menu
        auto_menu = self.menuBar().addMenu("Automation")
        
        self.action_auto_naming = QtWidgets.QAction("Auto-Naming", self)
        auto_menu.addAction(self.action_auto_naming)
        
        # Auto-Organization Submenu
        org_menu = auto_menu.addMenu("Auto-Organization")
        
        self.action_model = QtWidgets.QAction("Model", self)
        org_menu.addAction(self.action_model)
        
        self.action_rigging = QtWidgets.QAction("Rigging", self)
        org_menu.addAction(self.action_rigging)
        
        self.action_animation_2 = QtWidgets.QAction("Animation", self)
        org_menu.addAction(self.action_animation_2)
        
        # Logging Menu
        log_menu = self.menuBar().addMenu("Logging")
        
        # Work Plan Submenu
        work_menu = log_menu.addMenu("Work Plan")
        
        self.action_work_log = QtWidgets.QAction("Work Log", self)
        work_menu.addAction(self.action_work_log)
        
        # Help Menu
        help_menu = self.menuBar().addMenu("Help")
        
        self.action_documentation = QtWidgets.QAction("Documentation", self)
        help_menu.addAction(self.action_documentation)
        
        # Runtime Check Submenu
        runtime_menu = help_menu.addMenu("Runtime Check")
        
        self.action_environment_validation = QtWidgets.QAction("Environment Validation", self)
        runtime_menu.addAction(self.action_environment_validation)
        
        # PM Menu
        pm_menu = self.menuBar().addMenu("PM")
        
        # Vendor Submenu
        vendor_menu = pm_menu.addMenu("Vendor")
        
        self.action_company = QtWidgets.QAction("Company (Vendor)", self)
        vendor_menu.addAction(self.action_company)
        
        self.action_personnel = QtWidgets.QAction("Personnel (Vendor)", self)
        vendor_menu.addAction(self.action_personnel)
        
        # 添加Manager选项
        self.action_manager = QtWidgets.QAction("Manager (Auditor)", self)
        pm_menu.addAction(self.action_manager)

        # Project Submenu - 修改这个部分
        project_menu = pm_menu.addMenu("Project")
        
        # 创建New Project子菜单
        new_project_menu = project_menu.addMenu("New Project")
        
        # 在New Project子菜单中添加按钮
        self.action_project_code = QtWidgets.QAction("Project Code (Required)", self)
        new_project_menu.addAction(self.action_project_code)
        
        self.action_project_start_time = QtWidgets.QAction("Project Start Time (Auditor)", self)
        new_project_menu.addAction(self.action_project_start_time)
        
        self.action_project_end_time = QtWidgets.QAction("Project End Time (Auditor)", self)
        new_project_menu.addAction(self.action_project_end_time)
        
        self.action_asset_code = QtWidgets.QAction("Asset Code (Required)", self)
        new_project_menu.addAction(self.action_asset_code)
        
        self.action_asset_type = QtWidgets.QAction("Asset Type (Required)", self)
        new_project_menu.addAction(self.action_asset_type)
        
        self.action_asset_start_time = QtWidgets.QAction("Asset Start Time (Auditor)", self)
        new_project_menu.addAction(self.action_asset_start_time)
        
        self.action_asset_end_time = QtWidgets.QAction("Asset End Time (Auditor)", self)
        new_project_menu.addAction(self.action_asset_end_time)

        # 新增三个按钮
        self.action_phase_of_production = QtWidgets.QAction("Phase Of Production (Required)", self)
        new_project_menu.addAction(self.action_phase_of_production)
        
        self.action_version = QtWidgets.QAction("Version (Supplier)", self)
        new_project_menu.addAction(self.action_version)
        
        self.action_asset_file_type = QtWidgets.QAction("Asset File Type (Required)", self)
        new_project_menu.addAction(self.action_asset_file_type)
        
        # 添加Set Project按钮
        self.action_set_project = QtWidgets.QAction("Set Project", self)
        project_menu.addAction(self.action_set_project)
        
        # 更新菜单项样式
        self.update_menu_styles()
        
    def update_menu_styles(self):
        """更新菜单项的样式以显示角色提示"""
        # 供应商必填项
        supplier_required = [
            self.action_company,
            self.action_personnel,
            self.action_project_code,
            self.action_asset_code,
            self.action_asset_type,
            self.action_phase_of_production,
            self.action_version,
            self.action_asset_file_type
        ]
        
        # 审核人员必填项
        auditor_required = [
            self.action_manager,
            self.action_project_start_time,
            self.action_project_end_time,
            self.action_asset_start_time,
            self.action_asset_end_time
        ]
        
        for action in supplier_required:
            action.setProperty("supplier_required", "true")
            
        for action in auditor_required:
            action.setProperty("auditor_required", "true")
            
        # 更新样式
        self.style().unpolish(self)
        self.style().polish(self)
        

    def setup_connections(self):
        # 连接按钮信号
        self.browse_button.clicked.connect(self.browse_directory)
        self.refresh_button.clicked.connect(self.refresh_files)
        
        # 连接Clear按钮信号
        self.clear_button.clicked.connect(self.clear_all_info)
        
        # 连接列表选择信号
        self.file_list.itemSelectionChanged.connect(self.on_file_selected)
        
        # 连接置顶按钮信号
        self.pin_button.toggled.connect(self.toggle_window_pin)
        
        # 连接菜单动作 - 文件格式过滤
        self.action_fbx.triggered.connect(lambda: self.filter_by_format(".fbx"))
        self.action_obj.triggered.connect(lambda: self.filter_by_format(".obj"))
        self.action_ma.triggered.connect(lambda: self.filter_by_format(".ma"))
        self.action_mb.triggered.connect(lambda: self.filter_by_format(".mb"))
        self.action_usd.triggered.connect(lambda: self.filter_by_format(".usd"))
        self.action_abc.triggered.connect(lambda: self.filter_by_format(".abc"))
        self.action_png.triggered.connect(lambda: self.filter_by_format(".png"))
        self.action_jpeg.triggered.connect(lambda: self.filter_by_format(".jpeg"))
        self.action_EXR.triggered.connect(lambda: self.filter_by_format(".exr"))
        self.action_tga.triggered.connect(lambda: self.filter_by_format(".tga"))
        
        # 连接Compliance Check菜单动作
        self.action_compliance_check.triggered.connect(self.compliance_check)
        
        # 连接Auto Import All菜单动作（新增）
        self.action_import_all_2.triggered.connect(self.auto_import_all)
        
        # 连接Auto Export菜单动作（新增）
        self.action_auto_export.triggered.connect(self.export_models_and_textures)

        # 连接文件转换菜单动作
        self.action_obj_fbx.triggered.connect(self.convert_obj_to_fbx)
        self.action_fbx_obj.triggered.connect(self.convert_fbx_to_obj)

        # 连接Environment Validation菜单动作
        self.action_environment_validation.triggered.connect(self.environment_validation)   

        # 连接Vendor菜单动作
        self.action_company.triggered.connect(self.set_company_code)
        self.action_personnel.triggered.connect(self.set_personnel_code)
        self.action_manager.triggered.connect(self.create_pm_document)
        
        # 连接Project菜单动作
        self.action_project_code.triggered.connect(self.set_project_code)
        self.action_project_start_time.triggered.connect(self.set_project_start_time)
        self.action_project_end_time.triggered.connect(self.set_project_end_time)
        self.action_asset_code.triggered.connect(self.set_asset_code)
        self.action_asset_type.triggered.connect(self.set_asset_type)
        self.action_asset_start_time.triggered.connect(self.set_asset_start_time)
        self.action_asset_end_time.triggered.connect(self.set_asset_end_time)

        # 新增三个连接
        self.action_phase_of_production.triggered.connect(self.set_phase_of_production)
        self.action_version.triggered.connect(self.set_version)
        self.action_asset_file_type.triggered.connect(self.set_asset_file_type)

        # 连接文件类型过滤菜单动作 - 按命名规范过滤
        self.action_character_model.triggered.connect(lambda: self.filter_by_file_type("character_models"))
        self.action_scene_model.triggered.connect(lambda: self.filter_by_file_type("scene_models"))
        self.action_other_models.triggered.connect(lambda: self.filter_by_file_type("other_models"))
        self.action_character_rigging.triggered.connect(lambda: self.filter_by_file_type("character_rigging"))
        self.action_scene_rigging.triggered.connect(lambda: self.filter_by_file_type("scene_rigging"))
        self.action_other_rigging.triggered.connect(lambda: self.filter_by_file_type("other_rigging"))
        self.action_animation.triggered.connect(lambda: self.filter_by_file_type("animation"))
        self.action_texture.triggered.connect(lambda: self.filter_by_file_type("texture"))

        # 连接Import/Export菜单动作
        self.action_import_selection.triggered.connect(self.import_selection)
        self.action_import_all.triggered.connect(self.import_all)
        self.action_combined_export.triggered.connect(self.combined_export)
        self.action_individual_export.triggered.connect(self.individual_export)
        
        # 连接Auto-Naming菜单动作
        self.action_auto_naming.triggered.connect(self.auto_naming)
        
        # 连接Auto-Organization菜单动作
        self.action_model.triggered.connect(self.create_materials_for_models)
        self.action_rigging.triggered.connect(lambda: QtWidgets.QMessageBox.information(self, "Rigging", "Rigging功能待开发"))
        self.action_animation_2.triggered.connect(lambda: QtWidgets.QMessageBox.information(self, "Animation", "Animation功能待开发"))

        # 连接Set Project按钮
        self.action_set_project.triggered.connect(self.set_project_workflow)
        
        # 连接Work Log菜单动作
        self.action_work_log.triggered.connect(self.work_log_analysis)

        # 连接Help菜单动作
        self.action_documentation.triggered.connect(self.show_documentation)

    def browse_directory(self):
        """浏览目录"""
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", ""
        )
        if directory:
            self.file_path_edit.setText(directory)
            self.scan_directory(directory)
            
    def scan_directory(self, directory):
        """扫描目录中的文件"""
        self.file_list.clear()
        self.details_list.clear()
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    
                    item = QtWidgets.QListWidgetItem(relative_path)
                    item.setData(QtCore.Qt.UserRole, file_path)
                    
                    # 根据文件类型设置图标
                    ext = os.path.splitext(file)[1].lower()
                    if ext in [".ma", ".mb"]:
                        item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
                    elif ext in [".fbx", ".obj"]:
                        item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirLinkIcon))
                    elif ext in [".png", ".jpg", ".jpeg", ".tga", ".exr"]:
                        item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileLinkIcon))
                    elif ext in [".txt", ".log"]:
                        item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView))
                    else:
                        item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
                    
                    self.file_list.addItem(item)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to scan directory: {str(e)}")

    def filter_by_file_type(self, asset_type_filter, phase_filter=None):
        """按文件命名规范中的类型过滤文件"""
        directory = self.file_path_edit.text()
        if not directory or not os.path.exists(directory):
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a valid directory first.")
            return
            
        self.file_list.clear()
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    # 检查是否为ma或mb文件
                    if file.lower().endswith(('.ma', '.mb')):
                        # 解析文件名
                        base_name = os.path.splitext(file)[0]
                        parts = base_name.split('_')
                        
                        # 检查是否符合命名规范（7个部分）
                        if len(parts) == 7:
                            # 获取Asset Type和Phase
                            file_asset_type = parts[1]  # 第二个部分是Asset Type
                            file_phase = parts[3]      # 第四个部分是Phase
                            
                            # 根据过滤条件判断是否显示
                            should_display = False
                            
                            # Character Models: Asset Type = C, Phase = M
                            if asset_type_filter == "character_models":
                                should_display = (file_asset_type == "C" and file_phase == "M")
                            
                            # Scene Models: Asset Type = S, Phase = M
                            elif asset_type_filter == "scene_models":
                                should_display = (file_asset_type == "S" and file_phase == "M")
                            
                            # Other Models: Asset Type = O, Phase = M
                            elif asset_type_filter == "other_models":
                                should_display = (file_asset_type == "O" and file_phase == "M")
                            
                            # Character Rigging: Asset Type = C, Phase = R
                            elif asset_type_filter == "character_rigging":
                                should_display = (file_asset_type == "C" and file_phase == "R")
                            
                            # Scene Rigging: Asset Type = S, Phase = R
                            elif asset_type_filter == "scene_rigging":
                                should_display = (file_asset_type == "S" and file_phase == "R")
                            
                            # Other Rigging: Asset Type = O, Phase = R
                            elif asset_type_filter == "other_rigging":
                                should_display = (file_asset_type == "O" and file_phase == "R")
                            
                            # Animation: Phase = A
                            elif asset_type_filter == "animation":
                                should_display = (file_phase == "A")
                            
                            # Texture: Phase = T
                            elif asset_type_filter == "texture":
                                should_display = (file_phase == "T")
                            
                            # 如果符合条件，添加到文件列表
                            if should_display:
                                file_path = os.path.join(root, file)
                                relative_path = os.path.relpath(file_path, directory)
                                
                                item = QtWidgets.QListWidgetItem(relative_path)
                                item.setData(QtCore.Qt.UserRole, file_path)
                                item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
                                self.file_list.addItem(item)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to filter files: {str(e)}")

    def auto_naming(self):
        """自动重命名功能：根据上下文重命名模型或贴图"""
        # 检查是否选择了文件目录
        directory = self.file_path_edit.text()
        
        # 检查目录中是否有支持的贴图文件（仅在目录存在时）
        has_textures = False
        if directory and os.path.exists(directory):
            texture_extensions = ['.jpeg', '.jpg', '.png', '.exr', '.tga']
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in texture_extensions:
                        has_textures = True
                        break
                if has_textures:
                    break
        
        if has_textures:
            # 执行贴图重命名
            self.rename_textures(directory)
        else:
            # 执行模型重命名（原逻辑）
            self.rename_maya_models()

    def rename_textures(self, directory):
        """重命名贴图文件"""
        try:
            # 支持的贴图格式
            texture_extensions = ['.jpeg', '.jpg', '.png', '.exr', '.tga']
            
            # 贴图类型映射
            texture_type_map = {
                'basecolor': 'B',
                'base_color': 'B',
                'color': 'B',
                'albedo': 'B',
                'diffuse': 'B',
                'metalness': 'M',
                'metallic': 'M',
                'roughness': 'R',
                'glossiness': 'R',
                'emissive': 'E',
                'emission': 'E',
                'normal': 'N',
                'normals': 'N',
                'height': 'H',
                'displacement': 'H'
            }
            
            renamed_count = 0
            failed_files = []
            
            # 遍历目录中的文件
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # 只处理支持的贴图格式
                    if file_ext in texture_extensions:
                        file_path = os.path.join(root, file)
                        original_name = os.path.splitext(file)[0]  # 去掉扩展名
                        
                        try:
                            # 解析原始文件名
                            # 格式可能是：模型文件名_模型材质球名_贴图类型_UDIM
                            parts = original_name.split('_')
                            
                            if len(parts) >= 10:  # 至少需要10个部分才能包含完整的材质球名
                                # 查找材质球名部分
                                # 材质球名格式：项目代码_资产类型_资产编码_模型详细命名_M_S
                                # 通常出现在文件名的后半部分
                                
                                # 从后向前搜索，找到第一个"M"后面的"S"
                                s_index = -1
                                for i in range(len(parts)-1, -1, -1):
                                    if parts[i] == "S" and i > 0 and parts[i-1] == "M":
                                        s_index = i
                                        break
                                
                                if s_index != -1:
                                    # 提取材质球名（从M_S向前追溯5个部分）
                                    # 材质球名格式：项目代码_资产类型_资产编码_模型详细命名_M_S
                                    material_start_index = max(0, s_index - 5)  # 从S向前追溯5个部分
                                    material_name_parts = parts[material_start_index:s_index+1]
                                    material_name = '_'.join(material_name_parts)
                                    
                                    # 提取贴图类型（S后面的部分）
                                    if s_index + 1 < len(parts):
                                        texture_info = parts[s_index+1:]
                                        
                                        if texture_info:
                                            # 获取贴图类型文本
                                            texture_type_text = texture_info[0].lower()
                                            
                                            # 映射贴图类型
                                            texture_type_code = 'B'  # 默认BaseColor
                                            for key, value in texture_type_map.items():
                                                if key in texture_type_text:
                                                    texture_type_code = value
                                                    break
                                            
                                            # 检查是否有UDIM编号
                                            udim_part = ""
                                            if len(texture_info) > 1:
                                                # 检查最后一个部分是否是UDIM编号（4位数字）
                                                last_part = texture_info[-1]
                                                if last_part.isdigit() and len(last_part) == 4:
                                                    udim_part = f"_{last_part}"
                                            
                                            # 构建新文件名
                                            if udim_part:
                                                new_name = f"{material_name}_{texture_type_code}{udim_part}"
                                            else:
                                                new_name = f"{material_name}_{texture_type_code}"
                                            
                                            new_file = f"{new_name}{file_ext}"
                                            new_path = os.path.join(root, new_file)
                                            
                                            # 重命名文件
                                            if file_path != new_path:
                                                # 检查新文件是否已存在
                                                if os.path.exists(new_path):
                                                    # 添加后缀避免冲突
                                                    counter = 1
                                                    while os.path.exists(new_path):
                                                        new_name_with_counter = f"{new_name}_{counter:02d}"
                                                        new_file = f"{new_name_with_counter}{file_ext}"
                                                        new_path = os.path.join(root, new_file)
                                                        counter += 1
                                                
                                                os.rename(file_path, new_path)
                                                renamed_count += 1
                                                print(f"重命名: {file} -> {new_file}")
                                            else:
                                                print(f"无需重命名: {file}")
                                                
                                        else:
                                            failed_files.append(f"{file}: 无法提取贴图类型信息")
                                    else:
                                        failed_files.append(f"{file}: 文件名格式错误，找不到贴图类型信息")
                                else:
                                    failed_files.append(f"{file}: 文件名中未找到材质球名部分（M_S格式）")
                            else:
                                failed_files.append(f"{file}: 文件名部分不足，无法解析")
                                
                        except Exception as e:
                            failed_files.append(f"{file}: {str(e)}")
            
            # 显示结果
            message = f"贴图重命名完成！\n重命名了 {renamed_count} 个贴图文件。\n\n"
            
            if failed_files:
                message += f"失败 {len(failed_files)} 个文件：\n"
                for failed in failed_files[:10]:  # 只显示前10个失败
                    message += f"  - {failed}\n"
                if len(failed_files) > 10:
                    message += f"  ... 还有 {len(failed_files) - 10} 个失败文件\n"
            
            QtWidgets.QMessageBox.information(
                self, "Texture Renaming Complete",
                message
            )
            
            # 刷新文件列表显示新名称
            self.scan_directory(directory)
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Texture Renaming Error",
                f"贴图重命名过程中出错：{str(e)}"
            )

    def rename_maya_models(self):
        """重命名Maya场景中的模型并创建材质球和shadingEngine"""
        try:
            # 获取当前Maya文件名
            current_file = cmds.file(query=True, sceneName=True)
            if not current_file:
                QtWidgets.QMessageBox.warning(
                    self, "No File",
                    "Maya场景文件未保存。请先保存文件以获取文件名信息。"
                )
                return
            
            # 从文件名提取信息
            file_name = os.path.basename(current_file)
            base_name = os.path.splitext(file_name)[0]
            
            # 解析文件名（格式：项目代码_资产类型_资产编码_阶段_公司代码_人员代码_版本）
            parts = base_name.split('_')
            if len(parts) != 7:
                QtWidgets.QMessageBox.warning(
                    self, "Invalid File Name",
                    "Maya文件名不符合命名规范。\n"
                    "格式应为：项目代码_资产类型_资产编码_阶段_公司代码_人员代码_版本\n"
                    f"当前文件名：{file_name}"
                )
                return
            
            project_code = parts[0]      # 项目代码
            asset_type = parts[1]        # 资产类型 (C/S/O)
            asset_code = parts[2]        # 资产编码
            phase = parts[3]             # 阶段 (M/S/T/D/R/A)
            company_code = parts[4]      # 公司代码
            personnel_code = parts[5]    # 人员代码
            version = parts[6]           # 版本
            
            # 检查阶段是否为模型阶段
            if phase != 'M':
                QtWidgets.QMessageBox.warning(
                    self, "Wrong Phase",
                    "当前文件不是模型阶段（Phase='M'）的文件。\n"
                    "自动命名功能仅适用于模型阶段。"
                )
                return
            
            # 获取所有mesh类型的模型
            meshes = cmds.ls(type='mesh', long=True)
            if not meshes:
                QtWidgets.QMessageBox.warning(
                    self, "No Meshes",
                    "场景中没有找到mesh类型的模型。"
                )
                return
            
            renamed_count = 0
            materials_dict = {}  # 存储材质球和对应模型的映射
            created_materials = []  # 存储已创建的材质球
            created_shaders = []  # 存储已创建的shadingEngine
            
            for mesh in meshes:
                try:
                    # 获取mesh的父变换节点
                    parent = cmds.listRelatives(mesh, parent=True, fullPath=True)
                    if not parent:
                        continue
                    
                    transform_node = parent[0]
                    current_name = transform_node.split('|')[-1]
                    
                    # 解析当前模型名称
                    # 格式应为：RightHand 或 RightHand_001
                    base_parts = current_name.split('_')
                    
                    if len(base_parts) == 1:
                        # 没有序号：RightHand
                        model_detail = base_parts[0]
                        model_number = None
                    elif len(base_parts) >= 2 and base_parts[-1].isdigit():
                        # 有序号：RightHand_001
                        model_detail = '_'.join(base_parts[:-1])
                        model_number = base_parts[-1]
                    else:
                        # 不符合规范，使用原始名称作为详细命名
                        model_detail = current_name
                        model_number = None
                    
                    # 构建模型新名称
                    if model_number:
                        model_new_name = f"{project_code}_{asset_type}_{asset_code}_{model_detail}_{phase}_{model_number}"
                    else:
                        model_new_name = f"{project_code}_{asset_type}_{asset_code}_{model_detail}_{phase}"
                    
                    # 重命名模型
                    if current_name != model_new_name:
                        try:
                            # 获取短名称进行重命名
                            short_name = transform_node.split('|')[-1]
                            new_name = cmds.rename(short_name, model_new_name)
                            renamed_count += 1
                            print(f"模型重命名: {current_name} -> {new_name}")
                            
                            # 更新transform_node为新名称
                            transform_node = transform_node.replace(short_name, new_name)
                            
                        except Exception as rename_error:
                            print(f"重命名失败 {current_name} -> {model_new_name}: {str(rename_error)}")
                            new_name = current_name  # 使用原始名称继续处理
                        else:
                            new_name = model_new_name
                    else:
                        new_name = current_name
                    
                    # 构建材质球名称和shadingEngine名称
                    material_name = f"{project_code}_{asset_type}_{asset_code}_{model_detail}_M_S"
                    shader_name = f"{project_code}_{asset_type}_{asset_code}_{model_detail}_M_S_SG"
                    
                    # 创建或获取材质球
                    if material_name not in materials_dict:
                        # 检查是否已存在同名材质球
                        if not cmds.objExists(material_name):
                            # 创建aiStandardSurface材质球
                            ai_standard = cmds.shadingNode('aiStandardSurface', asShader=True, name=material_name)
                            
                            # 设置材质球的基本属性
                            cmds.setAttr(f"{material_name}.base", 1.0)  # 设置基础权重
                            cmds.setAttr(f"{material_name}.baseColor", 0.5, 0.5, 0.5, type="double3")  # 设置基础颜色为灰色
                            cmds.setAttr(f"{material_name}.metalness", 0.0)  # 设置金属度为0
                            cmds.setAttr(f"{material_name}.specularRoughness", 0.5)  # 设置粗糙度
                            
                            created_materials.append(material_name)
                            print(f"创建材质球: {material_name}")
                        else:
                            ai_standard = material_name
                            print(f"使用现有材质球: {material_name}")
                        
                        # 创建或获取shadingEngine节点
                        if not cmds.objExists(shader_name):
                            # 创建shadingEngine节点
                            shading_group = cmds.sets(
                                renderable=True, 
                                noSurfaceShader=True, 
                                empty=True, 
                                name=shader_name
                            )
                            
                            # 连接材质球的outColor到shadingEngine的surfaceShader
                            cmds.connectAttr(f"{material_name}.outColor", f"{shader_name}.surfaceShader")
                            
                            created_shaders.append(shader_name)
                            print(f"创建shadingEngine: {shader_name}")
                        else:
                            shading_group = shader_name
                            print(f"使用现有shadingEngine: {shader_name}")
                        
                        # 存储到字典中
                        materials_dict[material_name] = {
                            'material': material_name,
                            'shader': shader_name,
                            'model_detail': model_detail,
                            'models': []
                        }
                    
                    # 将当前模型添加到材质球的模型列表中
                    if new_name not in materials_dict[material_name]['models']:
                        materials_dict[material_name]['models'].append(new_name)
                    
                    # 将材质指定给当前模型 - 修改的关键部分
                    try:
                        # 获取模型的mesh节点（可能有多个）
                        mesh_nodes = cmds.listRelatives(transform_node, shapes=True, type='mesh')
                        if mesh_nodes:
                            for mesh_node in mesh_nodes:
                                # 将材质指定给每个mesh节点
                                cmds.sets(mesh_node, edit=True, forceElement=shader_name)
                                print(f"为模型 {new_name} 的mesh {mesh_node} 指定材质 {shader_name}")
                        else:
                            # 如果没有找到mesh节点，尝试直接使用原始mesh
                            cmds.sets(mesh, edit=True, forceElement=shader_name)
                            print(f"为模型 {new_name} 指定材质 {shader_name}")
                    except Exception as assign_error:
                        print(f"指定材质失败 {new_name} -> {shader_name}: {str(assign_error)}")
                    
                except Exception as mesh_error:
                    print(f"处理模型时出错 {mesh}: {str(mesh_error)}")
            
            # 显示重命名和材质创建结果
            message = f"自动命名和材质创建完成！\n"
            message += f"重命名了 {renamed_count} 个模型。\n"
            message += f"创建了 {len(created_materials)} 个材质球。\n"
            message += f"创建了 {len(created_shaders)} 个 shadingEngine 节点。\n\n"
            
            # 统计材质指定情况
            total_materials_assigned = 0
            for material_info in materials_dict.values():
                total_materials_assigned += len(material_info['models'])
            
            message += f"为 {total_materials_assigned} 个模型指定了材质。\n\n"
            
            # 显示材质球共享信息
            if materials_dict:
                shared_materials = {k: v for k, v in materials_dict.items() if len(v['models']) > 1}
                if shared_materials:
                    message += "材质球共享情况：\n"
                    for key, info in shared_materials.items():
                        message += f"\n材质球 '{info['material']}' 被以下模型共享：\n"
                        for model in info['models']:
                            message += f"  - {model}\n"
                
                # 显示材质球和shadingEngine连接信息
                message += "\n材质球和shadingEngine连接：\n"
                for material_name, info in materials_dict.items():
                    message += f"\n材质球: {info['material']}"
                    message += f"\nshadingEngine: {info['shader']}"
                    message += f"\n连接的模型数量: {len(info['models'])}"
            
            QtWidgets.QMessageBox.information(
                self, "Auto-Naming Complete",
                message
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Auto-Naming Error",
                f"自动命名过程中出错：{str(e)}"
            )

    def create_materials_for_models(self):
        """根据Browse文件夹中的贴图为场景中的模型创建材质球、shadingEngine和贴图节点（同步修复shadingEngine重复问题）"""
        try:
            # 获取当前Maya文件名
            current_file = cmds.file(query=True, sceneName=True)
            if not current_file:
                QtWidgets.QMessageBox.warning(
                    self, "No File",
                    "Maya场景文件未保存。请先保存文件以获取文件名信息。"
                )
                return
            
            # 从文件名提取信息
            file_name = os.path.basename(current_file)
            base_name = os.path.splitext(file_name)[0]
            
            # 解析文件名（格式：项目代码_资产类型_资产编码_阶段_公司代码_人员代码_版本）
            parts = base_name.split('_')
            if len(parts) != 7:
                QtWidgets.QMessageBox.warning(
                    self, "Invalid File Name",
                    "Maya文件名不符合命名规范。\n"
                    "格式应为：项目代码_资产类型_资产编码_阶段_公司代码_人员代码_版本\n"
                    f"当前文件名：{file_name}"
                )
                return
            
            project_code = parts[0]      # 项目代码
            asset_type = parts[1]        # 资产类型 (C/S/O)
            asset_code = parts[2]        # 资产编码
            
            # 检查阶段是否为模型阶段
            phase = parts[3]             # 阶段 (M/S/T/D/R/A)
            if phase != 'M':
                QtWidgets.QMessageBox.warning(
                    self, "Wrong Phase",
                    "当前文件不是模型阶段（Phase='M'）的文件。\n"
                    "材质创建功能仅适用于模型阶段。"
                )
                return
            
            # 获取Browse选择的目录
            texture_dir = self.file_path_edit.text()
            if not texture_dir or not os.path.exists(texture_dir):
                QtWidgets.QMessageBox.warning(
                    self, "No Directory",
                    "请先通过Browse按钮选择一个有效的贴图目录。"
                )
                return
            
            # 支持的贴图格式
            texture_extensions = ['.jpeg', '.jpg', '.png', '.exr', '.tga', '.tex']
            
            # 收集所有贴图文件并按材质球名分组
            texture_groups = {}
            
            print(f"开始扫描贴图目录: {texture_dir}")
            
            for root, dirs, files in os.walk(texture_dir):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # 只处理支持的贴图格式
                    if file_ext in texture_extensions:
                        file_path = os.path.join(root, file)
                        texture_name = os.path.splitext(file)[0]  # 去掉扩展名
                        
                        print(f"处理贴图文件: {texture_name}")
                        
                        # 解析贴图文件名
                        # 格式：项目代码_资产类型_资产编码_模型详细命名_M_S_贴图类型_UDIM(可选)
                        parts = texture_name.split('_')
                        
                        # 检查贴图命名是否符合要求
                        if len(parts) >= 6:
                            # 检查是否包含M和S部分
                            s_index = -1
                            for i in range(len(parts)-1, -1, -1):
                                if parts[i] == "S" and i > 0 and parts[i-1] == "M":
                                    s_index = i
                                    break
                            
                            if s_index != -1 and s_index >= 4:
                                # 提取材质球名（从项目代码到S）
                                material_name = '_'.join(parts[:s_index+1])  # 包含S
                                
                                # 提取贴图类型（S后面的部分）
                                if s_index + 1 < len(parts):
                                    texture_type_part = parts[s_index+1]
                                    
                                    # 检查贴图类型是否有效
                                    valid_texture_types = ['B', 'E', 'M', 'R', 'N', 'H']
                                    if texture_type_part in valid_texture_types:
                                        # 检查是否有UDIM编号
                                        udim_part = None
                                        if s_index + 2 < len(parts):
                                            next_part = parts[s_index+2]
                                            if next_part.isdigit() and len(next_part) == 4:
                                                udim_part = next_part
                                        
                                        # 添加到分组
                                        if material_name not in texture_groups:
                                            texture_groups[material_name] = {
                                                'material_name': material_name,
                                                'textures': []
                                            }
                                        
                                        texture_info = {
                                            'file_path': file_path,
                                            'file_name': file,
                                            'texture_type': texture_type_part,
                                            'udim': udim_part,
                                            'material_name': material_name
                                        }
                                        
                                        # 从材质球名中提取模型详细命名
                                        material_parts = material_name.split('_')
                                        if len(material_parts) >= 4:
                                            texture_info['model_detail'] = material_parts[3]
                                        
                                        texture_groups[material_name]['textures'].append(texture_info)
                                        print(f"成功解析贴图: {file}, 材质球: {material_name}, 贴图类型: {texture_type_part}, UDIM: {udim_part}")
                                    else:
                                        print(f"无效的贴图类型: {file}, 类型: {texture_type_part}")
                                else:
                                    print(f"贴图文件名缺少贴图类型部分: {file}")
                            else:
                                print(f"贴图文件名不包含有效的M_S结构: {file}")
                        else:
                            print(f"贴图文件名部分不足，无法解析: {file}")
            
            print(f"找到的贴图组数量: {len(texture_groups)}")
            for material_name, group_info in texture_groups.items():
                print(f"材质球: {material_name}, 贴图数量: {len(group_info['textures'])}")
                for texture in group_info['textures']:
                    print(f"  - 贴图: {texture['file_name']}, 类型: {texture['texture_type']}, UDIM: {texture['udim']}")
            
            if not texture_groups:
                QtWidgets.QMessageBox.warning(
                    self, "No Valid Textures",
                    "在指定目录中没有找到符合命名规范的贴图文件。\n"
                    "请确保贴图文件命名符合规范：项目代码_资产类型_资产编码_模型详细命名_M_S_贴图类型[_UDIM]\n"
                    f"例如: DDD_C_ABCDEF_HeadFront_M_S_B.png\n"
                    f"或: DDD_C_ABCDEF_HeadFront_M_S_B_1001.png (带UDIM)"
                )
                return
            
            # 获取所有mesh类型的模型
            meshes = cmds.ls(type='mesh', long=True)
            if not meshes:
                QtWidgets.QMessageBox.warning(
                    self, "No Meshes",
                    "场景中没有找到mesh类型的模型。"
                )
                return
            
            created_materials = []
            created_shaders = []
            created_files = []
            created_place2d = []
            created_bump2d = []
            
            # 为每个材质球组创建材质网络
            for material_name, group_info in texture_groups.items():
                textures = group_info['textures']
                
                if not textures:
                    continue
                
                # 提取模型详细命名
                model_detail = None
                for texture in textures:
                    if 'model_detail' in texture:
                        model_detail = texture['model_detail']
                        break
                
                if not model_detail:
                    # 从材质球名中提取
                    parts = material_name.split('_')
                    if len(parts) >= 4:
                        model_detail = parts[3]
                    else:
                        model_detail = "Unknown"
                
                print(f"为材质球 {material_name} 创建材质网络，模型详细命名: {model_detail}")
                
                # 检查是否已存在同名材质球
                if not cmds.objExists(material_name):
                    # 创建aiStandardSurface材质球
                    ai_standard = cmds.shadingNode('aiStandardSurface', asShader=True, name=material_name)
                    
                    # 设置材质球的基本属性
                    cmds.setAttr(f"{material_name}.base", 1.0)  # 设置基础权重
                    cmds.setAttr(f"{material_name}.baseColor", 0.5, 0.5, 0.5, type="double3")  # 设置基础颜色为灰色
                    cmds.setAttr(f"{material_name}.metalness", 0.0)  # 设置金属度为0
                    cmds.setAttr(f"{material_name}.specularRoughness", 0.5)  # 设置粗糙度
                    
                    created_materials.append(material_name)
                    print(f"创建材质球: {material_name}")
                else:
                    ai_standard = material_name
                    print(f"使用现有材质球: {material_name}")
                
                shader_name = f"{material_name}_SG"
                if not cmds.objExists(shader_name):
                    # 创建唯一的shadingEngine节点
                    shading_group = cmds.sets(
                        renderable=True, 
                        noSurfaceShader=True, 
                        empty=True, 
                        name=shader_name
                    )
                    
                    # 唯一连接
                    cmds.connectAttr(f"{material_name}.outColor", f"{shader_name}.surfaceShader")
                    
                    created_shaders.append(shader_name)
                    print(f"创建唯一shadingEngine: {shader_name}")
                else:
                    shading_group = shader_name
                    print(f"使用现有唯一shadingEngine: {shader_name}")
                
                # 后续贴图节点创建逻辑不变...
                for texture_info in textures:
                    texture_type = texture_info['texture_type']
                    file_path = texture_info['file_path']
                    udim = texture_info['udim']
                    
                    print(f"创建贴图节点: {texture_type}, 路径: {file_path}, UDIM: {udim}")
                    
                    # 创建File节点（命名：材质球名_贴图类型_F）
                    file_node_name = f"{material_name}_{texture_type}_F"
                    
                    # 如果已存在同名File节点，添加数字后缀
                    original_file_node_name = file_node_name
                    counter = 1
                    while cmds.objExists(file_node_name):
                        file_node_name = f"{original_file_node_name}_{counter:02d}"
                        counter += 1
                    
                    file_node = cmds.shadingNode('file', asTexture=True, name=file_node_name)
                    created_files.append(file_node_name)
                    print(f"创建File节点: {file_node_name}")
                    
                    # 设置File节点的贴图路径
                    normalized_path = file_path.replace('\\', '/')
                    cmds.setAttr(f"{file_node_name}.fileTextureName", normalized_path, type="string")
                    
                    # 设置颜色空间
                    if texture_type in ['B', 'E']:
                        cmds.setAttr(f"{file_node_name}.colorSpace", "sRGB", type="string")
                    else:
                        cmds.setAttr(f"{file_node_name}.colorSpace", "Raw", type="string")
                    
                    # 设置UDIM
                    if udim:
                        # 设置UV平铺模式为UDIM (Mari)
                        cmds.setAttr(f"{file_node_name}.uvTilingMode", 3)  # 3 = UDIM (Mari)
                        # 设置U向和V向平铺
                        cmds.setAttr(f"{file_node_name}.uvCoord[0].uvTiling[0]", 1)
                        cmds.setAttr(f"{file_node_name}.uvCoord[0].uvTiling[1]", 1)
                        cmds.setAttr(f"{file_node_name}.uvCoord[0].uvOffset[0]", 0)
                        cmds.setAttr(f"{file_node_name}.uvCoord[0].uvOffset[1]", 0)
                        print(f"为File节点 {file_node_name} 设置UDIM: {udim}")
                    
                    # 创建place2dTexture节点（命名：材质球名_贴图类型_p2d）
                    place2d_name = f"{material_name}_{texture_type}_p2d"
                    
                    # 如果已存在同名place2dTexture节点，添加数字后缀
                    original_place2d_name = place2d_name
                    counter = 1
                    while cmds.objExists(place2d_name):
                        place2d_name = f"{original_place2d_name}_{counter:02d}"
                        counter += 1
                    
                    place2d_node = cmds.shadingNode('place2dTexture', asUtility=True, name=place2d_name)
                    created_place2d.append(place2d_name)
                    print(f"创建place2dTexture节点: {place2d_name}")
                    
                    # 连接place2dTexture到File节点
                    cmds.connectAttr(f"{place2d_name}.outUV", f"{file_node_name}.uvCoord")
                    cmds.connectAttr(f"{place2d_name}.outUvFilterSize", f"{file_node_name}.uvFilterSize")
                    print(f"连接 {place2d_name}.outUV -> {file_node_name}.uvCoord")
                    
                    # 对于Normal贴图，创建bump2d节点
                    if texture_type == 'N':
                        bump2d_name = f"{material_name}_{texture_type}_bp2d"
                        
                        # 如果已存在同名bump2d节点，添加数字后缀
                        original_bump2d_name = bump2d_name
                        counter = 1
                        while cmds.objExists(bump2d_name):
                            bump2d_name = f"{original_bump2d_name}_{counter:02d}"
                            counter += 1
                        
                        bump2d_node = cmds.shadingNode('bump2d', asUtility=True, name=bump2d_name)
                        created_bump2d.append(bump2d_name)
                        print(f"创建bump2d节点: {bump2d_name}")
                        
                        # 设置bump2d属性（Use as: 切线法向空间）
                        cmds.setAttr(f"{bump2d_name}.bumpInterp", 1)  # 1 = 切线空间法线
                        
                        # 连接File节点的输出Alpha到bump2d的凹凸值
                        cmds.connectAttr(f"{file_node_name}.outAlpha", f"{bump2d_name}.bumpValue")
                        print(f"连接 {file_node_name}.outAlpha -> {bump2d_name}.bumpValue")
                        
                        # 连接bump2d的输出法线到aiStandardSurface的Normal Camera
                        cmds.connectAttr(f"{bump2d_name}.outNormal", f"{material_name}.normalCamera")
                        print(f"连接 {bump2d_name}.outNormal -> {material_name}.normalCamera")
                    else:
                        # 连接File节点到aiStandardSurface的相应属性
                        if texture_type == 'B':
                            # BaseColor: 输出颜色 -> baseColor
                            cmds.connectAttr(f"{file_node_name}.outColor", f"{material_name}.baseColor")
                            print(f"连接 {file_node_name}.outColor -> {material_name}.baseColor")
                        elif texture_type == 'E':
                            # Emission: 输出颜色 -> emissionColor
                            cmds.connectAttr(f"{file_node_name}.outColor", f"{material_name}.emissionColor")
                            print(f"连接 {file_node_name}.outColor -> {material_name}.emissionColor")
                        elif texture_type == 'M':
                            # Metalness: 输出颜色R -> metalness
                            cmds.connectAttr(f"{file_node_name}.outColorR", f"{material_name}.metalness")
                            print(f"连接 {file_node_name}.outColorR -> {material_name}.metalness")
                        elif texture_type == 'R':
                            # Roughness: 输出颜色R -> specularRoughness
                            cmds.connectAttr(f"{file_node_name}.outColorR", f"{material_name}.specularRoughness")
                            print(f"连接 {file_node_name}.outColorR -> {material_name}.specularRoughness")
                        elif texture_type == 'H':
                            # Height: 输出颜色R -> aiDisplacement
                            print(f"Height贴图节点已创建，但需要额外的displacement节点连接")
                        else:
                            print(f"未知的贴图类型: {texture_type}")
                
                # 查找使用该材质球的模型并指定材质
                models_assigned = 0
                for mesh in meshes:
                    try:
                        # 获取mesh的父变换节点
                        parent = cmds.listRelatives(mesh, parent=True, fullPath=True)
                        if not parent:
                            continue
                        
                        transform_node = parent[0]
                        mesh_name = transform_node.split('|')[-1]  # 获取短名称
                        
                        # 检查模型名称是否包含材质球名中的模型详细命名
                        if model_detail and model_detail in mesh_name:
                            # 将模型指定到唯一的shadingEngine
                            cmds.sets(mesh, edit=True, forceElement=shader_name)
                            models_assigned += 1
                            print(f"为模型 {mesh_name} 指定材质 {shader_name}")
                            
                    except Exception as mesh_error:
                        print(f"指定材质时出错 {mesh}: {str(mesh_error)}")
                        continue
                
                print(f"为 {models_assigned} 个模型指定了材质 {shader_name}")
            
            # 显示创建结果
            message = f"材质创建完成！\n\n"
            
            if created_materials:
                message += f"创建了 {len(created_materials)} 个材质球：\n"
                for mat in created_materials:
                    message += f"  - {mat}\n"
            
            if created_shaders:
                message += f"\n创建了 {len(created_shaders)} 个 shadingEngine 节点：\n"
                for shader in created_shaders:
                    message += f"  - {shader}\n"
            
            if created_files:
                message += f"\n创建了 {len(created_files)} 个 File 节点：\n"
                for file_node in created_files[:10]:  # 只显示前10个
                    message += f"  - {file_node}\n"
                if len(created_files) > 10:
                    message += f"  ... 还有 {len(created_files) - 10} 个\n"
            
            if created_place2d:
                message += f"\n创建了 {len(created_place2d)} 个 place2dTexture 节点：\n"
                for place2d in created_place2d[:10]:  # 只显示前10个
                    message += f"  - {place2d}\n"
                if len(created_place2d) > 10:
                    message += f"  ... 还有 {len(created_place2d) - 10} 个\n"
            
            if created_bump2d:
                message += f"\n创建了 {len(created_bump2d)} 个 bump2d 节点：\n"
                for bump2d in created_bump2d:
                    message += f"  - {bump2d}\n"
            
            message += f"\n所有相关模型已指定材质。"
            
            QtWidgets.QMessageBox.information(
                self, "Material Creation Complete",
                message
            )
            
        except Exception as e:
            import traceback
            QtWidgets.QMessageBox.warning(
                self, "Material Creation Error",
                f"创建材质过程中出错：{str(e)}\n\n详细错误：{traceback.format_exc()}"
            )

    def auto_import_all(self):
        """自动导入所有贴图并创建材质网络，同时导入对应的模型文件"""
        try:
            # 获取Browse文件夹路径
            directory = self.file_path_edit.text()
            if not directory or not os.path.exists(directory):
                QtWidgets.QMessageBox.warning(
                    self, "No Directory",
                    "请先通过Browse按钮选择一个有效的贴图目录。"
                )
                return
            
            # 获取当前Maya文件名
            current_file = cmds.file(query=True, sceneName=True)
            if not current_file:
                QtWidgets.QMessageBox.warning(
                    self, "No File",
                    "Maya场景文件未保存。请先保存文件以获取文件名信息。"
                )
                return
            
            # 从Maya文件名中提取信息
            file_name = os.path.basename(current_file)
            base_name = os.path.splitext(file_name)[0]
            
            # 解析Maya文件名（格式：项目代码_资产类型_资产编码_阶段_公司代码_人员代码_版本）
            parts = base_name.split('_')
            if len(parts) != 7:
                QtWidgets.QMessageBox.warning(
                    self, "Invalid File Name",
                    "Maya文件名不符合命名规范。\n"
                    "格式应为：项目代码_资产类型_资产编码_阶段_公司代码_人员代码_版本\n"
                    f"当前文件名：{file_name}"
                )
                return
            
            project_code = parts[0]      # 项目代码
            asset_type = parts[1]        # 资产类型 (C/S/O)
            asset_code = parts[2]        # 资产编码
            
            # 扫描目录中的贴图文件并分组
            texture_groups = self.scan_textures_for_auto_import(directory, project_code, asset_type, asset_code)
            
            if not texture_groups:
                QtWidgets.QMessageBox.warning(
                    self, "No Valid Textures",
                    "在指定目录中没有找到符合命名规范的贴图文件。\n"
                    "请确保贴图文件命名符合规范：项目代码_资产类型_资产编码_模型详细命名_M_S_贴图类型[_UDIM]\n"
                    f"例如: {project_code}_{asset_type}_{asset_code}_RightHand_M_S_B.png"
                )
                return
            
            # 先导入对应的模型文件
            imported_models = []
            for material_name, texture_info in texture_groups.items():
                model_detail = texture_info.get('model_detail', 'Unknown')
                
                # 查找并导入对应的模型文件
                model_files = self.find_model_files(directory, project_code, asset_type, asset_code, model_detail)
                
                if model_files:
                    for model_file in model_files:
                        imported_model = self.import_model_file(model_file)
                        if imported_model:
                            imported_models.append((model_detail, imported_model))
                            print(f"导入模型: {model_file}, 模型详细命名: {model_detail}")
                else:
                    print(f"未找到与材质球 {material_name} 对应的模型文件")
            
            # 为每个贴图组创建材质网络
            created_count = 0
            for material_name, texture_info in texture_groups.items():
                if self.create_material_network(material_name, texture_info):
                    created_count += 1
            
            # 将创建的材质指定给导入的模型
            materials_assigned = self.assign_materials_to_imported_models(imported_models, texture_groups)
            
            # 显示结果
            if created_count > 0:
                message = f"自动导入完成！\n\n"
                message += f"创建了 {created_count} 个材质网络。\n"
                message += f"导入了 {len(imported_models)} 个模型文件。\n"
                message += f"为 {materials_assigned} 个模型指定了材质。\n\n"
                message += f"每个材质网络包括：\n"
                message += f"- 1个aiStandardSurface材质球\n"
                message += f"- 1个shadingEngine节点\n"
                message += f"- 对应的File节点和place2dTexture节点"
                
                QtWidgets.QMessageBox.information(
                    self, "Auto Import Complete",
                    message
                )
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Auto Import Failed",
                    "自动导入失败，无法创建材质网络。"
                )
                    
        except Exception as e:
            import traceback
            QtWidgets.QMessageBox.warning(
                self, "Auto Import Error",
                f"自动导入过程中出错：{str(e)}\n\n详细错误：{traceback.format_exc()}"
            )

    def find_model_files(self, directory, project_code, asset_type, asset_code, model_detail):
        """查找与材质对应的模型文件"""
        model_files = []
        
        # 支持的模型格式
        model_extensions = ['.fbx', '.obj', '.ma', '.mb']
        
        print(f"查找模型文件: 项目={project_code}, 资产类型={asset_type}, 资产编码={asset_code}, 模型详细命名={model_detail}")
        
        # 遍历目录中的文件
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                
                # 只处理支持的模型格式
                if file_ext in model_extensions:
                    file_path = os.path.join(root, file)
                    model_name = os.path.splitext(file)[0]  # 去掉扩展名
                    
                    # 解析模型文件名
                    # 格式：项目代码_资产类型_资产编码_模型详细命名_M_序号(可选)
                    parts = model_name.split('_')
                    
                    # 检查模型命名是否符合要求
                    if len(parts) >= 4:
                        # 检查项目、资产类型、资产编码是否匹配
                        if (parts[0] == project_code and 
                            parts[1] == asset_type and 
                            parts[2] == asset_code):
                            
                            # 检查模型详细命名是否匹配
                            model_detail_part = parts[3]
                            
                            # 检查阶段是否为M（模型阶段）
                            if len(parts) > 4 and parts[4] == 'M':
                                if model_detail in model_detail_part:
                                    model_files.append(file_path)
                                    print(f"找到匹配的模型文件: {file}")
        
        return model_files

    def import_model_file(self, model_file):
        """导入模型文件到Maya场景"""
        try:
            file_ext = os.path.splitext(model_file)[1].lower()
            
            if file_ext == '.fbx':
                # 确保FBX插件已加载
                if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
                    cmds.loadPlugin('fbxmaya')
                
                # 导入FBX文件
                cmds.file(
                    model_file,
                    i=True,  # 导入
                    type='FBX',
                    ignoreVersion=True,
                    options="v=0;",
                    pr=True
                )
                
            elif file_ext == '.obj':
                # 确保OBJ插件已加载
                if not cmds.pluginInfo('objExport', query=True, loaded=True):
                    cmds.loadPlugin('objExport')
                
                # 导入OBJ文件
                cmds.file(
                    model_file,
                    i=True,  # 导入
                    type='OBJ',
                    ignoreVersion=True,
                    options="v=0;",
                    pr=True
                )
            
            elif file_ext in ['.ma', '.mb']:
                # 导入Maya文件
                cmds.file(
                    model_file,
                    i=True,  # 导入
                    ignoreVersion=True,
                    mergeNamespacesOnClash=False,
                    namespace=':',
                    options='v=0;'
                )
            
            # 获取最近导入的模型
            imported_nodes = cmds.ls(assemblies=True)
            if imported_nodes:
                return imported_nodes[-1]  # 返回最后一个导入的节点
            
            return None
            
        except Exception as e:
            print(f"导入模型文件失败 {model_file}: {str(e)}")
            return None

    def assign_materials_to_imported_models(self, imported_models, texture_groups):
        """将创建的材质指定给导入的模型"""
        materials_assigned = 0
        
        # 遍历所有导入的模型
        for model_detail, model_node in imported_models:
            # 找到与模型详细命名匹配的材质球
            for material_name, texture_info in texture_groups.items():
                group_model_detail = texture_info.get('model_detail', 'Unknown')
                
                if model_detail in group_model_detail or group_model_detail in model_detail:
                    # 获取shadingEngine名称
                    shader_name = f"{material_name}_SG"
                    
                    if cmds.objExists(shader_name):
                        # 获取模型的所有mesh
                        model_meshes = []
                        
                        # 如果是transform节点，获取其下的所有mesh
                        if cmds.objectType(model_node) == 'transform':
                            descendants = cmds.listRelatives(model_node, allDescendents=True, type='mesh')
                            if descendants:
                                model_meshes.extend(descendants)
                        
                        # 如果是mesh节点，直接使用
                        elif cmds.objectType(model_node) == 'mesh':
                            model_meshes.append(model_node)
                        
                        # 为每个mesh指定材质
                        for mesh in model_meshes:
                            try:
                                cmds.sets(mesh, edit=True, forceElement=shader_name)
                                materials_assigned += 1
                                print(f"为模型 {model_detail} 的mesh {mesh} 指定材质 {shader_name}")
                            except Exception as e:
                                print(f"指定材质失败 {mesh} -> {shader_name}: {str(e)}")
        
        return materials_assigned

    def scan_textures_for_auto_import(self, directory, project_code, asset_type, asset_code):
        """扫描贴图文件并按材质球名分组"""
        texture_groups = {}
        
        # 支持的贴图格式
        texture_extensions = ['.jpeg', '.jpg', '.png', '.exr', '.tga']
        
        print(f"扫描贴图目录: {directory}")
        print(f"项目代码: {project_code}, 资产类型: {asset_type}, 资产编码: {asset_code}")
        
        # 遍历目录中的文件
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                
                # 只处理支持的贴图格式
                if file_ext in texture_extensions:
                    file_path = os.path.join(root, file)
                    texture_name = os.path.splitext(file)[0]  # 去掉扩展名
                    
                    # 解析贴图文件名
                    # 格式：项目代码_资产类型_资产编码_模型详细命名_M_S_贴图类型[_UDIM]
                    parts = texture_name.split('_')
                    
                    # 检查贴图命名是否符合要求
                    if len(parts) >= 7:
                        # 检查项目、资产类型、资产编码是否匹配
                        if (parts[0] == project_code and 
                            parts[1] == asset_type and 
                            parts[2] == asset_code):
                            
                            # 检查是否包含M和S部分
                            s_index = -1
                            for i in range(len(parts)-1, -1, -1):
                                if parts[i] == "S" and i > 0 and parts[i-1] == "M":
                                    s_index = i
                                    break
                            
                            if s_index != -1 and s_index >= 4:
                                # 提取材质球名（从项目代码到S）
                                material_name = '_'.join(parts[:s_index+1])  # 包含S
                                
                                # 提取贴图类型（S后面的部分）
                                if s_index + 1 < len(parts):
                                    texture_type_part = parts[s_index+1]
                                    
                                    # 检查贴图类型是否有效
                                    valid_texture_types = ['B', 'E', 'M', 'R', 'N', 'H']
                                    if texture_type_part in valid_texture_types:
                                        # 提取模型详细命名
                                        model_detail = parts[3] if len(parts) > 3 else "Unknown"
                                        
                                        # 检查是否有UDIM编号
                                        udim_part = None
                                        if s_index + 2 < len(parts):
                                            next_part = parts[s_index+2]
                                            if next_part.isdigit() and len(next_part) == 4:
                                                udim_part = next_part
                                        
                                        # 添加到分组
                                        if material_name not in texture_groups:
                                            texture_groups[material_name] = {
                                                'material_name': material_name,
                                                'model_detail': model_detail,
                                                'textures': []
                                            }
                                        
                                        texture_info = {
                                            'file_path': file_path,
                                            'file_name': file,
                                            'texture_type': texture_type_part,
                                            'udim': udim_part
                                        }
                                        
                                        texture_groups[material_name]['textures'].append(texture_info)
                                        print(f"找到贴图: {file}, 材质球: {material_name}, 类型: {texture_type_part}, UDIM: {udim_part}")
        
        print(f"总共找到 {len(texture_groups)} 个贴图组")
        return texture_groups

    def create_material_network(self, material_name, texture_info):
        """为指定的贴图组创建材质网络，并清理错误的shadingEngine节点"""
        try:
            textures = texture_info['textures']
            model_detail = texture_info.get('model_detail', 'Unknown')
            
            print(f"为材质球 {material_name} 创建材质网络，模型详细命名: {model_detail}")
            
            # 1. 检查是否已存在同名材质球
            if not cmds.objExists(material_name):
                # 创建aiStandardSurface材质球
                ai_standard = cmds.shadingNode('aiStandardSurface', asShader=True, name=material_name)
                
                # 设置材质球的基本属性
                cmds.setAttr(f"{material_name}.base", 1.0)  # 设置基础权重
                cmds.setAttr(f"{material_name}.baseColor", 0.5, 0.5, 0.5, type="double3")  # 设置基础颜色为灰色
                cmds.setAttr(f"{material_name}.metalness", 0.0)  # 设置金属度为0
                cmds.setAttr(f"{material_name}.specularRoughness", 0.5)  # 设置粗糙度
                
                print(f"创建材质球: {material_name}")
            else:
                ai_standard = material_name
                print(f"使用现有材质球: {material_name}")
            
            # 2. 检查是否已存在同名shadingEngine - 修复这里的逻辑
            shader_name = f"{material_name}_SG"
            
            # 先检查是否已存在正确的shadingEngine节点
            if cmds.objExists(shader_name):
                shading_group = shader_name
                print(f"使用现有shadingEngine: {shader_name}")
            else:
                # 检查是否有其他可能错误的shadingEngine节点（如_MSG结尾的）
                possible_wrong_names = [
                    f"{material_name}_MSG",  # 可能的错误命名
                    f"{material_name}_M_SG",  # 另一个可能的错误命名
                ]
                
                # 删除任何错误的shadingEngine节点
                for wrong_name in possible_wrong_names:
                    if cmds.objExists(wrong_name):
                        try:
                            cmds.delete(wrong_name)
                            print(f"删除错误的shadingEngine节点: {wrong_name}")
                        except Exception as e:
                            print(f"删除错误节点失败 {wrong_name}: {str(e)}")
                
                # 创建正确的shadingEngine节点
                shading_group = cmds.sets(
                    renderable=True, 
                    noSurfaceShader=True, 
                    empty=True, 
                    name=shader_name
                )
                
                # 连接材质球的outColor到shadingEngine的surfaceShader
                cmds.connectAttr(f"{material_name}.outColor", f"{shader_name}.surfaceShader")
                
                print(f"创建shadingEngine: {shader_name}")
            
            # 3. 为每个贴图创建节点并连接
            for texture in textures:
                texture_type = texture['texture_type']
                file_path = texture['file_path']
                udim = texture['udim']
                
                print(f"处理贴图: {texture_type}, 路径: {file_path}, UDIM: {udim}")
                
                # 根据贴图类型创建不同的节点和连接
                if texture_type == 'B':
                    self.create_basecolor_nodes(material_name, texture_type, file_path, udim)
                elif texture_type == 'E':
                    self.create_emission_nodes(material_name, texture_type, file_path, udim)
                elif texture_type == 'M':
                    self.create_metalness_nodes(material_name, texture_type, file_path, udim)
                elif texture_type == 'R':
                    self.create_roughness_nodes(material_name, texture_type, file_path, udim)
                elif texture_type == 'N':
                    self.create_normal_nodes(material_name, texture_type, file_path, udim)
                elif texture_type == 'H':
                    self.create_height_nodes(material_name, texture_type, file_path, udim)
            
            # 4. 将材质指定给对应的模型（如果存在）
            # 注意：这个步骤现在在 assign_materials_to_imported_models 函数中统一处理
            # 这里我们只打印信息，不实际指定材质
            print(f"材质球 {material_name} 已创建，等待在导入模型后指定")
            
            # 5. 清理所有以_MSG结尾的错误shadingEngine节点
            print("开始清理错误的shadingEngine节点...")
            
            # 获取所有shadingEngine节点
            all_shaders = cmds.ls(type='shadingEngine')
            
            # 遍历并删除以_MSG结尾的节点
            nodes_deleted = 0
            for shader in all_shaders:
                if shader.endswith('_MSG'):
                    try:
                        cmds.delete(shader)
                        print(f"已删除节点: {shader}")
                        nodes_deleted += 1
                    except Exception as e:
                        print(f"删除节点 {shader} 失败: {str(e)}")
            
            print(f"清理完成，共删除 {nodes_deleted} 个错误节点")
            
            return True
                
        except Exception as e:
            print(f"创建材质网络失败 {material_name}: {str(e)}")
            return False
        
    def create_basecolor_nodes(self, material_name, texture_type, file_path, udim):
        """创建BaseColor贴图节点"""
        try:
            # 创建File节点
            file_node_name = f"{material_name}_{texture_type}_F"
            file_node = self.create_file_node(file_node_name, file_path, udim, is_srgb=True)
            
            # 创建place2dTexture节点
            place2d_name = f"{material_name}_{texture_type}_p2d"
            self.create_place2d_node(place2d_name, file_node_name)
            
            # 连接File节点的输出颜色到aiStandardSurface的BaseColor
            cmds.connectAttr(f"{file_node_name}.outColor", f"{material_name}.baseColor")
            print(f"连接 {file_node_name}.outColor -> {material_name}.baseColor")
            
            return True
        except Exception as e:
            print(f"创建BaseColor节点失败: {str(e)}")
            return False

    def create_emission_nodes(self, material_name, texture_type, file_path, udim):
        """创建Emission贴图节点"""
        try:
            # 创建File节点
            file_node_name = f"{material_name}_{texture_type}_F"
            file_node = self.create_file_node(file_node_name, file_path, udim, is_srgb=True)
            
            # 创建place2dTexture节点
            place2d_name = f"{material_name}_{texture_type}_p2d"
            self.create_place2d_node(place2d_name, file_node_name)
            
            # 连接File节点的输出颜色到aiStandardSurface的Emission Color
            cmds.connectAttr(f"{file_node_name}.outColor", f"{material_name}.emissionColor")
            print(f"连接 {file_node_name}.outColor -> {material_name}.emissionColor")
            
            return True
        except Exception as e:
            print(f"创建Emission节点失败: {str(e)}")
            return False

    def create_metalness_nodes(self, material_name, texture_type, file_path, udim):
        """创建Metalness贴图节点"""
        try:
            # 创建File节点
            file_node_name = f"{material_name}_{texture_type}_F"
            file_node = self.create_file_node(file_node_name, file_path, udim, is_srgb=False)
            
            # 创建place2dTexture节点
            place2d_name = f"{material_name}_{texture_type}_p2d"
            self.create_place2d_node(place2d_name, file_node_name)
            
            # 连接File节点的输出颜色R到aiStandardSurface的Metalness
            cmds.connectAttr(f"{file_node_name}.outColorR", f"{material_name}.metalness")
            print(f"连接 {file_node_name}.outColorR -> {material_name}.metalness")
            
            return True
        except Exception as e:
            print(f"创建Metalness节点失败: {str(e)}")
            return False

    def create_roughness_nodes(self, material_name, texture_type, file_path, udim):
        """创建Roughness贴图节点"""
        try:
            # 创建File节点
            file_node_name = f"{material_name}_{texture_type}_F"
            file_node = self.create_file_node(file_node_name, file_path, udim, is_srgb=False)
            
            # 创建place2dTexture节点
            place2d_name = f"{material_name}_{texture_type}_p2d"
            self.create_place2d_node(place2d_name, file_node_name)
            
            # 连接File节点的输出颜色R到aiStandardSurface的Specular Roughness
            cmds.connectAttr(f"{file_node_name}.outColorR", f"{material_name}.specularRoughness")
            print(f"连接 {file_node_name}.outColorR -> {material_name}.specularRoughness")
            
            return True
        except Exception as e:
            print(f"创建Roughness节点失败: {str(e)}")
            return False

    def create_normal_nodes(self, material_name, texture_type, file_path, udim):
        """创建Normal贴图节点"""
        try:
            # 创建File节点
            file_node_name = f"{material_name}_{texture_type}_F"
            file_node = self.create_file_node(file_node_name, file_path, udim, is_srgb=False)
            
            # 创建place2dTexture节点
            place2d_name = f"{material_name}_{texture_type}_p2d"
            self.create_place2d_node(place2d_name, file_node_name)
            
            # 创建bump2d节点
            bump2d_name = f"{material_name}_{texture_type}_bp2d"
            
            # 如果已存在同名bump2d节点，添加数字后缀
            original_bump2d_name = bump2d_name
            counter = 1
            while cmds.objExists(bump2d_name):
                bump2d_name = f"{original_bump2d_name}_{counter:02d}"
                counter += 1
            
            bump2d_node = cmds.shadingNode('bump2d', asUtility=True, name=bump2d_name)
            
            # 设置bump2d属性（Use as: 切线法向空间）
            cmds.setAttr(f"{bump2d_name}.bumpInterp", 1)  # 1 = 切线空间法线
            
            # 连接File节点的输出Alpha到bump2d的凹凸值
            cmds.connectAttr(f"{file_node_name}.outAlpha", f"{bump2d_name}.bumpValue")
            print(f"连接 {file_node_name}.outAlpha -> {bump2d_name}.bumpValue")
            
            # 连接bump2d的输出法线到aiStandardSurface的Normal Camera
            cmds.connectAttr(f"{bump2d_name}.outNormal", f"{material_name}.normalCamera")
            print(f"连接 {bump2d_name}.outNormal -> {material_name}.normalCamera")
            
            return True
        except Exception as e:
            print(f"创建Normal节点失败: {str(e)}")
            return False

    def create_height_nodes(self, material_name, texture_type, file_path, udim):
        """创建Height贴图节点"""
        try:
            # 创建File节点
            file_node_name = f"{material_name}_{texture_type}_F"
            file_node = self.create_file_node(file_node_name, file_path, udim, is_srgb=False)
            
            # 创建place2dTexture节点
            place2d_name = f"{material_name}_{texture_type}_p2d"
            self.create_place2d_node(place2d_name, file_node_name)
            
            # 注意：Height贴图节点已创建，但需要额外的displacement节点连接
            print(f"Height贴图节点已创建，但需要额外的displacement节点连接")
            
            return True
        except Exception as e:
            print(f"创建Height节点失败: {str(e)}")
            return False

    def create_file_node(self, file_node_name, file_path, udim, is_srgb=True):
        """创建File节点"""
        try:
            # 如果已存在同名File节点，添加数字后缀
            original_file_node_name = file_node_name
            counter = 1
            while cmds.objExists(file_node_name):
                file_node_name = f"{original_file_node_name}_{counter:02d}"
                counter += 1
            
            file_node = cmds.shadingNode('file', asTexture=True, name=file_node_name)
            
            # 设置File节点的贴图路径
            normalized_path = file_path.replace('\\', '/')
            cmds.setAttr(f"{file_node_name}.fileTextureName", normalized_path, type="string")
            
            # 设置颜色空间
            if is_srgb:
                cmds.setAttr(f"{file_node_name}.colorSpace", "sRGB", type="string")
            else:
                cmds.setAttr(f"{file_node_name}.colorSpace", "Raw", type="string")
            
            # 设置UDIM
            if udim:
                # 设置UV平铺模式为UDIM (Mari)
                cmds.setAttr(f"{file_node_name}.uvTilingMode", 3)  # 3 = UDIM (Mari)
                # 设置U向和V向平铺
                cmds.setAttr(f"{file_node_name}.uvCoord[0].uvTiling[0]", 1)
                cmds.setAttr(f"{file_node_name}.uvCoord[0].uvTiling[1]", 1)
                cmds.setAttr(f"{file_node_name}.uvCoord[0].uvOffset[0]", 0)
                cmds.setAttr(f"{file_node_name}.uvCoord[0].uvOffset[1]", 0)
                print(f"为File节点 {file_node_name} 设置UDIM: {udim}")
            
            print(f"创建File节点: {file_node_name}")
            return file_node_name
            
        except Exception as e:
            print(f"创建File节点失败: {str(e)}")
            return None

    def create_place2d_node(self, place2d_name, file_node_name):
        """创建place2dTexture节点并连接到File节点"""
        try:
            # 如果已存在同名place2dTexture节点，添加数字后缀
            original_place2d_name = place2d_name
            counter = 1
            while cmds.objExists(place2d_name):
                place2d_name = f"{original_place2d_name}_{counter:02d}"
                counter += 1
            
            place2d_node = cmds.shadingNode('place2dTexture', asUtility=True, name=place2d_name)
            
            # 连接place2dTexture到File节点
            cmds.connectAttr(f"{place2d_name}.outUV", f"{file_node_name}.uvCoord")
            cmds.connectAttr(f"{place2d_name}.outUvFilterSize", f"{file_node_name}.uvFilterSize")
            print(f"连接 {place2d_name}.outUV -> {file_node_name}.uvCoord")
            
            print(f"创建place2dTexture节点: {place2d_name}")
            return place2d_name
            
        except Exception as e:
            print(f"创建place2dTexture节点失败: {str(e)}")
            return None

    def assign_material_to_models(self, material_name, model_detail):
        """将材质指定给对应的模型"""
        try:
            # 获取所有mesh类型的模型
            meshes = cmds.ls(type='mesh', long=True)
            if not meshes:
                print("场景中没有找到mesh类型的模型")
                return
            
            # 正确的shader名称
            shader_name = f"{material_name}_SG"
            
            if not cmds.objExists(shader_name):
                print(f"Shader节点不存在: {shader_name}")
                return
            
            models_assigned = 0
            
            for mesh in meshes:
                try:
                    # 获取mesh的父变换节点
                    parent = cmds.listRelatives(mesh, parent=True, fullPath=True)
                    if not parent:
                        continue
                    
                    transform_node = parent[0]
                    mesh_name = transform_node.split('|')[-1]  # 获取短名称
                    
                    # 检查模型名称是否包含材质球名中的模型详细命名
                    if model_detail and model_detail in mesh_name:
                        # 将模型指定到shadingEngine
                        cmds.sets(mesh, edit=True, forceElement=shader_name)
                        models_assigned += 1
                        print(f"为模型 {mesh_name} 指定材质 {shader_name}")
                        
                except Exception as mesh_error:
                    print(f"指定材质时出错 {mesh}: {str(mesh_error)}")
                    continue
            
            print(f"为 {models_assigned} 个模型指定了材质 {shader_name}")
            
        except Exception as e:
            print(f"指定材质给模型时出错: {str(e)}")

    def export_models_and_textures(self):
        """自动导出场景中的模型和贴图到Browse文件夹"""
        try:
            # 检查是否选择了导出目录
            export_dir = self.file_path_edit.text()
            if not export_dir or not os.path.exists(export_dir):
                QtWidgets.QMessageBox.warning(
                    self, "Invalid Directory",
                    "Please select a valid export directory in Browse."
                )
                return
            
            # 选择导出格式
            format_choice, ok = QtWidgets.QInputDialog.getItem(
                self, "Export Format",
                "Choose export format:",
                ["fbx", "obj"], 0, False
            )
            
            if not ok:
                return  # 用户取消
            
            # 检查是否有模型可以导出
            if not cmds.ls(type='mesh'):
                QtWidgets.QMessageBox.warning(
                    self, "No Models Found",
                    "No mesh models found in the current scene."
                )
                return
            
            # 获取所有mesh
            all_meshes = cmds.ls(type='mesh', long=True)
            
            # 按模型分组（基于模型详细命名）
            model_groups = {}
            
            for mesh in all_meshes:
                try:
                    # 获取mesh的父变换节点
                    parent = cmds.listRelatives(mesh, parent=True, fullPath=True)
                    if not parent:
                        continue
                    
                    transform_node = parent[0]
                    model_name = transform_node.split('|')[-1]  # 获取模型名称
                    
                    # 解析模型名称
                    # 格式: 项目代码_资产类型_资产编码_模型详细命名_M
                    parts = model_name.split('_')
                    
                    if len(parts) >= 4:  # 至少需要4个部分
                        # 提取模型详细命名
                        if len(parts) >= 5 and parts[4] == 'M':
                            # 格式: 项目代码_资产类型_资产编码_模型详细命名_M
                            project_code = parts[0]
                            asset_type = parts[1]
                            asset_code = parts[2]
                            model_detail = parts[3]
                            
                            group_key = f"{project_code}_{asset_type}_{asset_code}_{model_detail}_M"
                            
                            if group_key not in model_groups:
                                model_groups[group_key] = {
                                    'project_code': project_code,
                                    'asset_type': asset_type,
                                    'asset_code': asset_code,
                                    'model_detail': model_detail,
                                    'models': [],
                                    'has_textures': False,
                                    'textures': set()
                                }
                            
                            # 检查模型是否有贴图
                            materials = self.get_materials_for_mesh(mesh)
                            has_textures = False
                            model_textures = set()
                            
                            for material in materials:
                                material_textures = self.get_textures_from_material(material)
                                if material_textures:
                                    has_textures = True
                                    model_textures.update(material_textures)
                            
                            model_groups[group_key]['models'].append({
                                'transform': transform_node,
                                'name': model_name,
                                'has_textures': has_textures
                            })
                            
                            # 如果模型有贴图，更新分组信息
                            if has_textures:
                                model_groups[group_key]['has_textures'] = True
                                model_groups[group_key]['textures'].update(model_textures)
            
                except Exception as e:
                    print(f"Error processing mesh {mesh}: {str(e)}")
                    continue
            
            if not model_groups:
                QtWidgets.QMessageBox.warning(
                    self, "No Models Found",
                    "No models with valid naming convention found in the current scene."
                )
                return
            
            # 导出每个模型组
            exported_count = 0
            
            for group_key, group_info in model_groups.items():
                try:
                    # 创建文件夹
                    group_folder = os.path.join(export_dir, group_key)
                    os.makedirs(group_folder, exist_ok=True)
                    
                    # 导出模型
                    model_exported = False
                    for model_info in group_info['models']:
                        try:
                            # 选择当前模型
                            cmds.select(model_info['transform'], replace=True)
                            
                            # 设置导出文件名
                            export_filename = f"{model_info['name']}.{format_choice}"
                            export_path = os.path.join(group_folder, export_filename)
                            
                            # 根据格式导出
                            if format_choice == 'fbx':
                                # 确保FBX插件已加载
                                if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
                                    cmds.loadPlugin('fbxmaya')
                                
                                cmds.file(
                                    export_path,
                                    force=True,
                                    options="v=0;",
                                    typ="FBX export",
                                    pr=True,
                                    es=True
                                )
                            
                            elif format_choice == 'obj':
                                # 确保OBJ插件已加载
                                if not cmds.pluginInfo('objExport', query=True, loaded=True):
                                    cmds.loadPlugin('objExport')
                                
                                cmds.file(
                                    export_path,
                                    force=True,
                                    options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1",
                                    typ="OBJexport",
                                    pr=True,
                                    es=True
                                )
                            
                            model_exported = True
                            exported_count += 1
                            print(f"Exported model: {model_info['name']} to {export_path}")
                            
                        except Exception as e:
                            print(f"Error exporting model {model_info['name']}: {str(e)}")
                            continue
                    
                    # 如果模型组有贴图，导出贴图
                    if group_info['has_textures'] and group_info['textures']:
                        texture_count = self.copy_textures_to_folder(
                            list(group_info['textures']), 
                            group_folder
                        )
                        print(f"Copied {texture_count} textures to {group_folder}")
                    
                    # 显示导出信息
                    export_info = f"Group: {group_key}\n"
                    export_info += f"Folder: {group_folder}\n"
                    export_info += f"Models exported: {len(group_info['models'])}\n"
                    if group_info['has_textures']:
                        export_info += f"Textures exported: {len(group_info['textures'])}\n"
                    else:
                        export_info += "No textures (only aiStandardSurface material)\n"
                    
                    print(export_info)
                
                except Exception as e:
                    print(f"Error exporting group {group_key}: {str(e)}")
                    continue
            
            # 清除选择
            cmds.select(clear=True)
            
            # 显示结果
            message = f"Auto Export Complete!\n\n"
            message += f"Exported {exported_count} model(s) to {len(model_groups)} folder(s).\n\n"
            
            for group_key, group_info in model_groups.items():
                message += f"Folder: {group_key}\n"
                message += f"  Models: {len(group_info['models'])}\n"
                if group_info['has_textures']:
                    message += f"  Textures: {len(group_info['textures'])}\n"
                else:
                    message += f"  Textures: None (aiStandardSurface only)\n"
                message += "\n"
            
            QtWidgets.QMessageBox.information(
                self, "Export Successful",
                message
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Export Error",
                f"Failed to export models and textures:\n{str(e)}"
            )

    def get_materials_for_mesh(self, mesh):
        """获取网格使用的所有材质"""
        materials = []
        try:
            # 获取分配给网格的shadingEngine
            shading_engines = cmds.listConnections(mesh, type='shadingEngine')
            if shading_engines:
                for sg in shading_engines:
                    # 获取shadingEngine连接的材质
                    shaders = cmds.listConnections(f"{sg}.surfaceShader", destination=False)
                    if shaders:
                        materials.extend(shaders)
        except Exception as e:
            print(f"Error getting materials for mesh {mesh}: {str(e)}")
        return materials

    def get_textures_from_material(self, material):
        """从材质获取所有贴图文件路径"""
        textures = []
        try:
            # 获取材质的所有file节点
            file_nodes = cmds.listConnections(material, type='file')
            if file_nodes:
                for file_node in file_nodes:
                    # 获取贴图文件路径
                    texture_path = cmds.getAttr(f"{file_node}.fileTextureName")
                    if texture_path and os.path.exists(texture_path):
                        # 规范化路径
                        normalized_path = os.path.normpath(texture_path)
                        textures.append(normalized_path)
            
            # 新增：获取连接到材质的bump2d节点
            bump2d_nodes = cmds.listConnections(material, type='bump2d')
            if bump2d_nodes:
                for bump2d_node in bump2d_nodes:
                    # 获取连接到bump2d节点的file节点
                    bump_connections = cmds.listConnections(
                        f"{bump2d_node}.bumpValue", 
                        source=True, 
                        destination=False, 
                        type='file'
                    )
                    if bump_connections:
                        for file_node in bump_connections:
                            # 获取贴图文件路径
                            texture_path = cmds.getAttr(f"{file_node}.fileTextureName")
                            if texture_path and os.path.exists(texture_path):
                                # 规范化路径
                                normalized_path = os.path.normpath(texture_path)
                                textures.append(normalized_path)
            
            return textures
        except Exception as e:
            print(f"Error getting textures from material {material}: {str(e)}")
            return textures

    def copy_textures_to_folder(self, textures, target_folder):
        """复制贴图文件到目标文件夹"""
        copied_count = 0
        for texture_path in textures:
            try:
                # 获取文件名
                texture_name = os.path.basename(texture_path)
                destination_path = os.path.join(target_folder, texture_name)
                
                # 如果目标文件已存在，询问是否覆盖
                if os.path.exists(destination_path):
                    reply = QtWidgets.QMessageBox.question(
                        self, "File Exists",
                        f"Texture file '{texture_name}' already exists in export directory.\n"
                        "Do you want to overwrite it?",
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.No
                    )
                    
                    if reply == QtWidgets.QMessageBox.No:
                        # 添加后缀避免冲突
                        base_name, ext = os.path.splitext(texture_name)
                        counter = 1
                        while os.path.exists(destination_path):
                            new_name = f"{base_name}_{counter:02d}{ext}"
                            destination_path = os.path.join(target_folder, new_name)
                            counter += 1
                
                # 复制文件
                import shutil
                shutil.copy2(texture_path, destination_path)
                copied_count += 1
                print(f"Copied texture: {texture_name}")
                
            except Exception as e:
                print(f"Error copying texture {texture_path}: {str(e)}")
        
        return copied_count

    def get_all_textures(self):
        """获取场景中所有材质使用的贴图文件路径"""
        all_textures = set()  # 使用set去重
        
        try:
            # 获取所有材质
            all_materials = cmds.ls(mat=True)
            
            # 获取所有file节点
            file_nodes = cmds.ls(type='file')
            
            for file_node in file_nodes:
                try:
                    # 获取贴图文件路径
                    texture_path = cmds.getAttr(f"{file_node}.fileTextureName")
                    if texture_path and os.path.exists(texture_path):
                        # 规范化路径
                        normalized_path = os.path.normpath(texture_path)
                        all_textures.add(normalized_path)
                except Exception as e:
                    print(f"Error getting texture from file node {file_node}: {str(e)}")
                    continue
            
            # 从材质获取贴图
            for material in all_materials:
                try:
                    material_textures = self.get_textures_from_material(material)
                    for texture in material_textures:
                        all_textures.add(texture)
                except Exception as e:
                    print(f"Error processing material {material}: {str(e)}")
                    continue
        
        except Exception as e:
            print(f"Error getting all textures: {str(e)}")
        
        return list(all_textures)

    def copy_textures(self, textures, export_dir):
        """复制贴图文件到导出目录"""
        copied_count = 0
        
        for texture_path in textures:
            try:
                # 获取文件名
                texture_name = os.path.basename(texture_path)
                destination_path = os.path.join(export_dir, texture_name)
                
                # 如果目标文件已存在，询问是否覆盖
                if os.path.exists(destination_path):
                    reply = QtWidgets.QMessageBox.question(
                        self, "File Exists",
                        f"Texture file '{texture_name}' already exists in export directory.\n"
                        "Do you want to overwrite it?",
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.No
                    )
                    
                    if reply == QtWidgets.QMessageBox.No:
                        # 添加后缀避免冲突
                        base_name, ext = os.path.splitext(texture_name)
                        counter = 1
                        while os.path.exists(destination_path):
                            new_name = f"{base_name}_{counter:02d}{ext}"
                            destination_path = os.path.join(export_dir, new_name)
                            counter += 1
                
                # 复制文件
                import shutil
                shutil.copy2(texture_path, destination_path)
                copied_count += 1
                print(f"Copied texture: {texture_name}")
                
            except Exception as e:
                print(f"Error copying texture {texture_path}: {str(e)}")
        
        return copied_count

    def export_all_models(self, export_dir, format_choice):
        """导出场景中的所有模型"""
        exported_count = 0
        
        try:
            # 获取所有mesh类型的模型
            all_meshes = cmds.ls(type='mesh', long=True)
            if not all_meshes:
                return 0
            
            # 去重，只处理每个网格的父变换节点
            transforms = []
            processed_transforms = set()
            
            for mesh in all_meshes:
                try:
                    # 获取mesh的父变换节点
                    parent = cmds.listRelatives(mesh, parent=True, fullPath=True)
                    if not parent:
                        continue
                    
                    transform_node = parent[0]
                    
                    # 检查是否已处理
                    if transform_node not in processed_transforms:
                        transforms.append(transform_node)
                        processed_transforms.add(transform_node)
                        
                except Exception as e:
                    print(f"Error processing mesh {mesh}: {str(e)}")
                    continue
            
            # 导出每个模型
            for transform in transforms:
                try:
                    # 获取模型名称（使用短名称）
                    model_name = transform.split('|')[-1]
                    
                    # 设置导出文件名
                    export_filename = f"{model_name}.{format_choice}"
                    export_path = os.path.join(export_dir, export_filename)
                    
                    # 选择当前模型
                    cmds.select(transform, replace=True)
                    
                    # 根据格式导出
                    if format_choice == 'fbx':
                        # 确保FBX插件已加载
                        if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
                            cmds.loadPlugin('fbxmaya')
                        
                        # 导出FBX
                        cmds.file(
                            export_path,
                            force=True,
                            options="v=0;",
                            typ="FBX export",
                            pr=True,
                            es=True
                        )
                    
                    elif format_choice == 'obj':
                        # 确保OBJ插件已加载
                        if not cmds.pluginInfo('objExport', query=True, loaded=True):
                            cmds.loadPlugin('objExport')
                        
                        # 导出OBJ
                        cmds.file(
                            export_path,
                            force=True,
                            options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1",
                            typ="OBJexport",
                            pr=True,
                            es=True
                        )
                    
                    exported_count += 1
                    print(f"Exported model: {model_name}")
                    
                except Exception as e:
                    print(f"Error exporting model {transform}: {str(e)}")
                    continue
            
            # 清除选择
            cmds.select(clear=True)
            
        except Exception as e:
            print(f"Error in export_all_models: {str(e)}")
        
        return exported_count

    def collect_texture_groups(self, directory, project_code, asset_type, asset_code):
        """收集目录中符合命名规范的贴图分组"""
        texture_groups = {}
        
        # 支持的贴图格式
        texture_extensions = ['.jpeg', '.jpg', '.png', '.exr', '.tga']
        
        print(f"收集贴图组：项目={project_code}, 资产类型={asset_type}, 资产编码={asset_code}")
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                
                # 只处理支持的贴图格式
                if file_ext in texture_extensions:
                    file_path = os.path.join(root, file)
                    texture_name = os.path.splitext(file)[0]  # 去掉扩展名
                    
                    # 解析贴图文件名
                    # 格式：项目代码_资产类型_资产编码_模型详细命名_M_S_贴图类型_UDIM(可选)
                    parts = texture_name.split('_')
                    
                    # 检查贴图命名是否符合要求
                    if len(parts) >= 6:
                        # 检查项目、资产类型、资产编码是否匹配
                        if (parts[0] == project_code and 
                            parts[1] == asset_type and 
                            parts[2] == asset_code):
                            
                            # 检查是否包含M和S部分
                            s_index = -1
                            for i in range(len(parts)-1, -1, -1):
                                if parts[i] == "S" and i > 0 and parts[i-1] == "M":
                                    s_index = i
                                    break
                            
                            if s_index != -1 and s_index >= 4:
                                # 提取材质球名（从项目代码到S）
                                material_name = '_'.join(parts[:s_index+1])  # 包含S
                                
                                # 提取贴图类型（S后面的部分）
                                if s_index + 1 < len(parts):
                                    texture_type_part = parts[s_index+1]
                                    
                                    # 检查贴图类型是否有效
                                    valid_texture_types = ['B', 'E', 'M', 'R', 'N', 'H']
                                    if texture_type_part in valid_texture_types:
                                        # 检查是否有UDIM编号
                                        udim_part = None
                                        if s_index + 2 < len(parts):
                                            next_part = parts[s_index+2]
                                            if next_part.isdigit() and len(next_part) == 4:
                                                udim_part = next_part
                                        
                                        # 添加到分组
                                        if material_name not in texture_groups:
                                            texture_groups[material_name] = {
                                                'material_name': material_name,
                                                'textures': []
                                            }
                                        
                                        texture_info = {
                                            'file_path': file_path,
                                            'file_name': file,
                                            'texture_type': texture_type_part,
                                            'udim': udim_part
                                        }
                                        
                                        texture_groups[material_name]['textures'].append(texture_info)
        
        print(f"收集到 {len(texture_groups)} 个贴图组")
        return texture_groups

    def create_material_for_mesh(self, mesh, material_name, textures):
        """为指定网格创建材质"""
        try:
            # 检查是否已存在同名材质球
            if not cmds.objExists(material_name):
                # 创建aiStandardSurface材质球
                ai_standard = cmds.shadingNode('aiStandardSurface', asShader=True, name=material_name)
                
                # 设置材质球的基本属性
                cmds.setAttr(f"{material_name}.base", 1.0)
                cmds.setAttr(f"{material_name}.baseColor", 0.5, 0.5, 0.5, type="double3")
                cmds.setAttr(f"{material_name}.metalness", 0.0)
                cmds.setAttr(f"{material_name}.specularRoughness", 0.5)
            else:
                ai_standard = material_name
            
            # 检查是否已存在同名shadingEngine - 使用正确的命名
            # 根据材质球名确定shadingEngine名称
            shader_name = f"{material_name}_SG"
            
            if not cmds.objExists(shader_name):
                # 创建shadingEngine节点
                shading_group = cmds.sets(
                    renderable=True, 
                    noSurfaceShader=True, 
                    empty=True, 
                    name=shader_name
                )
                
                # 连接材质球的outColor到shadingEngine的surfaceShader
                cmds.connectAttr(f"{material_name}.outColor", f"{shader_name}.surfaceShader")
            else:
                shading_group = shader_name
            
            # 为每个贴图创建节点
            for texture_info in textures:
                texture_type = texture_info['texture_type']
                file_path = texture_info['file_path']
                udim = texture_info['udim']
                
                # 创建File节点
                file_node_name = f"{material_name}_{texture_type}_F"
                
                # 如果已存在同名File节点，添加数字后缀
                original_file_node_name = file_node_name
                counter = 1
                while cmds.objExists(file_node_name):
                    file_node_name = f"{original_file_node_name}_{counter:02d}"
                    counter += 1
                
                file_node = cmds.shadingNode('file', asTexture=True, name=file_node_name)
                
                # 设置File节点的贴图路径
                normalized_path = file_path.replace('\\', '/')
                cmds.setAttr(f"{file_node_name}.fileTextureName", normalized_path, type="string")
                
                # 设置颜色空间
                if texture_type in ['B', 'E']:
                    cmds.setAttr(f"{file_node_name}.colorSpace", "sRGB", type="string")
                else:
                    cmds.setAttr(f"{file_node_name}.colorSpace", "Raw", type="string")
                
                # 设置UDIM
                if udim:
                    cmds.setAttr(f"{file_node_name}.uvTilingMode", 3)  # 3 = UDIM (Mari)
                    cmds.setAttr(f"{file_node_name}.uvCoord[0].uvTiling[0]", 1)
                    cmds.setAttr(f"{file_node_name}.uvCoord[0].uvTiling[1]", 1)
                    cmds.setAttr(f"{file_node_name}.uvCoord[0].uvOffset[0]", 0)
                    cmds.setAttr(f"{file_node_name}.uvCoord[0].uvOffset[1]", 0)
                
                # 创建place2dTexture节点
                place2d_name = f"{material_name}_{texture_type}_p2d"
                
                # 如果已存在同名place2dTexture节点，添加数字后缀
                original_place2d_name = place2d_name
                counter = 1
                while cmds.objExists(place2d_name):
                    place2d_name = f"{original_place2d_name}_{counter:02d}"
                    counter += 1
                
                place2d_node = cmds.shadingNode('place2dTexture', asUtility=True, name=place2d_name)
                
                # 连接place2dTexture到File节点
                cmds.connectAttr(f"{place2d_name}.outUV", f"{file_node_name}.uvCoord")
                cmds.connectAttr(f"{place2d_name}.outUvFilterSize", f"{file_node_name}.uvFilterSize")
                
                # 对于Normal贴图，创建bump2d节点
                if texture_type == 'N':
                    bump2d_name = f"{material_name}_{texture_type}_bp2d"
                    
                    # 如果已存在同名bump2d节点，添加数字后缀
                    original_bump2d_name = bump2d_name
                    counter = 1
                    while cmds.objExists(bump2d_name):
                        bump2d_name = f"{original_bump2d_name}_{counter:02d}"
                        counter += 1
                    
                    bump2d_node = cmds.shadingNode('bump2d', asUtility=True, name=bump2d_name)
                    
                    # 设置bump2d属性
                    cmds.setAttr(f"{bump2d_name}.bumpInterp", 1)  # 1 = 切线空间法线
                    
                    # 连接File节点的输出Alpha到bump2d的凹凸值
                    cmds.connectAttr(f"{file_node_name}.outAlpha", f"{bump2d_name}.bumpValue")
                    
                    # 连接bump2d的输出法线到aiStandardSurface的Normal Camera
                    cmds.connectAttr(f"{bump2d_name}.outNormal", f"{material_name}.normalCamera")
                else:
                    # 连接File节点到aiStandardSurface的相应属性
                    if texture_type == 'B':
                        cmds.connectAttr(f"{file_node_name}.outColor", f"{material_name}.baseColor")
                    elif texture_type == 'E':
                        cmds.connectAttr(f"{file_node_name}.outColor", f"{material_name}.emissionColor")
                    elif texture_type == 'M':
                        cmds.connectAttr(f"{file_node_name}.outColorR", f"{material_name}.metalness")
                    elif texture_type == 'R':
                        cmds.connectAttr(f"{file_node_name}.outColorR", f"{material_name}.specularRoughness")
                    elif texture_type == 'H':
                        # Height贴图需要额外的displacement节点
                        print(f"Height贴图节点已创建，但需要额外的displacement节点连接")
            
            # 将模型指定到shadingEngine
            cmds.sets(mesh, edit=True, forceElement=shader_name)
            
            return True
            
        except Exception as e:
            print(f"为网格创建材质失败：{str(e)}")
            return False

    def refresh_files(self):
        """刷新文件列表并更新/创建PM文档"""
        directory = self.file_path_edit.text()
        if not directory or not os.path.exists(directory):
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a valid directory first.")
            return
        
        try:
            # 判断当前用户角色
            self.determine_user_role()
            
            if self.current_role == "auditor":
                # 审核人员逻辑
                self.handle_auditor_workflow(directory)
            elif self.current_role == "supplier":
                # 供应商员工逻辑
                self.handle_supplier_workflow(directory)
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Warning",
                    "Please enter information for either auditor or supplier role.\n\n"
                    "For Auditor: Enter Manager code and project/asset information\n"
                    "For Supplier: Enter Company, Personnel codes and other required information"
                )
                return
            
            # 扫描目录中的文件
            self.scan_directory(directory)
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to refresh files: {str(e)}")

    def determine_user_role(self):
        """根据输入信息判断用户角色"""
        has_company_personnel = self.company_code and self.personnel_code
        has_manager = self.manager_code
        
        # 检查是否为审核人员
        auditor_condition = (
            has_manager and
            self.project_code and
            self.asset_code and
            self.asset_type and
            self.project_start_time and
            self.project_end_time and
            self.asset_start_time and
            self.asset_end_time and
            self.phase_of_production and
            self.asset_file_type
        )
        
        # 检查是否为供应商员工
        supplier_condition = (
            has_company_personnel and
            self.project_code and
            self.asset_code and
            self.asset_type and
            self.phase_of_production and
            self.version and
            self.asset_file_type
        )
        
        if auditor_condition:
            self.current_role = "auditor"
        elif supplier_condition:
            self.current_role = "supplier"
        else:
            self.current_role = None

    def handle_auditor_workflow(self, directory):
        """处理审核人员工作流程"""
        # 检查是否同时输入了Company和Personnel代码
        if self.company_code or self.personnel_code:
            QtWidgets.QMessageBox.warning(
                self, "Invalid Input",
                "Auditor cannot enter Company/Personnel codes.\n"
                "Please clear Company and Personnel codes."
            )
            return
        
        # 更新PM文档
        self.update_pm_document(directory)

    def handle_supplier_workflow(self, directory):
        """处理供应商员工工作流程"""
        # 检查是否输入了Manager代码
        if self.manager_code:
            QtWidgets.QMessageBox.warning(
                self, "Invalid Input",
                "Supplier cannot enter Manager code.\n"
                "Please clear Manager code."
            )
            return
        
        # 检查CSV文件是否存在
        csv_filename = "AutoSort_PM_Management_Doc.csv"
        csv_path = os.path.join(directory, csv_filename)
        
        if not os.path.exists(csv_path):
            QtWidgets.QMessageBox.warning(
                self, "Missing File",
                "Missing necessary AutoSort_PM_Management_Doc file.\n"
                "Please create PM document first as auditor."
            )
            return
        
        # 验证供应商输入信息
        if self.check_supplier_validation(csv_path):
            # 验证通过，创建Maya文件
            self.create_maya_file(directory)

    def check_supplier_validation(self, csv_path):
        """验证供应商员工输入的信息"""
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                # 检查是否有匹配的记录
                for i, row in enumerate(rows):
                    if i >= 3 and len(row) >= 16:  # 数据行
                        # 检查字段是否匹配
                        # CSV列索引（根据表头）：
                        # 0: Company Code, 1: Personnel Code, 3: Project Code, 
                        # 7: Asset Code, 8: Asset Type, 9: Phase Of Production, 11: Asset File Type
                        if (
                            row[3] == self.project_code and
                            row[7] == self.asset_code and
                            row[8] == self.asset_type and
                            row[9] == self.phase_of_production and
                            row[11] == self.asset_file_type):
                            
                            # 检查Version列是否为空（表示未审核）
                            if len(row) > 16 and row[16] == "":
                                return True
                            else:
                                QtWidgets.QMessageBox.warning(
                                    self, "Warning",
                                    "Asset has already been approved.\n"
                                    "Please check with auditor for new version."
                                )
                                return False
                
                # 没有找到匹配的记录
                QtWidgets.QMessageBox.warning(
                    self, "Validation Failed",
                    "Asset does not exist, please re-verify input content.\n\n"
                    "Make sure the information matches the PM document."
                )
                return False
                
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Error",
                f"Failed to validate supplier information: {str(e)}"
            )
            return False

    def create_maya_file(self, directory):
        """创建Maya文件"""
        try:
            # 生成文件名
            filename = f"{self.project_code}_{self.asset_type}_{self.asset_code}_{self.phase_of_production}_{self.company_code}_{self.personnel_code}_{self.version}.{self.asset_file_type}"
            file_path = os.path.join(directory, filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 创建新的场景并保存
            cmds.file(new=True, force=True)  # 新建场景，强制关闭当前场景（不保存）
            if self.asset_file_type == "ma":
                cmds.file(rename=file_path)
                cmds.file(save=True, type='mayaAscii', force=True)
            else:  # mb
                cmds.file(rename=file_path)
                cmds.file(save=True, type='mayaBinary', force=True)
            
            # 获取文件信息
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size
            version_start_time = time.strftime('%Y%m%d%H%M%S', time.localtime(file_stats.st_ctime))
            version_end_time = time.strftime('%Y%m%d%H%M%S', time.localtime(file_stats.st_mtime))
            
            # 使用原始字符串格式确保路径正确
            file_path_normalized = file_path.replace('\\', '/')  # 或者保持原始路径
            
            # 更新CSV文件
            self.update_csv_for_supplier(directory, filename, file_path_normalized, file_size, version_start_time, version_end_time)
            
            QtWidgets.QMessageBox.information(
                self, "Success",
                f"Maya file created successfully!\n\n"
                f"File: {filename}\n"
                f"Path: {file_path}\n\n"
                f"CSV document updated with file information."
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Error",
                f"Failed to create Maya file: {str(e)}"
            )

    def update_csv_for_supplier(self, directory, filename, file_path, file_size, version_start_time, version_end_time):
        """为供应商员工更新CSV文件"""
        csv_filename = "AutoSort_PM_Management_Doc.csv"
        csv_path = os.path.join(directory, csv_filename)
        
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # 查找匹配的行并更新
            updated = False
            for i, row in enumerate(rows):
                if i >= 3 and len(row) >= 16:
                    # 匹配条件：根据CSV表头
                    if (row[3] == self.project_code and  # Project Code
                        row[7] == self.asset_code and    # Asset Code
                        row[8] == self.asset_type and    # Asset Type
                        row[9] == self.phase_of_production and  # Phase Of Production
                        row[11] == self.asset_file_type):  # Asset File Type
                        
                        # 确保行有足够的列
                        while len(row) < 23:
                            row.append("")
                        
                        # 使用原始字符串格式确保路径正确
                        normalized_file_path = file_path.replace('\\', '\\\\')  # 将单个反斜杠转义为双反斜杠
                        
                        # 更新字段（根据CSV表头结构）
                        row[0] = self.company_code          # Company Code
                        row[1] = self.personnel_code        # Personnel Code
                        row[10] = filename                  # Asset File Name
                        row[12] = str(file_size)           # Asset File Size
                        row[13] = normalized_file_path     # Asset File Address - 使用转义后的路径
                        row[16] = self.version             # Version
                        row[17] = version_start_time       # Version Start Time
                        row[18] = version_end_time         # Version End Time
                        row[19] = self.project_code        # Asset Project V
                        row[20] = self.company_code        # Company Code V
                        row[21] = self.personnel_code      # Personnel Code V
                        row[22] = ""                       # Asset Manager Code V (空，等待审核)
                        
                        updated = True
                        break
            
            if updated:
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
                    
        except Exception as e:
            raise Exception(f"Failed to update CSV file: {str(e)}")

    def update_pm_document(self, directory):
        """更新或创建PM管理文档"""
        csv_filename = "AutoSort_PM_Management_Doc.csv"
        csv_path = os.path.join(directory, csv_filename)
        
        try:
            # 如果文件不存在，创建新文件并写入表头
            if not os.path.exists(csv_path):
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # 写入表头
                    writer.writerow(["Basic Information"])
                    writer.writerow(["Vendor", "", "PM", "Project", "", "", "", "Asset", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "Manager"])
                    writer.writerow(["Company Code", "Personnel Code", "Manager Code", "Project Code", 
                                "Project Start Time", "Project End Time", "", "Asset Code", "Asset Type",
                                "Phase Of Production", "Asset File Name", "Asset File Type", "Asset File Size",
                                "Asset File Address", "Asset Start Time", "Asset End Time", "Version",
                                "Version Start Time", "Version End Time", "Asset Project V", "Company Code V",
                                "Personnel Code V", "Asset Manager Code V"])
            
            # 读取现有数据
            rows = []
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    rows.append(row)
            
            # 检查重复并添加新数据
            new_rows_added = False
            updated_existing = False
            
            # 对于审核人员，检查是否有重复的Manager Code、Project Code、Asset Code、Asset Type
            row_updated = False
            for i, row in enumerate(rows):
                if i >= 3 and len(row) >= 9:  # 数据行，至少有9列
                    # 检查是否匹配
                    if (row[2] == self.manager_code and  # Manager Code
                        row[3] == self.project_code and  # Project Code
                        row[7] == self.asset_code and  # Asset Code
                        row[8] == self.asset_type):  # Asset Type
                        
                        # 更新现有行
                        # 确保行有足够的列
                        while len(row) < 23:
                            row.append("")
                        
                        # 更新可修改的字段
                        row[4] = self.project_start_time  # Project Start Time
                        row[5] = self.project_end_time  # Project End Time
                        row[14] = self.asset_start_time  # Asset Start Time
                        row[15] = self.asset_end_time  # Asset End Time
                        row[9] = self.phase_of_production  # Phase Of Production
                        row[11] = self.asset_file_type  # Asset File Type
                        
                        # 清空供应商相关字段
                        row[0] = ""  # Company Code
                        row[1] = ""  # Personnel Code
                        row[16] = ""  # Version (保持为空)
                        row[19] = self.project_code  # Asset Project V
                        row[22] = self.manager_code  # Asset Manager Code V
                        
                        updated_existing = True
                        row_updated = True
                        break
            
            if not row_updated:
                # 创建新行
                new_row = [
                    "", "",  # Company Code, Personnel Code (空)
                    self.manager_code,  # Manager Code
                    self.project_code,  # Project Code
                    self.project_start_time,  # Project Start Time
                    self.project_end_time,  # Project End Time
                    "",  # 空列
                    self.asset_code,  # Asset Code
                    self.asset_type,  # Asset Type
                    self.phase_of_production,  # Phase Of Production
                    "",  # Asset File Name (空)
                    self.asset_file_type,  # Asset File Type
                    "",  # Asset File Size (空)
                    "",  # Asset File Address (空)
                    self.asset_start_time,  # Asset Start Time
                    self.asset_end_time,  # Asset End Time
                    "",  # Version (空)
                    "",  # Version Start Time (空)
                    "",  # Version End Time (空)
                    self.project_code,  # Asset Project V
                    "", "",  # Company Code V, Personnel Code V (空)
                    self.manager_code  # Asset Manager Code V
                ]
                rows.append(new_row)
                new_rows_added = True
            
            # 保存文件
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            
            # 显示消息
            if updated_existing:
                QtWidgets.QMessageBox.information(
                    self, "PM Document Updated",
                    f"Existing record updated successfully.\n\n"
                    f"Manager: {self.manager_code}\n"
                    f"Project: {self.project_code}\n"
                    f"Asset: {self.asset_code}\n\n"
                    f"File: {csv_filename}"
                )
            elif new_rows_added:
                QtWidgets.QMessageBox.information(
                    self, "PM Document Created",
                    f"New record added successfully.\n\n"
                    f"Manager: {self.manager_code}\n"
                    f"Project: {self.project_code}\n"
                    f"Asset: {self.asset_code}\n\n"
                    f"File: {csv_filename}"
                )
            else:
                QtWidgets.QMessageBox.information(
                    self, "No Changes",
                    "No changes were made to the PM document."
                )
        
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Error",
                f"Failed to update PM document: {str(e)}"
            )

    def on_file_selected(self):
        """当文件被选中时更新详情和预览"""
        selected_items = self.file_list.selectedItems()
        self.details_list.clear()
        
        if not selected_items:
            self.preview_text.setText("Preview area\n\nSelect an item to preview")
            return
            
        item = selected_items[0]
        file_path = item.data(QtCore.Qt.UserRole)
        
        # 规范化文件路径以确保正确显示
        file_path = os.path.normpath(file_path)
        
        if os.path.exists(file_path):
            # 获取文件名和扩展名
            filename = os.path.basename(file_path)
            file_extension = os.path.splitext(filename)[1].lower()
            
            # 显示文件详情
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size
            
            # 获取修改时间并转换为Qt能处理的格式
            mtime = file_stats.st_mtime
            
            # 方法1: 使用Python的time模块转换为本地时间字符串
            local_time = time.localtime(mtime)
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
            
            details = [
                f"Name: {filename}",
                f"Path: {file_path}",
                f"Size: {self.format_file_size(file_size)}",
                f"Modified: {time_str}",
                f"Type: {file_extension}"
            ]
            
            # 检查是否为ma或mb格式的文件，并尝试解析文件名
            if file_extension in ['.ma', '.mb']:
                # 移除扩展名，获取基本文件名
                base_name = os.path.splitext(filename)[0]
                
                # 尝试按照命名规范解析文件名
                # 格式: ProjectCode_AssetType_AssetCode_Phase_CompanyCode_PersonnelCode_Version
                parts = base_name.split('_')
                
                if len(parts) == 7:
                    # 成功解析，提取各部分信息
                    project_code = parts[0]  # 项目代码
                    asset_type = parts[1]    # 资产类型
                    asset_code = parts[2]    # 资产代码
                    phase = parts[3]         # 制作阶段
                    company_code = parts[4]  # 公司代码
                    personnel_code = parts[5] # 人员代码
                    version = parts[6]       # 版本
                    
                    # 添加解析出的信息
                    details.append("")  # 添加空行分隔
                    details.append("=== Parsed File Information ===")
                    details.append(f"Project Code: {project_code}")
                    details.append(f"Asset Type: {asset_type}")
                    details.append(f"Asset Code: {asset_code}")
                    details.append(f"Phase Of Production: {phase}")
                    details.append(f"Company Code: {company_code}")
                    details.append(f"Personnel Code: {personnel_code}")
                    details.append(f"Version: {version}")
                else:
                    # 文件名不符合命名规范
                    details.append("")  # 添加空行分隔
                    details.append("=== File Information ===")
                    details.append("File name does not match naming convention")
                    details.append(f"Filename format: ProjectCode_AssetType_AssetCode_Phase_CompanyCode_PersonnelCode_Version")
                    details.append(f"Example: PSG_C_ASDASB_M_BHJ_ASU_V008.ma")
            
            for detail in details:
                self.details_list.addItem(detail)
            
            # 根据文件类型选择预览方式
            if file_extension in [".png", ".jpg", ".jpeg", ".tga", ".bmp", ".gif"]:
                self.load_image_preview(file_path)
            elif file_extension in [".txt", ".log", ".md", ".py", ".json", ".xml", ".html", ".css", ".js", ".csv"]:
                self.load_text_preview(file_path)
            else:
                self.preview_text.setText(f"File Preview\n\n{filename}\n\nFile type: {file_extension}\nPreview not available for this file type.")
        else:
            self.details_list.addItem("File not found!")
            self.preview_text.setText("File not found!")
            
    def load_image_preview(self, image_path):
        """加载图片预览"""
        try:
            # 清除文本内容
            self.preview_text.clear()
            
            # 将文件路径转换为Qt能正确处理的格式
            # 对于可能包含非ASCII字符的路径，使用QFile确保路径正确
            file_info = QtCore.QFileInfo(image_path)
            if not file_info.exists():
                self.preview_text.setText("Image file does not exist")
                return
                
            pixmap = QtGui.QPixmap()
            if pixmap.load(image_path):
                # 调整图片大小以适应预览区域
                # 使用固定的最大尺寸
                max_size = QtCore.QSize(350, 250)  # 固定最大尺寸
                scaled_pixmap = pixmap.scaled(
                    max_size,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                
                # 创建文档并插入图片
                cursor = self.preview_text.textCursor()
                self.preview_text.clear()
                self.preview_text.document().addResource(
                    QtGui.QTextDocument.ImageResource,
                    QtCore.QUrl("image"),
                    pixmap
                )
                
                # 插入图片
                image_format = QtGui.QTextImageFormat()
                image_format.setName("image")
                image_format.setWidth(scaled_pixmap.width())
                image_format.setHeight(scaled_pixmap.height())
                
                cursor.insertImage(image_format)
                
                # 添加文件名信息
                self.preview_text.append(f"\nImage: {os.path.basename(image_path)}")
                self.preview_text.append(f"Size: {pixmap.width()}x{pixmap.height()}")
                
            else:
                self.preview_text.setText("Cannot load image preview")
        except Exception as e:
            self.preview_text.setText(f"Error loading preview:\n{str(e)}")
            
    def load_text_preview(self, text_path):
        """加载文本文件预览"""
        try:
            # 清除预览区域
            self.preview_text.clear()
            
            # 检查文件是否存在
            if not os.path.exists(text_path):
                self.preview_text.setText("Text file does not exist")
                return
                
            # 获取文件大小
            file_size = os.path.getsize(text_path)
            
            # 限制预览的文件大小（例如最大1MB）
            MAX_PREVIEW_SIZE = 1024 * 1024  # 1MB
            
            if file_size > MAX_PREVIEW_SIZE:
                self.preview_text.setText(f"Text file too large for preview\n\nFile size: {self.format_file_size(file_size)}\nMaximum preview size: {self.format_file_size(MAX_PREVIEW_SIZE)}\n\nOnly showing first {MAX_PREVIEW_SIZE//1024}KB...")
                
                # 只读取部分内容
                with open(text_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(MAX_PREVIEW_SIZE)
                    self.preview_text.append(content)
                    self.preview_text.append(f"\n\n[...文件太大，只显示部分内容...]")
            else:
                # 读取整个文件
                try:
                    with open(text_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.preview_text.setText(content)
                except UnicodeDecodeError:
                    # 如果UTF-8解码失败，尝试其他编码
                    try:
                        with open(text_path, 'r', encoding='gbk') as f:
                            content = f.read()
                            self.preview_text.setText(content)
                    except:
                        with open(text_path, 'r', encoding='latin-1', errors='ignore') as f:
                            content = f.read()
                            self.preview_text.setText(content)
            
            # 添加文件信息
            info = f"\n\n--- File Info ---\n"
            info += f"File: {os.path.basename(text_path)}\n"
            info += f"Size: {self.format_file_size(file_size)}\n"
            info += f"Lines: {self.count_lines(text_path) if file_size <= MAX_PREVIEW_SIZE else 'Too many to count'}"
            
            self.preview_text.append(info)
            
        except Exception as e:
            self.preview_text.setText(f"Error loading text preview:\n{str(e)}")
    
    def count_lines(self, file_path):
        """计算文件行数"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return "Unknown"
            
    def filter_by_format(self, file_format):
        """按格式过滤文件"""
        directory = self.file_path_edit.text()
        if not directory or not os.path.exists(directory):
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a valid directory first.")
            return
            
        self.file_list.clear()
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(file_format.lower()):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, directory)
                        
                        item = QtWidgets.QListWidgetItem(relative_path)
                        item.setData(QtCore.Qt.UserRole, file_path)
                        item.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
                        self.file_list.addItem(item)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to filter files: {str(e)}")
            
    def format_file_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
        
    def toggle_window_pin(self, checked):
        """切换窗口置顶状态"""
        if checked:
            # 设置为置顶
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            self.pin_button.setText("Pinned")
            # 更新按钮图标
            pin_icon = self.style().standardIcon(QtWidgets.QStyle.SP_TitleBarMaxButton)
            self.pin_button.setIcon(pin_icon)
        else:
            # 取消置顶
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
            self.pin_button.setText("Pin Window")
            # 恢复按钮图标
            pin_icon = self.style().standardIcon(QtWidgets.QStyle.SP_TitleBarNormalButton)
            self.pin_button.setIcon(pin_icon)
        
        # 重新显示窗口使标志生效
        self.show()
    
    def clear_all_info(self):
        """清空所有输入信息"""
        # 询问用户是否确认清空
        reply = QtWidgets.QMessageBox.question(
            self, 
            "Confirm Clear",
            "Are you sure you want to clear all input information?\n\n"
            "This will reset Company, Personnel, Project and Asset codes/times.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # 清空所有存储的信息
            self.company_code = ""
            self.personnel_code = ""
            self.project_code = ""
            self.project_start_time = ""
            self.project_end_time = ""
            self.asset_code = ""
            self.asset_type = ""
            self.asset_start_time = ""
            self.asset_end_time = ""
            self.manager_code = ""
            self.phase_of_production = ""
            self.version = ""
            self.asset_file_type = ""
            self.current_role = None
            
            # 显示成功消息
            QtWidgets.QMessageBox.information(
                self, "Information Cleared",
                "All input information has been cleared successfully.\n\n"
                "All codes and times have been reset to default."
            )
    
    def set_company_code(self):
        """设置Company代码"""
        # 检查是否已输入Manager代码
        if self.manager_code:
            QtWidgets.QMessageBox.warning(
                self, "Invalid Operation",
                "Cannot set Company code when Manager code is already set.\n"
                "Please clear Manager code first."
            )
            return
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Company Code", 
            "Enter Company Code (3 uppercase letters):",
            QtWidgets.QLineEdit.Normal, 
            self.company_code if self.company_code else ""
        )
        if ok and text:
            # 转换为大写并限制为3个字符
            code = text.upper()[:3]
            # 验证：必须是3个大写字母
            if len(code) == 3 and code.isalpha() and code.isupper():
                self.company_code = code
                QtWidgets.QMessageBox.information(self, "Success", f"Company code set to: {code}")
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter exactly 3 uppercase letters.")
                # 不保存输入
                return
    
    def set_personnel_code(self):
        """设置Personnel代码"""
        # 检查是否已输入Manager代码
        if self.manager_code:
            QtWidgets.QMessageBox.warning(
                self, "Invalid Operation",
                "Cannot set Personnel code when Manager code is already set.\n"
                "Please clear Manager code first."
            )
            return
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Personnel Code", 
            "Enter Personnel Code (3 uppercase letters):",
            QtWidgets.QLineEdit.Normal, 
            self.personnel_code if self.personnel_code else ""
        )
        if ok and text:
            # 转换为大写并限制为3个字符
            code = text.upper()[:3]
            # 验证：必须是3个大写字母
            if len(code) == 3 and code.isalpha() and code.isupper():
                self.personnel_code = code
                QtWidgets.QMessageBox.information(self, "Success", f"Personnel code set to: {code}")
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter exactly 3 uppercase letters.")
                # 不保存输入
                return
    
    def set_project_code(self):
        """设置Project代码"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Project Code", 
            "Enter Project Code (3 uppercase letters):",
            QtWidgets.QLineEdit.Normal, 
            self.project_code if self.project_code else ""
        )
        if ok and text:
            # 转换为大写并限制为3个字符
            code = text.upper()[:3]
            # 验证：必须是3个大写字母
            if len(code) == 3 and code.isalpha() and code.isupper():
                self.project_code = code
                QtWidgets.QMessageBox.information(self, "Success", f"Project code set to: {code}")
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter exactly 3 uppercase letters.")
                # 不保存输入
                return
    
    def set_project_start_time(self):
        """设置Project开始时间"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Project Start Time", 
            "Enter Project Start Time (14 digits, e.g., 20250904191530):",
            QtWidgets.QLineEdit.Normal, 
            self.project_start_time if self.project_start_time else ""
        )
        if ok and text:
            # 验证是否为14位数字
            if text.isdigit() and len(text) == 14:
                # 可选：验证时间是否合理（年份在2000-2099之间）
                year = int(text[0:4])
                month = int(text[4:6])
                day = int(text[6:8])
                hour = int(text[8:10])
                minute = int(text[10:12])
                second = int(text[12:14])
                
                if (2000 <= year <= 2099 and 1 <= month <= 12 and 
                    1 <= day <= 31 and 0 <= hour <= 23 and 
                    0 <= minute <= 59 and 0 <= second <= 59):
                    self.project_start_time = text
                    QtWidgets.QMessageBox.information(self, "Success", f"Project start time set to: {text}")
                else:
                    QtWidgets.QMessageBox.warning(self, "Invalid Input", 
                        "Please enter a valid date/time (YYYYMMDDHHMMSS format).\n"
                        "Year: 2000-2099, Month: 01-12, Day: 01-31,\n"
                        "Hour: 00-23, Minute: 00-59, Second: 00-59")
                    # 不保存输入
                    return
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter exactly 14 digits (YYYYMMDDHHMMSS format).")
                # 不保存输入
                return
    
    def set_project_end_time(self):
        """设置Project结束时间"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Project End Time", 
            "Enter Project End Time (14 digits, e.g., 20250904191530):",
            QtWidgets.QLineEdit.Normal, 
            self.project_end_time if self.project_end_time else ""
        )
        if ok and text:
            # 验证是否为14位数字
            if text.isdigit() and len(text) == 14:
                # 验证时间是否合理（年份在2000-2099之间）
                year = int(text[0:4])
                month = int(text[4:6])
                day = int(text[6:8])
                hour = int(text[8:10])
                minute = int(text[10:12])
                second = int(text[12:14])
                
                if (2000 <= year <= 2099 and 1 <= month <= 12 and 
                    1 <= day <= 31 and 0 <= hour <= 23 and 
                    0 <= minute <= 59 and 0 <= second <= 59):
                    
                    # 可选：验证结束时间是否晚于开始时间（如果开始时间已设置）
                    if self.project_start_time:
                        if text < self.project_start_time:
                            QtWidgets.QMessageBox.warning(self, "Invalid Input", 
                                "Project end time must be later than start time.")
                            return
                    
                    self.project_end_time = text
                    QtWidgets.QMessageBox.information(self, "Success", f"Project end time set to: {text}")
                else:
                    QtWidgets.QMessageBox.warning(self, "Invalid Input", 
                        "Please enter a valid date/time (YYYYMMDDHHMMSS format).\n"
                        "Year: 2000-2099, Month: 01-12, Day: 01-31,\n"
                        "Hour: 00-23, Minute: 00-59, Second: 00-59")
                    # 不保存输入
                    return
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter exactly 14 digits (YYYYMMDDHHMMSS format).")
                # 不保存输入
                return
    
    def set_asset_code(self):
        """设置Asset代码"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Asset Code", 
            "Enter Asset Code (6 uppercase letters):",
            QtWidgets.QLineEdit.Normal, 
            self.asset_code if self.asset_code else ""
        )
        if ok and text:
            # 转换为大写并限制为6个字符
            code = text.upper()[:6]
            # 验证：必须是6个大写字母
            if len(code) == 6 and code.isalpha() and code.isupper():
                self.asset_code = code
                QtWidgets.QMessageBox.information(self, "Success", f"Asset code set to: {code}")
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter exactly 6 uppercase letters.")
                # 不保存输入
                return
    
    def set_asset_type(self):
        """设置Asset类型"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Asset Type", 
            "Enter Asset Type (C, S, or O):",
            QtWidgets.QLineEdit.Normal, 
            self.asset_type if self.asset_type else ""
        )
        if ok and text:
            # 转换为大写，取第一个字符
            atype = text.upper()[:1]
            if atype in ['C', 'S', 'O']:
                self.asset_type = atype
                QtWidgets.QMessageBox.information(self, "Success", f"Asset type set to: {atype}")
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter C, S, or O.")
                # 不保存输入
                return
    
    def set_asset_start_time(self):
        """设置Asset开始时间"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Asset Start Time", 
            "Enter Asset Start Time (14 digits, e.g., 20250904191530):",
            QtWidgets.QLineEdit.Normal, 
            self.asset_start_time if self.asset_start_time else ""
        )
        if ok and text:
            # 验证是否为14位数字
            if text.isdigit() and len(text) == 14:
                # 验证时间是否合理（年份在2000-2099之间）
                year = int(text[0:4])
                month = int(text[4:6])
                day = int(text[6:8])
                hour = int(text[8:10])
                minute = int(text[10:12])
                second = int(text[12:14])
                
                if (2000 <= year <= 2099 and 1 <= month <= 12 and 
                    1 <= day <= 31 and 0 <= hour <= 23 and 
                    0 <= minute <= 59 and 0 <= second <= 59):
                    self.asset_start_time = text
                    QtWidgets.QMessageBox.information(self, "Success", f"Asset start time set to: {text}")
                else:
                    QtWidgets.QMessageBox.warning(self, "Invalid Input", 
                        "Please enter a valid date/time (YYYYMMDDHHMMSS format).\n"
                        "Year: 2000-2099, Month: 01-12, Day: 01-31,\n"
                        "Hour: 00-23, Minute: 00-59, Second: 00-59")
                    # 不保存输入
                    return
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter exactly 14 digits (YYYYMMDDHHMMSS format).")
                # 不保存输入
                return
    
    def set_asset_end_time(self):
        """设置Asset结束时间"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Asset End Time", 
            "Enter Asset End Time (14 digits, e.g., 20250904191530):",
            QtWidgets.QLineEdit.Normal, 
            self.asset_end_time if self.asset_end_time else ""
        )
        if ok and text:
            # 验证是否为14位数字
            if text.isdigit() and len(text) == 14:
                # 验证时间是否合理（年份在2000-2099之间）
                year = int(text[0:4])
                month = int(text[4:6])
                day = int(text[6:8])
                hour = int(text[8:10])
                minute = int(text[10:12])
                second = int(text[12:14])
                
                if (2000 <= year <= 2099 and 1 <= month <= 12 and 
                    1 <= day <= 31 and 0 <= hour <= 23 and 
                    0 <= minute <= 59 and 0 <= second <= 59):
                    
                    # 可选：验证结束时间是否晚于开始时间（如果开始时间已设置）
                    if self.asset_start_time:
                        if text < self.asset_start_time:
                            QtWidgets.QMessageBox.warning(self, "Invalid Input", 
                                "Asset end time must be later than start time.")
                            return
                    
                    self.asset_end_time = text
                    QtWidgets.QMessageBox.information(self, "Success", f"Asset end time set to: {text}")
                else:
                    QtWidgets.QMessageBox.warning(self, "Invalid Input", 
                        "Please enter a valid date/time (YYYYMMDDHHMMSS format).\n"
                        "Year: 2000-2099, Month: 01-12, Day: 01-31,\n"
                        "Hour: 00-23, Minute: 00-59, Second: 00-59")
                    # 不保存输入
                    return
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter exactly 14 digits (YYYYMMDDHHMMSS format).")
                # 不保存输入
                return

    def set_phase_of_production(self):
        """设置制作阶段"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Phase Of Production", 
            "Enter Phase Of Production (M/S/T/D/R/A):\n"
            "M: Modeling (建模阶段)\n"
            "S: Shading (材质阶段)\n"
            "T: Texturing (贴图阶段)\n"
            "D: Rendering (渲染阶段)\n"
            "R: Rigging (绑定阶段)\n"
            "A: Animation (动画阶段)",
            QtWidgets.QLineEdit.Normal, 
            self.phase_of_production if self.phase_of_production else ""
        )
        if ok and text:
            # 转换为大写，取第一个字符
            phase = text.upper()[:1]
            if phase in ['M', 'S', 'T', 'D', 'R', 'A']:
                self.phase_of_production = phase
                phase_names = {
                    'M': 'Modeling (建模阶段)',
                    'S': 'Shading (材质阶段)', 
                    'T': 'Texturing (贴图阶段)',
                    'D': 'Rendering (渲染阶段)',
                    'R': 'Rigging (绑定阶段)',
                    'A': 'Animation (动画阶段)'
                }
                QtWidgets.QMessageBox.information(
                    self, "Success", 
                    f"Phase of production set to: {phase}\n({phase_names[phase]})"
                )
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Invalid Input", 
                    "Please enter one of: M, S, T, D, R, A.\n\n"
                    "M: Modeling (建模阶段)\n"
                    "S: Shading (材质阶段)\n"
                    "T: Texturing (贴图阶段)\n"
                    "D: Rendering (渲染阶段)\n"
                    "R: Rigging (绑定阶段)\n"
                    "A: Animation (动画阶段)"
                )
                # 不保存输入
                return

    def set_version(self):
        """设置版本"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Version", 
            "Enter Version:\n"
            "Format 1: V + 3 digits (e.g., V001, V008) - Work in progress\n"
            "Format 2: VFN - Final approved version",
            QtWidgets.QLineEdit.Normal, 
            self.version if self.version else ""
        )
        if ok and text:
            # 转换为大写
            version = text.upper()
            # 验证格式
            if version == "VFN":
                self.version = version
                QtWidgets.QMessageBox.information(
                    self, "Success", 
                    f"Version set to: {version}\n(Final approved version)"
                )
            elif version.startswith("V") and len(version) == 4 and version[1:].isdigit():
                # 验证数字部分
                num_part = version[1:]
                if 1 <= int(num_part) <= 999:
                    self.version = version
                    QtWidgets.QMessageBox.information(
                        self, "Success", 
                        f"Version set to: {version}\n(Work in progress, version {int(num_part)})"
                    )
                else:
                    QtWidgets.QMessageBox.warning(
                        self, "Invalid Input", 
                        "Version number must be between 001 and 999."
                    )
                    return
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Invalid Input", 
                    "Please enter valid version format:\n\n"
                    "1. V + 3 digits (e.g., V001, V008) for work in progress\n"
                    "2. VFN for final approved version"
                )
                return

    def set_asset_file_type(self):
        """设置资产文件类型"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Asset File Type", 
            "Enter Asset File Type (ma or mb):",
            QtWidgets.QLineEdit.Normal, 
            self.asset_file_type if self.asset_file_type else ""
        )
        if ok and text:
            # 转换为小写
            file_type = text.lower()
            if file_type in ['ma', 'mb']:
                self.asset_file_type = file_type
                QtWidgets.QMessageBox.information(
                    self, "Success", 
                    f"Asset file type set to: .{file_type}"
                )
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Invalid Input", 
                    "Please enter 'ma' or 'mb'."
                )
                return

    def create_pm_document(self):
        """设置Manager代码"""
        # 检查是否已输入Company或Personnel代码
        if self.company_code or self.personnel_code:
            QtWidgets.QMessageBox.warning(
                self, "Invalid Operation",
                "Cannot set Manager code when Company/Personnel codes are already set.\n"
                "Please clear Company and Personnel codes first."
            )
            return
            
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Manager Code", 
            "Enter Manager Code (3 lowercase letters):",
            QtWidgets.QLineEdit.Normal, 
            self.manager_code if self.manager_code else ""
        )
        
        if not ok or not text:
            return  # 用户取消了输入
        
        # 验证输入
        manager_code = text.lower().strip()
        if len(manager_code) != 3 or not manager_code.isalpha() or not manager_code.islower():
            QtWidgets.QMessageBox.warning(
                self, "Invalid Input", 
                "Please enter exactly 3 lowercase letters."
            )
            return
        
        self.manager_code = manager_code
        QtWidgets.QMessageBox.information(self, "Success", f"Manager code set to: {manager_code}")

    def import_selection(self):
        """导入选择的文件"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(
                self, "Warning", 
                "Please select files to import first."
            )
            return
        
        directory = self.file_path_edit.text()
        if not directory or not os.path.exists(directory):
            QtWidgets.QMessageBox.warning(
                self, "Warning", 
                "Please select a valid directory first."
            )
            return
        
        # 支持的导入格式
        supported_formats = ['.ma', '.mb', '.obj', '.fbx', '.usd', '.abc']
        
        imported_count = 0
        for item in selected_items:
            file_path = item.data(QtCore.Qt.UserRole)
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in supported_formats:
                try:
                    # 根据文件格式导入
                    if file_ext in ['.ma', '.mb']:
                        # 导入Maya文件
                        cmds.file(file_path, i=True, ignoreVersion=True, 
                                mergeNamespacesOnClash=False, 
                                namespace=':', options='v=0;')
                    
                    elif file_ext in ['.obj', '.fbx']:
                        # 导入OBJ或FBX
                        if file_ext == '.obj':
                            # 先检查OBJ插件是否加载
                            if not cmds.pluginInfo('objExport', query=True, loaded=True):
                                cmds.loadPlugin('objExport')
                            cmds.file(file_path, i=True, type='OBJ', 
                                    ignoreVersion=True, options='v=0')
                        else:  # fbx
                            # 先检查FBX插件是否加载
                            if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
                                cmds.loadPlugin('fbxmaya')
                            cmds.file(file_path, i=True, type='FBX', 
                                    ignoreVersion=True, options='v=0')
                    
                    elif file_ext == '.usd':
                        # 导入USD - 需要确保USD插件已加载
                        if not cmds.pluginInfo('mayaUsdPlugin', query=True, loaded=True):
                            try:
                                cmds.loadPlugin('mayaUsdPlugin')
                            except:
                                QtWidgets.QMessageBox.warning(
                                    self, "Warning",
                                    "USD plugin not available. Skipping USD import."
                                )
                                continue
                        cmds.file(file_path, i=True, type='USD Import', 
                                ignoreVersion=True, options='v=0')
                    
                    elif file_ext == '.abc':
                        # 导入Alembic - 需要确保Alembic插件已加载
                        if not cmds.pluginInfo('AbcImport', query=True, loaded=True):
                            try:
                                cmds.loadPlugin('AbcImport')
                            except:
                                QtWidgets.QMessageBox.warning(
                                    self, "Warning",
                                    "Alembic plugin not available. Skipping Alembic import."
                                )
                                continue
                        cmds.file(file_path, i=True, type='Alembic', 
                                ignoreVersion=True, options='v=0')
                    
                    imported_count += 1
                    
                except Exception as e:
                    QtWidgets.QMessageBox.warning(
                        self, "Import Error",
                        f"Failed to import {os.path.basename(file_path)}:\n{str(e)}"
                    )
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Unsupported Format",
                    f"File {os.path.basename(file_path)} has unsupported format for import.\n"
                    f"Supported formats: .ma, .mb, .obj, .fbx, .usd, .abc"
                )
        
        if imported_count > 0:
            QtWidgets.QMessageBox.information(
                self, "Success",
                f"Successfully imported {imported_count} file(s)."
            )

    def import_all(self):
        """导入所有符合要求的文件"""
        directory = self.file_path_edit.text()
        if not directory or not os.path.exists(directory):
            QtWidgets.QMessageBox.warning(
                self, "Warning", 
                "Please select a valid directory first."
            )
            return
        
        # 支持的导入格式
        supported_formats = ['.ma', '.mb', '.obj', '.fbx', '.usd', '.abc']
        
        imported_count = 0
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if file_ext in supported_formats:
                        file_path = os.path.join(root, file)
                        
                        try:
                            # 根据文件格式导入
                            if file_ext in ['.ma', '.mb']:
                                cmds.file(file_path, i=True, ignoreVersion=True, 
                                        mergeNamespacesOnClash=False, 
                                        namespace=':', options='v=0;')
                            
                            elif file_ext in ['.obj', '.fbx']:
                                if file_ext == '.obj':
                                    if not cmds.pluginInfo('objExport', query=True, loaded=True):
                                        cmds.loadPlugin('objExport')
                                    cmds.file(file_path, i=True, type='OBJ', 
                                            ignoreVersion=True, options='v=0')
                                else:  # fbx
                                    if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
                                        cmds.loadPlugin('fbxmaya')
                                    cmds.file(file_path, i=True, type='FBX', 
                                            ignoreVersion=True, options='v=0')
                            
                            elif file_ext == '.usd':
                                if not cmds.pluginInfo('mayaUsdPlugin', query=True, loaded=True):
                                    try:
                                        cmds.loadPlugin('mayaUsdPlugin')
                                    except:
                                        continue  # 跳过USD文件
                                cmds.file(file_path, i=True, type='USD Import', 
                                        ignoreVersion=True, options='v=0')
                            
                            elif file_ext == '.abc':
                                if not cmds.pluginInfo('AbcImport', query=True, loaded=True):
                                    try:
                                        cmds.loadPlugin('AbcImport')
                                    except:
                                        continue  # 跳过Alembic文件
                                cmds.file(file_path, i=True, type='Alembic', 
                                        ignoreVersion=True, options='v=0')
                            
                            imported_count += 1
                            
                        except Exception as e:
                            # 静默失败，继续导入其他文件
                            print(f"Failed to import {file}: {str(e)}")
            
            if imported_count > 0:
                QtWidgets.QMessageBox.information(
                    self, "Success",
                    f"Successfully imported {imported_count} file(s)."
                )
            else:
                QtWidgets.QMessageBox.information(
                    self, "No Files Imported",
                    "No supported files found for import in the selected directory."
                )
                
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Error",
                f"Failed to import files: {str(e)}"
            )

    def combined_export(self):
        """合并导出所有模型为单个文件"""
        # 检查是否在Maya中
        if not cmds.ls(type='mesh'):
            QtWidgets.QMessageBox.warning(
                self, "No Models Found",
                "No mesh models found in the current scene."
            )
            return
        
        # 获取导出目录
        export_dir = self.file_path_edit.text()
        if not export_dir or not os.path.exists(export_dir):
            QtWidgets.QMessageBox.warning(
                self, "Invalid Directory",
                "Please select a valid export directory in Browse."
            )
            return
        
        # 选择导出格式
        format_choice, ok = QtWidgets.QInputDialog.getItem(
            self, "Export Format",
            "Choose export format:",
            ["fbx", "obj"], 0, False
        )
        
        if not ok:
            return  # 用户取消
        
        try:
            # 选择所有网格
            all_meshes = cmds.ls(type='mesh', long=True)
            if not all_meshes:
                QtWidgets.QMessageBox.warning(
                    self, "No Models Found",
                    "No mesh models found in the current scene."
                )
                return
            
            # 获取所有网格的变换节点
            transforms = []
            for mesh in all_meshes:
                parent = cmds.listRelatives(mesh, parent=True, fullPath=True)
                if parent:
                    transforms.append(parent[0])
            
            if not transforms:
                QtWidgets.QMessageBox.warning(
                    self, "Error",
                    "Could not find transform nodes for meshes."
                )
                return
            
            # 选择所有变换节点
            cmds.select(transforms, replace=True)
            
            # 合并所有模型
            combined = cmds.polyUnite(
                transforms,
                mergeUVSets=True,
                centerPivot=True,
                name="combined_mesh"
            )
            
            # 删除历史记录
            cmds.delete(combined[0], constructionHistory=True)
            
            # 重命名合并后的模型
            combined_name = "PPAAAS"  # 示例名称，实际应获取合并后的模型名称
            cmds.rename(combined[0], combined_name)
            
            # 设置导出文件名
            export_filename = f"{combined_name}_combined.{format_choice}"
            export_path = os.path.join(export_dir, export_filename)
            
            # 导出合并的模型
            cmds.select(combined_name, replace=True)
            
            if format_choice == 'fbx':
                # 导出FBX
                if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
                    cmds.loadPlugin('fbxmaya')
                
                cmds.file(
                    export_path,
                    force=True,
                    options="v=0;",
                    typ="FBX export",
                    pr=True,
                    es=True
                )
            
            elif format_choice == 'obj':
                # 导出OBJ
                if not cmds.pluginInfo('objExport', query=True, loaded=True):
                    cmds.loadPlugin('objExport')
                
                cmds.file(
                    export_path,
                    force=True,
                    options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1",
                    typ="OBJexport",
                    pr=True,
                    es=True
                )
            
            # 恢复场景（删除合并的模型，保留原始模型）
            cmds.delete(combined_name)
            
            QtWidgets.QMessageBox.information(
                self, "Export Successful",
                f"Combined model exported successfully to:\n{export_path}"
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Export Error",
                f"Failed to export combined model:\n{str(e)}"
            )

    def individual_export(self):
        """单独导出每个模型"""
        # 检查是否在Maya中
        if not cmds.ls(type='mesh'):
            QtWidgets.QMessageBox.warning(
                self, "No Models Found",
                "No mesh models found in the current scene."
            )
            return
        
        # 获取导出目录
        export_dir = self.file_path_edit.text()
        if not export_dir or not os.path.exists(export_dir):
            QtWidgets.QMessageBox.warning(
                self, "Invalid Directory",
                "Please select a valid export directory in Browse."
            )
            return
        
        # 选择导出格式
        format_choice, ok = QtWidgets.QInputDialog.getItem(
            self, "Export Format",
            "Choose export format:",
            ["fbx", "obj"], 0, False
        )
        
        if not ok:
            return  # 用户取消
        
        try:
            # 获取所有网格
            all_meshes = cmds.ls(type='mesh', long=True)
            if not all_meshes:
                QtWidgets.QMessageBox.warning(
                    self, "No Models Found",
                    "No mesh models found in the current scene."
                )
                return
            
            exported_count = 0
            failed_exports = []
            
            for mesh in all_meshes:
                try:
                    # 获取网格的变换节点
                    parent = cmds.listRelatives(mesh, parent=True, fullPath=True)
                    if not parent:
                        continue
                    
                    transform = parent[0]
                    mesh_name = transform.split('|')[-1]  # 获取短名称
                    
                    # 选择当前网格
                    cmds.select(transform, replace=True)
                    
                    # 设置导出文件名
                    export_filename = f"{mesh_name}.{format_choice}"
                    export_path = os.path.join(export_dir, export_filename)
                    
                    # 根据格式导出
                    if format_choice == 'fbx':
                        # 确保FBX插件已加载
                        if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
                            cmds.loadPlugin('fbxmaya')
                        
                        cmds.file(
                            export_path,
                            force=True,
                            options="v=0;",
                            typ="FBX export",
                            pr=True,
                            es=True
                        )
                    
                    elif format_choice == 'obj':
                        # 确保OBJ插件已加载
                        if not cmds.pluginInfo('objExport', query=True, loaded=True):
                            cmds.loadPlugin('objExport')
                        
                        cmds.file(
                            export_path,
                            force=True,
                            options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1",
                            typ="OBJexport",
                            pr=True,
                            es=True
                        )
                    
                    exported_count += 1
                    
                except Exception as e:
                    failed_exports.append(f"{mesh_name}: {str(e)}")
            
            # 显示结果
            if exported_count > 0:
                message = f"Successfully exported {exported_count} model(s)."
                if failed_exports:
                    message += f"\n\nFailed to export {len(failed_exports)} model(s):"
                    for failed in failed_exports[:5]:  # 只显示前5个失败
                        message += f"\n• {failed}"
                    if len(failed_exports) > 5:
                        message += f"\n... and {len(failed_exports) - 5} more"
                
                QtWidgets.QMessageBox.information(
                    self, "Export Results",
                    message
                )
            else:
                QtWidgets.QMessageBox.warning(
                    self, "No Exports",
                    "No models were exported successfully."
                )
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Export Error",
                f"Failed to export individual models:\n{str(e)}"
            )

    def compliance_check(self):
        """合规性检查：检查模型和贴图文件命名是否符合规范"""
        try:
            # 获取当前Maya文件名
            current_file = cmds.file(query=True, sceneName=True)
            if not current_file:
                QtWidgets.QMessageBox.warning(
                    self, "No File",
                    "Maya scene file is not saved. Please save the file first to get filename information."
                )
                return
            
            # 从文件名提取信息
            file_name = os.path.basename(current_file)
            base_name = os.path.splitext(file_name)[0]
            
            # 解析文件名（格式：项目代码_资产类型_资产编码_阶段_公司代码_人员代码_版本）
            parts = base_name.split('_')
            if len(parts) != 7:
                QtWidgets.QMessageBox.warning(
                    self, "Invalid File Name",
                    "Maya file name does not conform to naming convention.\n"
                    "Format should be: ProjectCode_AssetType_AssetCode_Phase_CompanyCode_PersonnelCode_Version\n"
                    f"Current file name: {file_name}"
                )
                return
            
            project_code = parts[0]      # 项目代码
            asset_type = parts[1]        # 资产类型 (C/S/O)
            asset_code = parts[2]        # 资产编码
            
            # 获取Browse选择的目录
            check_dir = self.file_path_edit.text()
            if not check_dir or not os.path.exists(check_dir):
                QtWidgets.QMessageBox.warning(
                    self, "No Directory",
                    "Please first select a valid directory through the Browse button."
                )
                return
            
            # 检查模型文件
            model_errors = self.check_model_files(check_dir, project_code, asset_type, asset_code)
            
            # 检查贴图文件
            texture_errors = self.check_texture_files(check_dir, project_code, asset_type, asset_code)
            
            # 显示检查结果
            if not model_errors and not texture_errors:
                QtWidgets.QMessageBox.information(
                    self, "Compliance Check Passed",
                    "Naming meets requirements, automatic import command can be executed."
                )
            else:
                error_message = "Naming does not meet requirements, automatic import command cannot be executed, please rename.\n\n"
                
                if model_errors:
                    error_message += "Model file errors:\n"
                    for error in model_errors:
                        error_message += f"- {error}\n"
                    error_message += "\n"
                
                if texture_errors:
                    error_message += "Texture file errors:\n"
                    for error in texture_errors:
                        error_message += f"- {error}\n"
                
                QtWidgets.QMessageBox.warning(
                    self, "Compliance Check Failed",
                    error_message
                )
                
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Compliance Check Error",
                f"Error during compliance check: {str(e)}"
            )

    def convert_obj_to_fbx(self):
        """将OBJ文件转换为FBX文件"""
        try:
            # 获取Browse文件夹路径
            directory = self.file_path_edit.text()
            if not directory or not os.path.exists(directory):
                QtWidgets.QMessageBox.warning(
                    self, "Invalid Directory",
                    "Please select a valid directory in Browse first."
                )
                return
            
            # 获取所有OBJ文件
            obj_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.obj'):
                        obj_files.append(os.path.join(root, file))
            
            if not obj_files:
                QtWidgets.QMessageBox.warning(
                    self, "No OBJ Files",
                    "No OBJ files found in the selected directory."
                )
                return
            
            # 询问导出文件名
            export_name, ok = QtWidgets.QInputDialog.getText(
                self, "Export FBX File",
                "Enter the name for the exported FBX file (without extension):",
                QtWidgets.QLineEdit.Normal,
                "converted_model"
            )
            
            if not ok or not export_name:
                return  # 用户取消
            
            # 确保FBX插件已加载
            if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
                cmds.loadPlugin('fbxmaya')
            
            # 确保OBJ插件已加载
            if not cmds.pluginInfo('objExport', query=True, loaded=True):
                cmds.loadPlugin('objExport')
            
            # 保存当前场景（可选）
            current_scene = cmds.file(query=True, sceneName=True)
            
            # 导入所有OBJ文件
            imported_objects = []
            for obj_file in obj_files:
                try:
                    # 导入OBJ文件
                    cmds.file(
                        obj_file,
                        i=True,  # 导入
                        type='OBJ',
                        ignoreVersion=True,
                        options="v=0;",
                        pr=True
                    )
                    
                    # 获取最近导入的对象
                    imported_nodes = cmds.ls(assemblies=True)
                    if imported_nodes:
                        imported_objects.extend(imported_nodes)
                        
                except Exception as e:
                    print(f"Error importing {obj_file}: {str(e)}")
                    continue
            
            if not imported_objects:
                QtWidgets.QMessageBox.warning(
                    self, "Import Failed",
                    "Failed to import any OBJ files."
                )
                return
            
            # 选择所有导入的对象
            cmds.select(imported_objects, replace=True)
            
            # 设置导出路径
            export_path = os.path.join(directory, f"{export_name}.fbx")
            
            # 检查文件是否已存在
            if os.path.exists(export_path):
                reply = QtWidgets.QMessageBox.question(
                    self, "File Exists",
                    f"FBX file '{export_name}.fbx' already exists.\n"
                    "Do you want to overwrite it?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No
                )
                if reply == QtWidgets.QMessageBox.No:
                    # 添加序号避免冲突
                    counter = 1
                    while os.path.exists(export_path):
                        export_path = os.path.join(directory, f"{export_name}_{counter:02d}.fbx")
                        counter += 1
            
            # 导出为FBX
            cmds.file(
                export_path,
                force=True,
                options="v=0;",
                typ="FBX export",
                pr=True,
                es=True
            )
            
            # 删除导入的对象（可选，恢复原始场景）
            if imported_objects:
                cmds.delete(imported_objects)
            
            # 恢复原始选择
            cmds.select(clear=True)
            
            QtWidgets.QMessageBox.information(
                self, "Conversion Complete",
                f"Successfully converted {len(obj_files)} OBJ file(s) to FBX.\n\n"
                f"Exported FBX file: {os.path.basename(export_path)}\n"
                f"Saved to: {directory}"
            )
            
            # 刷新文件列表
            self.scan_directory(directory)
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Conversion Error",
                f"Failed to convert OBJ to FBX:\n{str(e)}"
            )

    def convert_fbx_to_obj(self):
        """将FBX文件转换为OBJ文件"""
        try:
            # 获取Browse文件夹路径
            directory = self.file_path_edit.text()
            if not directory or not os.path.exists(directory):
                QtWidgets.QMessageBox.warning(
                    self, "Invalid Directory",
                    "Please select a valid directory in Browse first."
                )
                return
            
            # 获取所有FBX文件
            fbx_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.fbx'):
                        fbx_files.append(os.path.join(root, file))
            
            if not fbx_files:
                QtWidgets.QMessageBox.warning(
                    self, "No FBX Files",
                    "No FBX files found in the selected directory."
                )
                return
            
            # 询问导出文件名
            export_name, ok = QtWidgets.QInputDialog.getText(
                self, "Export OBJ File",
                "Enter the name for the exported OBJ file (without extension):",
                QtWidgets.QLineEdit.Normal,
                "converted_model"
            )
            
            if not ok or not export_name:
                return  # 用户取消
            
            # 确保FBX插件已加载
            if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
                cmds.loadPlugin('fbxmaya')
            
            # 确保OBJ插件已加载
            if not cmds.pluginInfo('objExport', query=True, loaded=True):
                cmds.loadPlugin('objExport')
            
            # 保存当前场景（可选）
            current_scene = cmds.file(query=True, sceneName=True)
            
            # 导入所有FBX文件
            imported_objects = []
            for fbx_file in fbx_files:
                try:
                    # 导入FBX文件
                    cmds.file(
                        fbx_file,
                        i=True,  # 导入
                        type='FBX',
                        ignoreVersion=True,
                        options="v=0;",
                        pr=True
                    )
                    
                    # 获取最近导入的对象
                    imported_nodes = cmds.ls(assemblies=True)
                    if imported_nodes:
                        imported_objects.extend(imported_nodes)
                        
                except Exception as e:
                    print(f"Error importing {fbx_file}: {str(e)}")
                    continue
            
            if not imported_objects:
                QtWidgets.QMessageBox.warning(
                    self, "Import Failed",
                    "Failed to import any FBX files."
                )
                return
            
            # 选择所有导入的对象
            cmds.select(imported_objects, replace=True)
            
            # 设置导出路径
            export_path = os.path.join(directory, f"{export_name}.obj")
            
            # 检查文件是否已存在
            if os.path.exists(export_path):
                reply = QtWidgets.QMessageBox.question(
                    self, "File Exists",
                    f"OBJ file '{export_name}.obj' already exists.\n"
                    "Do you want to overwrite it?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No
                )
                if reply == QtWidgets.QMessageBox.No:
                    # 添加序号避免冲突
                    counter = 1
                    while os.path.exists(export_path):
                        export_path = os.path.join(directory, f"{export_name}_{counter:02d}.obj")
                        counter += 1
            
            # 导出为OBJ
            cmds.file(
                export_path,
                force=True,
                options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1",
                typ="OBJexport",
                pr=True,
                es=True
            )
            
            # 删除导入的对象（可选，恢复原始场景）
            if imported_objects:
                cmds.delete(imported_objects)
            
            # 恢复原始选择
            cmds.select(clear=True)
            
            QtWidgets.QMessageBox.information(
                self, "Conversion Complete",
                f"Successfully converted {len(fbx_files)} FBX file(s) to OBJ.\n\n"
                f"Exported OBJ file: {os.path.basename(export_path)}\n"
                f"Saved to: {directory}"
            )
            
            # 刷新文件列表
            self.scan_directory(directory)
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Conversion Error",
                f"Failed to convert FBX to OBJ:\n{str(e)}"
            )

    def check_model_files(self, directory, project_code, asset_type, asset_code):
        """检查模型文件命名是否符合规范"""
        errors = []
        
        # 支持的模型格式
        model_extensions = ['.fbx', '.obj']
        
        # 遍历目录中的文件
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                
                # 只处理支持的模型格式
                if file_ext in model_extensions:
                    file_path = os.path.join(root, file)
                    base_name = os.path.splitext(file)[0]  # 去掉扩展名
                    
                    # 解析文件名
                    # 格式：项目代码_资产类型_资产编码_模型详细命名_M_序号(可选)
                    parts = base_name.split('_')
                    
                    if len(parts) < 5 or len(parts) > 6:
                        errors.append(f"{file}: Invalid format. Expected 5-6 parts, got {len(parts)} parts")
                        continue
                    
                    # 检查各个部分
                    file_project_code = parts[0] if len(parts) > 0 else ""
                    file_asset_type = parts[1] if len(parts) > 1 else ""
                    file_asset_code = parts[2] if len(parts) > 2 else ""
                    file_model_detail = parts[3] if len(parts) > 3 else ""
                    file_phase = parts[4] if len(parts) > 4 else ""
                    
                    # 检查项目代码
                    if file_project_code != project_code:
                        errors.append(f"{file}: Project code mismatch. Expected '{project_code}', got '{file_project_code}'")
                    
                    # 检查资产类型
                    if file_asset_type != asset_type:
                        errors.append(f"{file}: Asset type mismatch. Expected '{asset_type}', got '{file_asset_type}'")
                    
                    # 检查资产编码
                    if file_asset_code != asset_code:
                        errors.append(f"{file}: Asset code mismatch. Expected '{asset_code}', got '{file_asset_code}'")
                    
                    # 检查阶段（必须是M）
                    if file_phase != 'M':
                        errors.append(f"{file}: Phase must be 'M' (Model), got '{file_phase}'")
                    
                    # 检查是否有序号（第6部分，可选）
                    if len(parts) == 6:
                        sequence_number = parts[5]
                        if not sequence_number.isdigit():
                            errors.append(f"{file}: Sequence number must be digits, got '{sequence_number}'")
                    
                    # 检查模型详细命名（不能为空）
                    if not file_model_detail or file_model_detail == "":
                        errors.append(f"{file}: Model detail name is empty")
        
        return errors

    def check_texture_files(self, directory, project_code, asset_type, asset_code):
        """检查贴图文件命名是否符合规范"""
        errors = []
        
        # 支持的贴图格式
        texture_extensions = ['.jpeg', '.jpg', '.png', '.exr', '.tga']
        
        # 贴图类型映射
        texture_type_map = {
            'B': 'BaseColor',
            'M': 'Metalness',
            'R': 'Roughness',
            'E': 'Emissive',
            'N': 'Normal',
            'H': 'Height'
        }
        
        # 遍历目录中的文件
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                
                # 只处理支持的贴图格式
                if file_ext in texture_extensions:
                    file_path = os.path.join(root, file)
                    base_name = os.path.splitext(file)[0]  # 去掉扩展名
                    
                    # 解析文件名
                    # 格式：项目代码_资产类型_资产编码_模型详细命名_M_S_贴图类型_UDIM(可选)
                    parts = base_name.split('_')
                    
                    if len(parts) < 7 or len(parts) > 8:
                        errors.append(f"{file}: Invalid format. Expected 7-8 parts, got {len(parts)} parts")
                        continue
                    
                    # 检查各个部分
                    file_project_code = parts[0] if len(parts) > 0 else ""
                    file_asset_type = parts[1] if len(parts) > 1 else ""
                    file_asset_code = parts[2] if len(parts) > 2 else ""
                    file_model_detail = parts[3] if len(parts) > 3 else ""
                    file_phase = parts[4] if len(parts) > 4 else ""
                    file_shading = parts[5] if len(parts) > 5 else ""
                    file_texture_type = parts[6] if len(parts) > 6 else ""
                    
                    # 检查项目代码
                    if file_project_code != project_code:
                        errors.append(f"{file}: Project code mismatch. Expected '{project_code}', got '{file_project_code}'")
                    
                    # 检查资产类型
                    if file_asset_type != asset_type:
                        errors.append(f"{file}: Asset type mismatch. Expected '{asset_type}', got '{file_asset_type}'")
                    
                    # 检查资产编码
                    if file_asset_code != asset_code:
                        errors.append(f"{file}: Asset code mismatch. Expected '{asset_code}', got '{file_asset_code}'")
                    
                    # 检查阶段（必须是M）
                    if file_phase != 'M':
                        errors.append(f"{file}: Phase must be 'M' (Model), got '{file_phase}'")
                    
                    # 检查是否为材质（必须是S）
                    if file_shading != 'S':
                        errors.append(f"{file}: Shading indicator must be 'S', got '{file_shading}'")
                    
                    # 检查贴图类型
                    if file_texture_type not in texture_type_map:
                        errors.append(f"{file}: Invalid texture type '{file_texture_type}'. Must be one of: {', '.join(texture_type_map.keys())}")
                    
                    # 检查模型详细命名（不能为空）
                    if not file_model_detail or file_model_detail == "":
                        errors.append(f"{file}: Model detail name is empty")
                    
                    # 检查UDIM部分（如果有）
                    if len(parts) == 8:
                        udim_part = parts[7]
                        if not udim_part.isdigit() or len(udim_part) != 4:
                            errors.append(f"{file}: UDIM must be 4 digits, got '{udim_part}'")
        
        return errors
    
    def environment_validation(self):
        """验证Maya环境是否为2024版本"""
        try:
            # 获取Maya版本信息
            maya_version = cmds.about(version=True)
            
            # 检查是否为2024版本 - 修改这里
            if maya_version.startswith("2024"):  # 修改了这里，从 "2024.2" 改为 "2024"
                # 获取更详细的版本信息
                build_version = cmds.about(version=True)
                api_version = cmds.about(api=True)
                
                # 显示验证通过的消息
                QtWidgets.QMessageBox.information(
                    self, 
                    "Environment Validation - PASSED",
                    f"Maya版本验证通过！\n\n"
                    f"当前版本: {maya_version}\n"
                    f"详细版本: {build_version}\n"
                    f"API版本: {api_version}\n\n"
                    f"环境符合要求，可以正常运行。"
                )
            else:
                # 显示错误消息 - 修改了要求的版本号
                error_msg = f"Maya版本验证失败！\n\n"
                error_msg += f"当前版本: {maya_version}\n"
                error_msg += f"要求版本: Maya 2024\n\n"  # 修改了这里，从 "Maya 2024.2" 改为 "Maya 2024"
                error_msg += "请安装Maya 2024版本以确保所有功能正常运行。\n"  # 修改了这里
                error_msg += "当前版本可能导致以下问题：\n"
                error_msg += "1. 某些功能可能无法正常工作\n"
                error_msg += "2. 兼容性问题可能导致崩溃\n"
                error_msg += "3. 性能可能不稳定\n\n"
                error_msg += "建议下载并安装Maya 2024版本。"  # 修改了这里
                
                QtWidgets.QMessageBox.critical(
                    self,
                    "Environment Validation - FAILED",
                    error_msg
                )
                
        except Exception as e:
            # 获取版本信息失败时的处理
            QtWidgets.QMessageBox.warning(
                self,
                "Environment Validation Error",
                f"无法验证Maya环境：\n{str(e)}\n\n"
                "请确保在Maya环境中运行此工具。"
            )

    def set_project_workflow(self):
        """Set Project工作流程"""
        try:
            # 获取Project Code
            project_code, ok1 = QtWidgets.QInputDialog.getText(
                self, "Project Code",
                "Enter Project Code (3 uppercase letters):",
                QtWidgets.QLineEdit.Normal,
                ""
            )
            
            if not ok1 or not project_code:
                return  # 用户取消
            
            # 验证Project Code
            project_code = project_code.upper()[:3]
            if len(project_code) != 3 or not project_code.isalpha() or not project_code.isupper():
                QtWidgets.QMessageBox.warning(self, "Invalid Input", 
                    "Please enter exactly 3 uppercase letters for Project Code.")
                return
            
            # 获取Asset Code
            asset_code, ok2 = QtWidgets.QInputDialog.getText(
                self, "Asset Code",
                "Enter Asset Code (6 uppercase letters):",
                QtWidgets.QLineEdit.Normal,
                ""
            )
            
            if not ok2 or not asset_code:
                return  # 用户取消
            
            # 验证Asset Code
            asset_code = asset_code.upper()[:6]
            if len(asset_code) != 6 or not asset_code.isalpha() or not asset_code.isupper():
                QtWidgets.QMessageBox.warning(self, "Invalid Input", 
                    "Please enter exactly 6 uppercase letters for Asset Code.")
                return
            
            # 存储到实例变量
            self.set_project_code = project_code
            self.set_asset_code = asset_code
            
            QtWidgets.QMessageBox.information(
                self, "Set Project Complete",
                f"Project Code: {project_code}\nAsset Code: {asset_code}\n\n"
                f"You can now click 'Work Log' to analyze project information."
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Set Project Error",
                f"Failed to set project: {str(e)}"
            )

    def work_log_analysis(self):
        """History Version分析功能 - 显示项目历史版本信息"""
        try:
            # 获取项目信息（优先使用Set Project设置的，其次使用菜单输入的）
            project_code = None
            asset_code = None
            
            # 首先检查是否通过Set Project设置了项目
            if hasattr(self, 'set_project_code') and hasattr(self, 'set_asset_code'):
                if self.set_project_code and self.set_asset_code:
                    project_code = self.set_project_code
                    asset_code = self.set_asset_code
            
            # 如果没有通过Set Project设置，检查是否有选择的文件
            if not project_code or not asset_code:
                selected_items = self.file_list.selectedItems()
                if selected_items:
                    # 检查选择的文件是否是ma或mb文件
                    item = selected_items[0]
                    file_path = item.data(QtCore.Qt.UserRole)
                    file_ext = os.path.splitext(file_path)[1].lower()
                    
                    if file_ext in ['.ma', '.mb']:
                        # 从文件名解析Project Code和Asset Code
                        filename = os.path.basename(file_path)
                        base_name = os.path.splitext(filename)[0]
                        parts = base_name.split('_')
                        
                        if len(parts) >= 3:
                            project_code = parts[0]  # 项目代码
                            asset_code = parts[2]   # 资产代码
                        else:
                            QtWidgets.QMessageBox.warning(
                                self, "Invalid File Name",
                                "The selected file does not match the naming convention.\n"
                                "Format should be: ProjectCode_AssetType_AssetCode_...\n"
                                f"File: {filename}"
                            )
                            return
            
            # 如果还没有获取到项目信息，检查是否有通过菜单输入的
            if not project_code or not asset_code:
                if self.project_code and self.asset_code:
                    project_code = self.project_code
                    asset_code = self.asset_code
                else:
                    QtWidgets.QMessageBox.warning(
                        self, "No Project Information",
                        "Please either:\n"
                        "1. Use 'Set Project' to enter Project Code and Asset Code, or\n"
                        "2. Select a Maya file (.ma/.mb) with proper naming convention, or\n"
                        "3. Enter Project and Asset codes through the Project menu."
                    )
                    return
            
            # 获取Browse文件夹路径
            directory = self.file_path_edit.text()
            if not directory or not os.path.exists(directory):
                QtWidgets.QMessageBox.warning(
                    self, "Invalid Directory",
                    "Please select a valid directory in Browse first."
                )
                return
            
            # 检查CSV文件是否存在
            csv_filename = "AutoSort_PM_Management_Doc.csv"
            csv_path = os.path.join(directory, csv_filename)
            
            if not os.path.exists(csv_path):
                QtWidgets.QMessageBox.warning(
                    self, "Missing File",
                    f"Could not find {csv_filename} in the selected directory.\n"
                    f"Please ensure the PM document exists."
                )
                return
            
            # 读取CSV文件并查找所有匹配的记录
            found_match = False
            project_info = {}
            all_versions = []  # 存储所有版本信息
            
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                # 跳过表头（3行）
                for i, row in enumerate(rows):
                    if i >= 3 and len(row) >= 17:  # 数据行，至少有17列
                        # CSV列索引（根据表头）：
                        # 3: Project Code, 7: Asset Code
                        csv_project_code = row[3] if len(row) > 3 else ""
                        csv_asset_code = row[7] if len(row) > 7 else ""
                        
                        if csv_project_code == project_code and csv_asset_code == asset_code:
                            found_match = True
                            
                            # 提取版本信息
                            version_info = {
                                'version': row[16] if len(row) > 16 else "",  # Version
                                'version_start_time': row[17] if len(row) > 17 else "",  # Version Start Time
                                'version_end_time': row[18] if len(row) > 18 else "",  # Version End Time
                                'phase_of_production': row[9] if len(row) > 9 else "",  # Phase Of Production
                                'company_code': row[0] if len(row) > 0 else "",  # Company Code
                                'personnel_code': row[1] if len(row) > 1 else "",  # Personnel Code
                                'manager_code': row[2] if len(row) > 2 else "",  # Manager Code
                                'asset_file_name': row[10] if len(row) > 10 else ""  # Asset File Name
                            }
                            
                            # 只收集有版本号的信息
                            if version_info['version']:
                                all_versions.append(version_info)
                            
                            # 如果是第一条匹配的记录，提取项目基本信息
                            if not project_info:
                                project_info = {
                                    'project_code': csv_project_code,
                                    'project_start_time': row[4] if len(row) > 4 else "",
                                    'project_end_time': row[5] if len(row) > 5 else "",
                                    'asset_code': csv_asset_code,
                                    'asset_type': row[8] if len(row) > 8 else "",
                                    'asset_start_time': row[14] if len(row) > 14 else "",
                                    'asset_end_time': row[15] if len(row) > 15 else "",
                                }
            
            # 清空Details列表
            self.details_list.clear()
            
            if found_match and all_versions:
                # 按版本号排序：VFN为最高，然后按数字版本排序
                def version_sort_key(v):
                    version = v['version']
                    if version == "VFN":
                        return (2, 0)  # VFN最高优先级
                    elif version.startswith("V") and version[1:].isdigit():
                        return (1, int(version[1:]))
                    else:
                        return (0, version)
                
                all_versions.sort(key=version_sort_key, reverse=True)
                
                # 获取最新版本信息
                latest_version = all_versions[0]
                
                # 在Details中显示项目信息
                self.details_list.addItem("=== Project History Version ===")
                self.details_list.addItem("")
                self.details_list.addItem("项目名称：")
                self.details_list.addItem(f"  Project Code: {project_info['project_code']}")
                self.details_list.addItem(f"  Asset Code: {project_info['asset_code']}")
                self.details_list.addItem(f"  Asset Type: {project_info['asset_type']}")
                self.details_list.addItem("")
                
                self.details_list.addItem("项目开始时间：")
                self.details_list.addItem(f"  {project_info['project_start_time'] or 'Not set'}")
                self.details_list.addItem("")
                
                self.details_list.addItem("项目结束时间：")
                self.details_list.addItem(f"  {project_info['project_end_time'] or 'Not set'}")
                self.details_list.addItem("")
                
                self.details_list.addItem("资产名称：")
                self.details_list.addItem(f"  Asset Code: {project_info['asset_code']}")
                self.details_list.addItem(f"  Asset Type: {project_info['asset_type']}")
                self.details_list.addItem("")
                
                # 显示所有版本号
                self.details_list.addItem("资产所有版本号：")
                for i, version_info in enumerate(all_versions):
                    version_display = version_info['version']
                    phase_display = version_info['phase_of_production']
                    phase_names = {
                        'M': 'Modeling',
                        'S': 'Shading', 
                        'T': 'Texturing',
                        'D': 'Rendering',
                        'R': 'Rigging',
                        'A': 'Animation'
                    }
                    phase_name = phase_names.get(phase_display, phase_display)
                    
                    if version_info.get('asset_file_name'):
                        self.details_list.addItem(f"  {i+1}. {version_display} ({phase_name}) - {version_info['asset_file_name']}")
                    else:
                        self.details_list.addItem(f"  {i+1}. {version_display} ({phase_name})")
                self.details_list.addItem("")
                
                # 显示最新版本的开始时间
                self.details_list.addItem("版本开始时间：")
                if latest_version['version_start_time']:
                    # 格式化时间显示
                    time_str = latest_version['version_start_time']
                    if len(time_str) == 14 and time_str.isdigit():
                        formatted_time = f"{time_str[0:4]}-{time_str[4:6]}-{time_str[6:8]} {time_str[8:10]}:{time_str[10:12]}:{time_str[12:14]}"
                        self.details_list.addItem(f"  Latest version ({latest_version['version']}): {formatted_time}")
                    else:
                        self.details_list.addItem(f"  Latest version ({latest_version['version']}): {time_str}")
                else:
                    self.details_list.addItem(f"  Latest version ({latest_version['version']}): Not set")
                
                # 在预览区域也显示信息
                preview_text = "History Version Analysis Results:\n\n"
                preview_text += f"Project: {project_info['project_code']}\n"
                preview_text += f"Asset: {project_info['asset_code']} ({project_info['asset_type']})\n\n"
                preview_text += f"Project Period: {project_info['project_start_time'] or 'N/A'} to {project_info['project_end_time'] or 'N/A'}\n"
                preview_text += f"Asset Period: {project_info['asset_start_time'] or 'N/A'} to {project_info['asset_end_time'] or 'N/A'}\n\n"
                preview_text += f"Total Versions: {len(all_versions)}\n"
                preview_text += f"Latest Version: {latest_version['version']}\n"
                
                if latest_version['version_start_time']:
                    time_str = latest_version['version_start_time']
                    if len(time_str) == 14 and time_str.isdigit():
                        formatted_time = f"{time_str[0:4]}-{time_str[4:6]}-{time_str[6:8]} {time_str[8:10]}:{time_str[10:12]}:{time_str[12:14]}"
                        preview_text += f"Latest Version Start Time: {formatted_time}\n"
                    else:
                        preview_text += f"Latest Version Start Time: {time_str}\n"
                
                preview_text += "\nAll Versions:\n"
                for version_info in all_versions:
                    preview_text += f"- {version_info['version']} ({version_info['phase_of_production']})"
                    if version_info.get('company_code'):
                        preview_text += f" - Company: {version_info['company_code']}"
                    if version_info.get('personnel_code'):
                        preview_text += f", Personnel: {version_info['personnel_code']}"
                    preview_text += "\n"
                
                self.preview_text.setText(preview_text)
                
            elif found_match and not all_versions:
                # 找到匹配但无版本信息
                self.details_list.addItem("=== History Version Analysis ===")
                self.details_list.addItem("")
                self.details_list.addItem("Project and Asset found, but no version information available.")
                self.details_list.addItem("")
                self.details_list.addItem(f"Project Code: {project_code}")
                self.details_list.addItem(f"Asset Code: {asset_code}")
                
                self.preview_text.setText(
                    "History Version Analysis\n\n"
                    f"Project: {project_code}\n"
                    f"Asset: {asset_code}\n\n"
                    "No version information found for this asset.\n"
                    "This asset may not have been submitted yet."
                )
                
            else:
                # 没有找到匹配的记录
                self.details_list.addItem("=== History Version Analysis ===")
                self.details_list.addItem("")
                self.details_list.addItem("No matching information found.")
                self.details_list.addItem("Please re-enter the information.")
                self.details_list.addItem("")
                self.details_list.addItem(f"Search parameters:")
                self.details_list.addItem(f"  Project Code: {project_code}")
                self.details_list.addItem(f"  Asset Code: {asset_code}")
                
                self.preview_text.setText(
                    "History Version Analysis - No Match Found\n\n"
                    f"Project Code: {project_code}\n"
                    f"Asset Code: {asset_code}\n\n"
                    "No corresponding information found in the PM document.\n"
                    "Please re-enter the information."
                )
                    
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "History Version Error",
                f"Failed to analyze history version: {str(e)}"
            )

    def show_documentation(self):
        """显示插件使用说明文档"""
        try:
            # 清空Details列表
            self.details_list.clear()
            
            # 在Details列表中显示插件功能说明
            documentation_items = [
                "=== AutoSort 插件使用说明 ===",
                "",
                "一、插件概述",
                "AutoSort是一款为Maya设计的自动化资产管理工具，",
                "主要功能包括文件管理、自动命名、材质创建、文件转换等。",
                "",
                "二、主要功能模块",
                "1. Asset Management (资产管理)",
                "   - Categorized Search: 按类别搜索文件",
                "   - Import/Export: 导入/导出模型和贴图",
                "   - Auto Import: 自动导入功能",
                "",
                "2. File Processing (文件处理)",
                "   - File Conversion: 文件格式转换 (OBJ↔FBX)",
                "",
                "3. Automation (自动化)",
                "   - Auto-Naming: 自动命名模型和贴图",
                "   - Auto-Organization: 自动整理 (模型、绑定、动画)",
                "",
                "4. Logging (日志)",
                "   - Work Plan: 工作计划和工作日志",
                "",
                "5. PM (项目管理)",
                "   - Vendor: 供应商管理 (公司、人员)",
                "   - Project: 项目管理 (项目、资产)",
                "",
                "6. Help (帮助)",
                "   - Documentation: 使用说明文档",
                "   - Runtime Check: 运行时环境验证",
                "",
                "三、主要按钮功能",
                "1. Browse: 浏览选择文件夹",
                "2. Clear All: 清空所有输入信息",
                "3. Refresh: 刷新文件列表并创建PM文档",
                "4. Pin Window: 窗口置顶/取消置顶",
                "",
                "四、使用流程",
                "1. 供应商员工流程:",
                "   - 输入Company和Personnel代码",
                "   - 设置Project、Asset等信息",
                "   - 点击Refresh创建Maya文件",
                "",
                "2. 审核人员流程:",
                "   - 输入Manager代码",
                "   - 设置Project、Asset等信息",
                "   - 点击Refresh创建PM管理文档",
                "",
                "五、文件命名规范",
                "Maya文件格式: ProjectCode_AssetType_AssetCode_Phase_CompanyCode_PersonnelCode_Version",
                "示例: PSG_C_ASDASB_M_BHJ_ASU_V008.ma",
                "",
                "六、支持的文件格式",
                "模型: .fbx, .obj, .ma, .mb, .usd, .abc",
                "贴图: .png, .jpeg, .jpg, .exr, .tga",
                "",
                "七、版本信息",
                "版本: ver.2025.12.06.01",
                "作者: Old_He"
            ]
            
            # 添加文档内容到Details列表
            for item in documentation_items:
                self.details_list.addItem(item)
            
            # 在预览区域显示详细说明
            preview_content = """AutoSort 插件使用说明

一、插件概述
AutoSort是一款专为Maya设计的自动化资产管理插件，旨在提高3D资产管理的效率和规范性。插件支持模型和贴图的自动命名、材质创建、文件转换等功能。

二、主要功能模块

1. Asset Management (资产管理)
   - Categorized Search (分类搜索): 
     * File Format: 按文件格式过滤 (.fbx, .obj, .ma等)
     * File Type: 按文件类型过滤 (Model, Rigging, Animation等)
   - Import/Export (导入/导出):
     * Import Selection: 导入选中的文件
     * Import All: 导入所有支持格式的文件
     * Combined Export: 合并导出所有模型为单个文件
     * Individual Export: 分别导出每个模型为单独文件
   - Auto Import (自动导入):
     * Compliance Check: 合规性检查，验证文件命名是否符合规范
     * Auto Import All: 自动导入所有贴图和模型并创建材质网络

2. File Processing (文件处理)
   - File Conversion (文件转换):
     * OBJ → FBX: 将OBJ文件转换为FBX格式
     * FBX → OBJ: 将FBX文件转换为OBJ格式

3. Automation (自动化)
   - Auto-Naming (自动命名):
     * 自动重命名场景中的模型或贴图文件
   - Auto-Organization (自动整理):
     * Model: 为模型自动创建材质网络
     * Rigging: 绑定功能 (待开发)
     * Animation: 动画功能 (待开发)

4. Logging (日志)
   - Work Plan (工作计划):
     * Work Log: 工作日志功能

5. PM (项目管理)
   - Vendor (供应商管理):
     * Company (Vendor): 设置公司代码 (供应商必填)
     * Personnel (Vendor): 设置人员代码 (供应商必填)
   - Project (项目管理):
     * New Project: 创建新项目 (包含所有必需字段)
     * Set Project: 设置项目工作流程

6. Help (帮助)
   - Documentation: 显示使用说明文档
   - Runtime Check: 运行时环境验证

三、界面按钮说明
1. Browse (浏览按钮): 选择要管理的文件夹
2. Clear All (清空所有): 清除所有输入的信息和代码
3. Refresh (刷新): 
   - 审核人员: 创建/更新PM管理文档
   - 供应商员工: 验证信息并创建Maya文件
4. Pin Window (置顶窗口): 将窗口置顶显示，方便操作

四、工作流程

1. 供应商员工工作流程:
   - 输入公司代码 (Company Code) 和人员代码 (Personnel Code)
   - 设置项目信息 (Project Code, Asset Code等)
   - 点击Refresh按钮，系统会验证信息并创建Maya文件
   - 可以在创建的Maya文件中进行建模、材质等工作

2. 审核人员工作流程:
   - 输入经理代码 (Manager Code)
   - 设置项目信息 (包括起止时间等)
   - 点击Refresh按钮，系统会创建PM管理文档
   - 可以查看和审核供应商提交的工作成果

五、文件命名规范
所有文件都应遵循统一的命名规范:
1. Maya文件: ProjectCode_AssetType_AssetCode_Phase_CompanyCode_PersonnelCode_Version
   示例: PSG_C_ASDASB_M_BHJ_ASU_V008.ma

2. 贴图文件: ProjectCode_AssetType_AssetCode_ModelDetail_M_S_TextureType[_UDIM]
   示例: PSG_C_ASDASB_HeadFront_M_S_B_1001.png

六、支持的格式
1. 模型文件: .fbx, .obj, .ma, .mb, .usd, .abc
2. 贴图文件: .png, .jpeg, .jpg, .exr, .tga

七、注意事项
1. 请确保在Maya 2024环境中运行本插件
2. 使用前请通过Environment Validation验证环境
3. 重要操作前请备份数据
4. 如有问题，请查看控制台输出信息

八、版本信息
版本: ver.2025.12.06.01
作者: Old_He"""
            
            self.preview_text.setText(preview_content)
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Documentation Error",
                f"无法显示文档: {str(e)}"
            )


    def showEvent(self, event):
        """窗口显示事件"""
        super(AutoSortV03, self).showEvent(event)
        self.center_window()
        
    def center_window(self):
        """居中窗口"""
        frame_geo = self.frameGeometry()
        screen_center = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
        frame_geo.moveCenter(screen_center)
        self.move(frame_geo.topLeft())

def show_ui():
    """显示UI主函数"""
    # 检查是否已有实例运行
    for widget in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(widget, AutoSortV03) and widget.objectName() == "AutoSortV03":
            widget.raise_()
            widget.activateWindow()
            return widget
    
    # 创建新实例
    window = AutoSortV03()
    window.show()
    return window

# 在Maya中直接执行
if __name__ == "__main__":
    # 创建应用实例（如果不存在）
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    window = show_ui()
