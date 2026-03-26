# _*_ coding:utf-8 _*_
__author__ = 'Old_He'
################################################################################
# AutoSort V3.0是一款为Autodesk Maya 2024设计的专业资产管理插件，旨在提升3D资产管理的
# 效率和规范性。该插件集成了文件管理、自动命名、材质创建、文件转换、项目管理等多项功能，
# 适用于游戏开发、影视制作、三维动画等领域的资产管理工作。
################################################################################

import os
import pymel.core as pm

class MayaAutoSortTool:
    def __init__(self):  # 初始化函数
        self.toolShelf = 'Tool'
        self.autoSortTool = 'AutoSort Tool'
        self.mayaAutoSortTool = 'AutoSort_Tool_Maya'
        self.ConflictWarningWindow = 'Conflict warning window'
        self.windowText = '冲突警告'
        self.tool_rack()  # 创建工具架函数

    def warning_of_cnflict(self):  # 创建冲突警告弹窗
        self.window = pm.window(self.ConflictWarningWindow, title=self.windowText, widthHeight=(250, 30))
        # 创建一个窗口
        with pm.columnLayout():
            pm.iconTextButton(style='textOnly', label='工具架按钮命名冲突，请删除后重试！')
            # 创建一个窗口，只显示文字，文字为"工具架按钮命名冲突，请删除后重试！"
        self.window.show()  # 显示窗口

    def tool_rack(self):  # 创建工具架
        self.shelfNames = pm.shelfTabLayout('ShelfLayout', q=True, tl=True)  # 获取Maya所有工具架的名称
        if not self.toolShelf in self.shelfNames:  # 如果没有'Tool'
            pm.shelfLayout(self.toolShelf, p='ShelfLayout')  # 新建一个"Tool"选项卡
            self.tool_shelf_button()  # 创建子工具按钮
        else:
            self.toolHolderButton = pm.shelfLayout(self.toolShelf, q=True, ca=True)  # 获取选项卡所有子按钮
            if self.toolHolderButton is None:  # 如果子按钮等于None
                self.tool_shelf_button()  # 创建子按钮
            else:  # 否则
                if not self.autoSortTool in self.toolHolderButton:  # 如果没有叫'AutoSort Tool'的子按钮
                    self.tool_shelf_button()  # 创建子工具按钮
                else:  # 否则
                    self.warning_of_cnflict()  # 创建冲突警告窗口

    def tool_shelf_button(self):  # 创建子工具按钮
        mayaPath = os.environ.get('MAYA_LOCATION')  # 获取maya安装路径
        # 指定AutoSort工具的具体路径
        tool_dir = os.path.join(mayaPath, 'bin', 'plug-ins', 'Old_He_AutoSort_Tool')
        iconPath = os.path.join(tool_dir, 'Maya_AutoSort.png')
        
        # 工具命令 - 加载AutoSort工具
        command = f"""
# _*_ coding:utf-8 _*_
import sys
import os

# 添加工具路径到系统路径
tool_dir = r"{tool_dir}"
if tool_dir not in sys.path:
    sys.path.append(tool_dir)

try:
    # 尝试导入AutoSort工具模块
    try:
        # 首先尝试直接导入AutoSort_Tool_Maya
        import AutoSort_Tool_Maya
        from AutoSort_Tool_Maya import show_ui
        module_name = "AutoSort_Tool_Maya"
    except ImportError as e:
        # 如果导入失败，尝试其他可能的模块名
        try:
            # 列出目录中的文件来查找正确的模块
            files = os.listdir(tool_dir) if os.path.exists(tool_dir) else []
            python_files = [f for f in files if f.endswith('.py')]
            print("目录中的Python文件:", python_files)
            
            # 尝试重新加载sys.path
            if tool_dir in sys.path:
                sys.path.remove(tool_dir)
            sys.path.insert(0, tool_dir)
            
            # 再次尝试导入
            import AutoSort_Tool_Maya
            from AutoSort_Tool_Maya import show_ui
            module_name = "AutoSort_Tool_Maya"
            
        except ImportError:
            # 如果所有尝试都失败，显示错误信息
            error_files = ", ".join(python_files) if 'python_files' in locals() else "无法访问目录"
            raise ImportError(f"无法找到AutoSort工具模块。工具目录: {{tool_dir}}，目录中的文件: {{error_files}}")
    
    # 声明全局变量
    global auto_sort_ui
    
    # 检查是否已经存在实例，如果存在则删除
    if 'auto_sort_ui' in globals():
        try:
            auto_sort_ui.close()
            auto_sort_ui.deleteLater()
            # 设置为None以释放引用
            auto_sort_ui = None
        except:
            pass
    
    # 创建新的UI实例
    auto_sort_ui = show_ui()
    
except Exception as e:
    import traceback
    error_msg = "加载AutoSort工具时出错:\\n{{}}\\n{{}}".format(str(e), traceback.format_exc())
    print(error_msg)
    from maya import cmds
    cmds.confirmDialog(title="错误", message=error_msg, button=["确定"])
"""
        
        # 检查图标文件是否存在，如果不存在使用默认图标
        if not os.path.exists(iconPath):
            print(f"警告: 图标文件不存在: {iconPath}")
            print(f"图标文件路径: {iconPath}")
            print(f"工具目录: {tool_dir}")
            if os.path.exists(tool_dir):
                print(f"工具目录内容: {os.listdir(tool_dir)}")
            # 使用None让Maya使用默认图标
            iconPath = None
        
        pm.shelfButton(  # 创建一个工具架按钮
            self.autoSortTool,
            p=self.toolShelf,
            i=iconPath,
            l='AutoSort工具',
            command=command
        )

# 创建工具实例
try:
    MayaAutoSortTool()
    print("AutoSort工具安装完成")
except Exception as e:
    print(f"安装AutoSort工具时出错: {e}")
