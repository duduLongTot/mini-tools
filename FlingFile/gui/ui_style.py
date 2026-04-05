"""窗口样式工具模块"""


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QScreen


class UIStyle:
    """UI样式工具类"""
    
    @staticmethod
    def set_window_always_on_top(window: QWidget, always_on_top: bool = True):
        """设置窗口置顶
        
        Args:
            window: 窗口控件
            always_on_top: 是否置顶
        """
        if always_on_top:
            window.setWindowFlags(window.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            window.setWindowFlags(window.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        window.show()
    
    @staticmethod
    def set_window_borderless(window: QWidget, borderless: bool = True):
        """设置窗口无边框
        
        Args:
            window: 窗口控件
            borderless: 是否无边框
        """
        if borderless:
            window.setWindowFlags(window.windowFlags() | Qt.WindowType.FramelessWindowHint)
        else:
            window.setWindowFlags(window.windowFlags() & ~Qt.WindowType.FramelessWindowHint)
        window.show()
    
    @staticmethod
    def set_window_opacity(window: QWidget, opacity: float):
        """设置窗口透明度
        
        Args:
            window: 窗口控件
            opacity: 透明度值 (0.0-1.0)
        """
        # 确保透明度值在有效范围内
        opacity = max(0.0, min(1.0, opacity))
        window.setWindowOpacity(opacity)
    
    @staticmethod
    def get_screen_resolution() -> tuple:
        """获取屏幕分辨率
        
        Returns:
            tuple: (宽度, 高度)
        """
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            return geometry.width(), geometry.height()
        return 1920, 1080  # 默认值
    
    @staticmethod
    def get_screen_geometry():
        """获取屏幕几何信息
        
        Returns:
            QRect: 屏幕几何信息
        """
        screen = QApplication.primaryScreen()
        if screen:
            return screen.geometry()
        return None
    
    @staticmethod
    def center_window(window: QWidget):
        """居中窗口
        
        Args:
            window: 窗口控件
        """
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            window_geometry = window.geometry()
            x = (screen_geometry.width() - window_geometry.width()) // 2
            y = (screen_geometry.height() - window_geometry.height()) // 2
            window.move(x, y)