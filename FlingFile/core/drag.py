"""文件拖拽处理模块"""

from PyQt6.QtCore import QMimeData
from PyQt6.QtWidgets import QWidget
import os


class DragHandler:
    """拖拽处理器类"""
    
    def __init__(self, parent: QWidget):
        """初始化拖拽处理器
        
        Args:
            parent: 父窗口控件，用于调用on_file_dropped方法
        """
        self.parent = parent
    
    def dragEnterEvent(self, event):
        """拖拽进入事件处理
        
        Args:
            event: 拖拽事件对象
        """
        # 检查是否有URL数据
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """拖拽移动事件处理
        
        Args:
            event: 拖拽事件对象
        """
        # 检查是否有URL数据
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """拖拽释放事件处理
        
        Args:
            event: 拖拽事件对象
        """
        # 提取文件路径
        file_paths = self._extract_file_paths(event.mimeData())
        
        # 调用主窗口的on_file_dropped方法
        if file_paths and hasattr(self.parent, 'on_file_dropped'):
            self.parent.on_file_dropped(file_paths)
    
    def _extract_file_paths(self, mime_data: QMimeData) -> list:
        """从MimeData中提取有效的文件路径
        
        Args:
            mime_data: MimeData对象
            
        Returns:
            list: 有效的文件路径列表
        """
        file_paths = []
        
        # 检查是否有URL数据
        if mime_data.hasUrls():
            for url in mime_data.urls():
                # 转换为本地文件路径
                file_path = url.toLocalFile()
                
                # 过滤掉文件夹和无效路径
                if self._is_valid_file(file_path):
                    file_paths.append(file_path)
        
        return file_paths
    
    def _is_valid_file(self, path: str) -> bool:
        """检查路径是否为有效的文件
        
        Args:
            path: 文件路径
            
        Returns:
            bool: 是否为有效的文件
        """
        # 检查路径是否存在
        if not os.path.exists(path):
            return False
        
        # 检查是否为文件（不是文件夹）
        if not os.path.isfile(path):
            return False
        
        # 检查是否有访问权限
        try:
            with open(path, 'rb') as f:
                pass
            return True
        except:
            return False