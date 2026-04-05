"""UDP打洞模块 - 用于局域网内P2P穿透"""

import socket
import threading
import time
from config.settings import UDP_PORT, BUFF_SIZE


class UDPHolePuncher:
    """UDP打洞器类 - 实现局域网内P2P穿透"""
    
    def __init__(self):
        """初始化UDP打洞器"""
        # UDP套接字
        self.sock = None
        # 本地IP地址
        self.local_ip = ""
        # 本地端口
        self.local_port = 0
        # 运行状态
        self.running = False
        # 接收线程
        self.receive_thread = None
        # 心跳线程
        self.heartbeat_thread = None
        # 对端地址列表
        self.peer_addresses = set()
        # 回调函数
        self.on_receive_callback = None
        # 对端探测回调
        self.on_peer_detected_callback = None
    
    def start(self):
        """启动UDP打洞器
        
        Returns:
            bool: 是否启动成功
        """
        try:
            # 创建UDP套接字
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # 绑定到固定端口，确保能够接收到广播消息
            self.sock.bind(('', UDP_PORT))
            
            # 获取本地IP和实际绑定的端口
            self.local_ip = self._get_local_ip()
            self.local_port = UDP_PORT
            
            # 设置运行状态
            self.running = True
            
            # 启动接收线程
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            # 启动心跳线程
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.heartbeat_thread.start()
            
            print(f"UDP打洞器启动成功，本地IP: {self.local_ip}, 端口: {self.local_port}")
            return True
        except Exception as e:
            print(f"UDP打洞器启动失败: {e}")
            self.stop()
            return False
    
    def stop(self):
        """停止UDP打洞器"""
        try:
            # 设置运行状态
            self.running = False
            
            # 等待线程结束
            if self.receive_thread and self.receive_thread.is_alive():
                self.receive_thread.join(timeout=2)
            
            if self.heartbeat_thread and self.heartbeat_thread.is_alive():
                self.heartbeat_thread.join(timeout=2)
            
            # 关闭套接字
            if self.sock:
                self.sock.close()
                self.sock = None
            
            # 清空对端地址列表
            self.peer_addresses.clear()
            
            print("UDP打洞器已停止")
        except Exception as e:
            print(f"停止UDP打洞器失败: {e}")
    
    def send(self, data: bytes, address: tuple):
        """发送数据
        
        Args:
            data: 要发送的数据
            address: 目标地址 (ip, port)
            
        Returns:
            bool: 是否发送成功
        """
        try:
            if self.sock and self.running:
                self.sock.sendto(data, address)
                # 将目标地址添加到对端列表
                self.peer_addresses.add(address)
                return True
            return False
        except Exception as e:
            print(f"发送数据失败: {e}")
            return False
    
    def broadcast(self, data: bytes):
        """广播数据
        
        Args:
            data: 要广播的数据
        """
        try:
            # 构建广播地址 - 广播到UDP_PORT端口，这样其他实例可以接收到
            broadcast_address = ('255.255.255.255', UDP_PORT)  # 使用配置的UDP端口进行广播
            
            # 启用广播
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # 发送广播
            self.sock.sendto(data, broadcast_address)
            
            # 同时发送到本地网络的广播地址（针对某些网络环境）
            # 获取本地网络的广播地址
            local_ip = self._get_local_ip()
            # 构建本地网络广播地址（假设子网掩码为255.255.255.0）
            network_prefix = '.'.join(local_ip.split('.')[:3])
            local_broadcast = (f"{network_prefix}.255", UDP_PORT)
            self.sock.sendto(data, local_broadcast)
        
            # 禁用广播
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 0)
        except Exception as e:
            print(f"广播数据失败: {e}")
    
    def set_on_receive_callback(self, callback):
        """设置接收回调函数
        
        Args:
            callback: 回调函数，格式为 callback(data: bytes, address: tuple)
        """
        self.on_receive_callback = callback
    
    def set_on_peer_detected_callback(self, callback):
        """设置对端检测回调函数
        
        Args:
            callback: 回调函数，格式为 callback(address: tuple)
        """
        self.on_peer_detected_callback = callback
    
    def _get_local_ip(self) -> str:
        """获取本地IP地址
        
        Returns:
            str: 本地IP地址
        """
        try:
            # 创建临时套接字获取本地IP
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_sock.connect(('8.8.8.8', 80))
            local_ip = temp_sock.getsockname()[0]
            temp_sock.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    def _receive_loop(self):
        """接收数据循环"""
        while self.running:
            try:
                # 设置超时，避免阻塞
                self.sock.settimeout(1.0)
                
                # 接收数据
                data, address = self.sock.recvfrom(BUFF_SIZE)
                
                # 处理接收到的数据
                self._handle_received_data(data, address)
                
            except socket.timeout:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                if self.running:
                    print(f"接收数据失败: {e}")
                break
    
    def _handle_received_data(self, data: bytes, address: tuple):
        """处理接收到的数据
        
        Args:
            data: 接收到的数据
            address: 发送方地址
        """
        # 确保地址是元组格式
        if isinstance(address, tuple) and len(address) == 2:
            # 将地址添加到对端列表
            if address not in self.peer_addresses:
                self.peer_addresses.add(address)
                # 触发对端检测回调
                if self.on_peer_detected_callback:
                    try:
                        self.on_peer_detected_callback(address)
                    except Exception as e:
                        print(f"对端检测回调失败: {e}")
            
            # 触发接收回调
            if self.on_receive_callback:
                try:
                    self.on_receive_callback(data, address)
                except Exception as e:
                    print(f"接收回调失败: {e}")
    
    def _heartbeat_loop(self):
        """心跳循环 - 保持连接"""
        while self.running:
            try:
                # 发送心跳包
                heartbeat_data = b'HEARTBEAT'
                for address in list(self.peer_addresses):
                    self.send(heartbeat_data, address)
                
                # 等待一段时间
                time.sleep(5)
            except Exception as e:
                if self.running:
                    print(f"心跳发送失败: {e}")
                break
    
    def get_peer_addresses(self) -> list:
        """获取所有对端地址
        
        Returns:
            list: 对端地址列表
        """
        return list(self.peer_addresses)
    
    def is_running(self) -> bool:
        """检查是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        return self.running