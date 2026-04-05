"""抛扔检测模块"""

from config.settings import SCREEN_MARGIN


class FlingDetector:
    """抛扔检测器类"""
    
    @staticmethod
    def is_fling_out(mouse_x: int, mouse_y: int, screen_width: int, screen_height: int) -> bool:
        """判断鼠标是否抛出屏幕边界
        
        Args:
            mouse_x: 鼠标x坐标
            mouse_y: 鼠标y坐标
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            
        Returns:
            bool: 是否抛出屏幕边界
        """
        # 检查鼠标是否超出屏幕左边界
        if mouse_x < -SCREEN_MARGIN:
            return True
        
        # 检查鼠标是否超出屏幕右边界
        if mouse_x > screen_width + SCREEN_MARGIN:
            return True
        
        # 检查鼠标是否超出屏幕上边界
        if mouse_y < -SCREEN_MARGIN:
            return True
        
        # 检查鼠标是否超出屏幕下边界
        if mouse_y > screen_height + SCREEN_MARGIN:
            return True
        
        # 未超出屏幕边界
        return False