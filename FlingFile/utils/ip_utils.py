"""IP工具模块"""

import socket
import platform


class IPUtils:
    """IP工具类"""
    
    @staticmethod
    def get_local_ip() -> str:
        """获取本机当前的局域网IPv4地址
        
        Returns:
            str: 本机局域网IPv4地址，如果获取失败则返回空字符串
        """
        try:
            # 优先适配Windows系统
            if platform.system() == 'Windows':
                return IPUtils._get_windows_local_ip()
            else:
                return IPUtils._get_generic_local_ip()
        except Exception as e:
            print(f"获取本地IP失败: {e}")
            return ""
    
    @staticmethod
    def _get_windows_local_ip() -> str:
        """获取Windows系统的本地IP地址
        
        Returns:
            str: 本地IP地址
        """
        try:
            # 创建一个UDP套接字
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # 连接到一个外部服务器（不会实际发送数据）
            # 这样可以获取到当前正在使用的网卡的IP地址
            sock.connect(('8.8.8.8', 80))
            
            # 获取本地IP地址
            local_ip = sock.getsockname()[0]
            
            # 关闭套接字
            sock.close()
            
            # 确保不是回环地址
            if local_ip != '127.0.0.1':
                return local_ip
            else:
                return IPUtils._get_all_interfaces_ip()
        except:
            return IPUtils._get_all_interfaces_ip()
    
    @staticmethod
    def _get_generic_local_ip() -> str:
        """获取通用系统的本地IP地址
        
        Returns:
            str: 本地IP地址
        """
        try:
            # 创建一个UDP套接字
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # 连接到一个外部服务器（不会实际发送数据）
            sock.connect(('8.8.8.8', 80))
            
            # 获取本地IP地址
            local_ip = sock.getsockname()[0]
            
            # 关闭套接字
            sock.close()
            
            # 确保不是回环地址
            if local_ip != '127.0.0.1':
                return local_ip
            else:
                return IPUtils._get_all_interfaces_ip()
        except:
            return IPUtils._get_all_interfaces_ip()
    
    @staticmethod
    def _get_all_interfaces_ip() -> str:
        """获取所有网络接口的IP地址，排除回环地址
        
        Returns:
            str: 第一个非回环地址的IP
        """
        try:
            # 获取所有网络接口
            interfaces = socket.getaddrinfo(socket.gethostname(), None)
            
            # 遍历所有接口，找到第一个非回环地址
            for info in interfaces:
                family, socktype, proto, canonname, sockaddr = info
                if family == socket.AF_INET:  # 只考虑IPv4地址
                    ip = sockaddr[0]
                    if ip != '127.0.0.1':
                        return ip
            
            return ""
        except:
            return ""