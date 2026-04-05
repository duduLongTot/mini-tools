"""悬浮窗主窗口模块"""

import os

from PyQt6.QtCore import Qt, QPoint, QEvent, QCoreApplication
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QMenu, QSystemTrayIcon, QProgressBar
from PyQt6.QtGui import QMouseEvent, QFont, QIcon, QPixmap, QAction

from config.settings import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_OPACITY, WINDOW_ALWAYS_ON_TOP, WINDOW_TITLE
from gui.ui_style import UIStyle
from core.drag import DragHandler


class FloatingWindow(QWidget):
    """悬浮窗主窗口类"""
    
    def __init__(self):
        """初始化悬浮窗"""
        super().__init__()
        
        self.init_window()
        self.drag_handler = DragHandler(self)
        
        self.dragging = False
        self.drag_position = QPoint()
        self.current_mouse_pos = QPoint(0, 0)
        self.fling_triggered = False  # 抛扔触发标志
        
        # 初始化提示标签
        self.init_label()
        
        # 初始化进度条
        self.init_progress_bar()
        
        # 初始化控制按钮
        self.init_control_buttons()
        
        # 初始化系统托盘
        self.init_system_tray()
        
    def init_window(self):
        """初始化窗口设置"""
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle(WINDOW_TITLE)
        
        # 根据配置决定是否置顶
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if WINDOW_ALWAYS_ON_TOP:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        
        # 设置窗口透明度
        self.setWindowOpacity(WINDOW_OPACITY)
        
        # 设置半透明深色背景
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 0.7);
                border-radius: 10px;
            }
        """)
        
        self.setMouseTracking(True)
        # 启用窗口的文件拖放功能
        self.setAcceptDrops(True)
        UIStyle.center_window(self)
    

    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件处理
        
        Args:
            event: 鼠标事件对象
        """
        global_pos = event.globalPosition()
        self.current_mouse_pos = QPoint(int(global_pos.x()), int(global_pos.y()))

        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            # 检查窗口是否超出屏幕边界，触发抛扔发送
            self.check_window_boundary()
            event.accept()
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
    
    def changeEvent(self, event):
        """窗口状态变化事件处理
        
        Args:
            event: 事件对象
        """
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMinimized():
                # 当窗口最小化时，隐藏到托盘
                self.hide()
                event.accept()
    
    def dragEnterEvent(self, event):
        self.drag_handler.dragEnterEvent(event)
    
    def dragMoveEvent(self, event):
        self.drag_handler.dragMoveEvent(event)
    
    def dropEvent(self, event):
        # 调用拖拽处理器的dropEvent方法
        self.drag_handler.dropEvent(event)
        # 确保调用应用的on_file_dropped方法
        if hasattr(self, 'on_file_dropped'):
            # 提取文件路径
            file_paths = self.drag_handler._extract_file_paths(event.mimeData())
            if file_paths:
                self.on_file_dropped(file_paths)
    
    def on_file_dropped(self, file_paths: list):
        """文件拖拽到窗口时的处理
        
        Args:
            file_paths: 拖拽的文件路径列表
        """
        print(f"Files dropped: {file_paths}")
        # 隐藏进度条
        self.progress_bar.hide()
        # 更新窗口文字，显示已拖入的文件名
        if file_paths:
            # 只显示第一个文件名，避免文字过多
            file_name = os.path.basename(file_paths[0])
            if len(file_paths) > 1:
                self.label.setText(f"已拖入 {len(file_paths)} 个文件\n第一个: {file_name}")
            else:
                self.label.setText(f"已拖入文件:\n{file_name}")
        else:
            self.label.setText("将文件拖入此处，\n甩出屏幕即可发送")
        # 确保标签显示在最前面
        self.label.raise_()
    
    def get_mouse_position(self) -> QPoint:
        return self.current_mouse_pos
    
    def init_label(self):
        """初始化提示标签"""
        # 创建提示标签
        self.label = QLabel("将文件拖入此处，\n甩出屏幕即可发送", self)
        
        # 设置标签样式
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setGeometry(10, 10, WINDOW_WIDTH - 20, WINDOW_HEIGHT - 40)
        
        # 设置字体
        font = QFont("Microsoft YaHei", 10, QFont.Weight.Normal)
        self.label.setFont(font)
        
        # 设置文字颜色为白色
        self.label.setStyleSheet("color: white;")
        
        # 确保标签显示在最前面
        self.label.raise_()
    
    def init_progress_bar(self):
        """初始化进度条"""
        # 创建进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(10, WINDOW_HEIGHT - 30, WINDOW_WIDTH - 20, 15)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        # 设置进度条样式
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 5px;
                background-color: rgba(50, 50, 50, 0.5);
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)
        
        # 默认隐藏进度条
        self.progress_bar.hide()
        
        # 确保进度条显示在标签下方
        self.label.raise_()

    def init_control_buttons(self):
        """初始化控制按钮"""
        # 创建最小化按钮
        self.minimize_button = QPushButton(self)
        self.minimize_button.setText('—')
        self.minimize_button.setGeometry(WINDOW_WIDTH - 40, 5, 15, 15)
        self.minimize_button.setStyleSheet('''
            QPushButton {
                color: white;
                background-color: transparent;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid white;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: gray;
            }
        ''')
        self.minimize_button.clicked.connect(self.minimize_to_tray)
        
        # 创建关闭按钮
        self.close_button = QPushButton(self)
        self.close_button.setText('×')
        self.close_button.setGeometry(WINDOW_WIDTH - 20, 5, 15, 15)
        self.close_button.setStyleSheet('''
            QPushButton {
                color: white;
                background-color: transparent;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid white;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: red;
            }
        ''')
        self.close_button.clicked.connect(self._close_button_clicked)
        # 设置按钮的尺寸
        self.close_button.setFixedSize(15, 15)

    def _firewall_button_clicked(self):
        """防火墙放行按钮点击事件"""
        # 导入必要的库
        import subprocess
        import sys
        import os
        import ctypes
        from config.settings import UDP_PORT, TCP_PORT
        
        # 检查是否为Windows系统
        if os.name != 'nt':
            print("仅支持Windows系统进行防火墙放行")
            return
        
        # 检查是否已具有管理员权限
        if ctypes.windll.shell32.IsUserAnAdmin():
            # 以管理员权限运行时，执行防火墙放行规则添加
            try:
                # 添加UDP端口防火墙规则
                udp_rule_cmd = [
                    'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                    f'name=FlingFile_UDP_{UDP_PORT}',
                    f'dir=in',
                    'action=allow',
                    'protocol=UDP',
                    f'localport={UDP_PORT}'
                ]
                result_udp_in = subprocess.run(udp_rule_cmd, capture_output=True, text=True, shell=True)
                print(f"UDP入站规则添加结果: {result_udp_in.returncode}, 输出: {result_udp_in.stdout}, 错误: {result_udp_in.stderr}")
                
                udp_rule_out_cmd = [
                    'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                    f'name=FlingFile_UDP_{UDP_PORT}_Out',
                    f'dir=out',
                    'action=allow',
                    'protocol=UDP',
                    f'localport={UDP_PORT}'
                ]
                result_udp_out = subprocess.run(udp_rule_out_cmd, capture_output=True, text=True, shell=True)
                print(f"UDP出站规则添加结果: {result_udp_out.returncode}, 输出: {result_udp_out.stdout}, 错误: {result_udp_out.stderr}")
                
                # 添加TCP端口防火墙规则
                tcp_rule_cmd = [
                    'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                    f'name=FlingFile_TCP_{TCP_PORT}',
                    f'dir=in',
                    'action=allow',
                    'protocol=TCP',
                    f'localport={TCP_PORT}'
                ]
                result_tcp_in = subprocess.run(tcp_rule_cmd, capture_output=True, text=True, shell=True)
                print(f"TCP入站规则添加结果: {result_tcp_in.returncode}, 输出: {result_tcp_in.stdout}, 错误: {result_tcp_in.stderr}")
                
                tcp_rule_out_cmd = [
                    'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                    f'name=FlingFile_TCP_{TCP_PORT}_Out',
                    f'dir=out',
                    'action=allow',
                    'protocol=TCP',
                    f'localport={TCP_PORT}'
                ]
                result_tcp_out = subprocess.run(tcp_rule_out_cmd, capture_output=True, text=True, shell=True)
                print(f"TCP出站规则添加结果: {result_tcp_out.returncode}, 输出: {result_tcp_out.stdout}, 错误: {result_tcp_out.stderr}")
                
                print("防火墙规则添加完成")
                # 显示提示信息
                from PyQt6.QtWidgets import QMessageBox
                msg_box = QMessageBox()
                msg_box.setWindowTitle("防火墙放行")
                msg_box.setText("已放行防火墙，请正常启动程序使用")
                msg_box.exec()
                
                # 退出管理员进程
                QCoreApplication.quit()
                
            except Exception as e:
                print(f"添加防火墙规则失败: {e}")
        else:
            # 没有管理员权限，请求提升权限
            try:
                # 显示提示信息
                from PyQt6.QtWidgets import QMessageBox
                msg_box = QMessageBox()
                msg_box.setWindowTitle("权限提示")
                msg_box.setText("需要管理员权限来放行防火墙，请在弹出的对话框中选择'是'以继续")
                msg_box.exec()
                
                # 以管理员权限重新启动程序
                script = os.path.abspath(sys.argv[0])
                params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]]) + ' --firewall-mode'
                cmd = f'"{script}" {params}'
                
                # 使用shell=True来请求管理员权限
                proc_info = ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, cmd, None, 1
                )
                
                if proc_info <= 32:
                    print("请求管理员权限失败")
                else:
                    print("正在以管理员权限启动程序...")
                    # 退出当前进程
                    QCoreApplication.quit()
                    
            except Exception as e:
                print(f"请求管理员权限失败: {e}")
    
    def _close_button_clicked(self, event):
        """关闭按钮点击事件"""
        # 通知主应用关闭服务
        if hasattr(self, 'on_close'):
            try:
                self.on_close()
            except Exception as e:
                print(f"关闭回调执行失败: {e}")
        # 退出应用
        QCoreApplication.quit()
    
    def init_system_tray(self):
        """初始化系统托盘"""
        # 检查系统是否支持系统托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("系统不支持系统托盘功能")
            return
        
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 创建一个简单的图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.cyan)
        self.tray_icon.setIcon(QIcon(pixmap))
        
        # 设置托盘图标提示
        self.tray_icon.setToolTip("FlingFile")
        
        # 创建托盘菜单
        self.tray_menu = QMenu(self)
        
        # 显示窗口动作
        self.show_action = QAction("显示窗口", self)
        self.show_action.triggered.connect(self.show_window)
        
        # 隐藏窗口动作
        self.hide_action = QAction("隐藏窗口", self)
        self.hide_action.triggered.connect(self.hide)
        
        # 退出动作
        self.quit_action = QAction("退出", self)
        self.quit_action.triggered.connect(self.quit_application)
        
        # 添加动作到菜单
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.hide_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.quit_action)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # 连接托盘图标激活信号
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
        print("系统托盘已初始化")
    
    def minimize_to_tray(self):
        """最小化到系统托盘"""
        self.hide()
        print("窗口已最小化到系统托盘")
    

    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.fling_triggered = False  # 重置抛扔触发标志
            event.accept()
    
    def check_window_boundary(self):
        """检查窗口是否超出屏幕边界
        
        当窗口移动到屏幕边界外时，触发抛扔发送逻辑
        """
        # 如果已经触发过抛扔，不再重复触发
        if self.fling_triggered:
            return
        
        # 获取屏幕几何信息
        screen_geometry = self.screen().geometry()
        window_geometry = self.geometry()
        
        # 检查窗口是否超出屏幕边界
        if (window_geometry.left() < -20 or 
            window_geometry.right() > screen_geometry.width() + 20 or 
            window_geometry.top() < -20 or 
            window_geometry.bottom() > screen_geometry.height() + 20):
            # 触发抛扔发送
            if hasattr(self, 'on_fling'):
                try:
                    self.on_fling()
                    self.fling_triggered = True  # 设置抛扔触发标志
                except Exception as e:
                    print(f"抛扔发送回调执行失败: {e}")
            # 触发后将窗口移回屏幕内
            self.move(
                max(0, min(window_geometry.x(), screen_geometry.width() - window_geometry.width())),
                max(0, min(window_geometry.y(), screen_geometry.height() - window_geometry.height()))
            )
    
    def show_window(self):
        """显示窗口"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def show_progress(self, value):
        """显示进度条
        
        Args:
            value: 进度值 (0-100)
        """
        # 直接更新UI组件（在主线程中）
        self.progress_bar.setValue(value)
        if not self.progress_bar.isVisible():
            self.progress_bar.show()
        # 确保进度条显示在前面
        self.progress_bar.raise_()
        # 标签显示在进度条上方
        self.label.raise_()
    
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.hide()
    
    def on_tray_icon_activated(self, reason):
        """托盘图标激活事件处理
        
        Args:
            reason: 激活原因
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 单击托盘图标，切换窗口显示/隐藏状态
            if self.isVisible():
                self.hide()
            else:
                self.show_window()
    
    def quit_application(self):
        """退出应用"""
        # 通知主应用关闭服务
        if hasattr(self, 'on_close'):
            try:
                self.on_close()
            except Exception as e:
                print(f"关闭回调执行失败: {e}")
        # 退出应用
        QCoreApplication.quit()
    
    def closeEvent(self, event):
        """窗口关闭事件处理
        
        Args:
            event: 关闭事件对象
        """
        # 直接退出应用，而不是最小化到托盘
        # 通知主应用关闭服务
        if hasattr(self, 'on_close'):
            try:
                self.on_close()
            except Exception as e:
                print(f"关闭回调执行失败: {e}")
        # 接受关闭事件，让应用退出
        event.accept()