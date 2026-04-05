"""路径工具模块"""

import os
import platform
import sys
from config.settings import DEFAULT_SAVE_PATH


class PathUtils:
    """路径工具类 - 处理Windows文件路径"""
    
    @staticmethod
    def get_default_save_path() -> str:
        """获取默认保存路径
        
        读取 config/settings.py 中的 DEFAULT_SAVE_PATH，
        并将其设置为程序根目录下的对应文件夹
        
        Returns:
            str: 默认保存路径
        """
        try:
            # 检测是否在PyInstaller打包环境中运行
            if getattr(sys, 'frozen', False):
                # PyInstaller环境，使用exe所在目录
                root_dir = os.path.dirname(sys.executable)
            else:
                # 开发环境，使用源码目录
                root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # 构建默认保存路径
            save_path = os.path.join(root_dir, DEFAULT_SAVE_PATH)
            
            # 确保目录存在
            PathUtils.ensure_dir(save_path)
            
            return save_path
        except Exception as e:
            print(f"获取默认保存路径失败: {e}")
            # 失败时返回当前目录
            return os.getcwd()
    
    @staticmethod
    def ensure_dir(directory: str) -> bool:
        """确保目录存在，如果不存在则创建
        
        Args:
            directory: 目录路径
            
        Returns:
            bool: 是否成功
        """
        try:
            if not os.path.exists(directory):
                # 创建目录，包括所有中间目录
                os.makedirs(directory, exist_ok=True)
                
                # 验证目录是否创建成功
                if os.path.exists(directory) and os.path.isdir(directory):
                    return True
                else:
                    return False
            else:
                # 目录已存在，检查是否为目录
                if os.path.isdir(directory):
                    return True
                else:
                    return False
        except Exception as e:
            print(f"创建目录失败: {e}")
            return False
    
    @staticmethod
    def is_valid_path(path: str) -> bool:
        """检查路径是否合法
        
        Args:
            path: 要检查的路径
            
        Returns:
            bool: 路径是否合法
        """
        try:
            # 检查路径是否包含无效字符（Windows系统）
            if platform.system() == 'Windows':
                invalid_chars = '\\/:*?"<>|'
                for char in invalid_chars:
                    if char in path:
                        return False
            
            # 尝试规范化路径
            normalized_path = os.path.normpath(path)
            
            # 检查路径长度（Windows路径长度限制）
            if platform.system() == 'Windows' and len(normalized_path) > 260:
                return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def has_write_permission(path: str) -> bool:
        """检查路径是否有写入权限
        
        Args:
            path: 要检查的路径
            
        Returns:
            bool: 是否有写入权限
        """
        try:
            # 如果路径不存在，检查其父目录
            if not os.path.exists(path):
                parent_dir = os.path.dirname(path)
                if not parent_dir:
                    parent_dir = os.getcwd()
                path = parent_dir
            
            # 检查是否有写入权限
            return os.access(path, os.W_OK)
        except Exception:
            return False