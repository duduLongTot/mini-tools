"""FlingFile 主入口文件"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

# 导入自定义模块
from gui.window import FloatingWindow
from network.udp_hole import UDPHolePuncher
from network.tcp_transfer import TCPFileTransfer
from core.fling_detector import FlingDetector
from utils.ip_utils import IPUtils
from config.settings import UDP_PORT, TCP_PORT


class SignalHandler(QObject):
    """信号处理器 - 用于在主线程中更新UI"""
    
    # 定义信号
    transfer_start_signal = pyqtSignal(str, int, tuple, bool)
    transfer_progress_signal = pyqtSignal(str, int, tuple, bool)
    transfer_complete_signal = pyqtSignal(str, str, tuple, bool)
    transfer_error_signal = pyqtSignal(str, tuple, bool)
    



class FlingFileApp:
    """FlingFile 应用主类"""
    
    def __init__(self):
        """初始化应用"""
        # 创建Qt应用
        self.app = QApplication(sys.argv)
        
        # 创建信号处理器
        self.signal_handler = SignalHandler()
        
        # 创建悬浮窗
        self.window = FloatingWindow()
        
        # 创建UDP打洞器
        self.udp_puncher = UDPHolePuncher()
        
        # 创建TCP文件传输器
        self.tcp_transfer = TCPFileTransfer()
        
        # 已发现的设备列表
        self.discovered_devices = set()
        
        # 当前拖拽的文件列表
        self.current_files = []
        
        # 初始化
        self._init_components()
    
    def _init_components(self):
        """初始化组件"""
        # 连接信号
        self._connect_signals()
        
        # 绑定窗口关闭回调
        self.window.on_close = self.on_window_close
        
        # 启动服务
        self._start_services()
    
    def _connect_signals(self):
        """连接信号和回调"""
        # 设置窗口的文件拖拽回调
        self.window.on_file_dropped = self.on_file_dropped
        
        # 设置窗口的抛扔回调
        self.window.on_fling = self.on_fling
        
        # 设置UDP打洞器回调
        self.udp_puncher.set_on_receive_callback(self.on_udp_receive)
        self.udp_puncher.set_on_peer_detected_callback(self.on_peer_detected)
        
        # 设置TCP传输器回调 - 使用信号处理器避免跨线程UI更新
        self.tcp_transfer.set_on_transfer_start_callback(self._emit_transfer_start)
        self.tcp_transfer.set_on_transfer_progress_callback(self._emit_transfer_progress)
        self.tcp_transfer.set_on_transfer_complete_callback(self._emit_transfer_complete)
        self.tcp_transfer.set_on_transfer_error_callback(self._emit_transfer_error)
        
        # 连接信号处理器到对应的槽
        self.signal_handler.transfer_start_signal.connect(self.on_transfer_start)
        self.signal_handler.transfer_progress_signal.connect(self.on_transfer_progress)
        self.signal_handler.transfer_complete_signal.connect(self.on_transfer_complete)
        self.signal_handler.transfer_error_signal.connect(self.on_transfer_error)
    
    def _start_services(self):
        """启动服务"""
        # 启动UDP打洞服务
        if not self.udp_puncher.start():
            print("警告: UDP打洞服务启动失败")
        
        # 启动TCP文件接收服务端
        if not self.tcp_transfer.start_server():
            print("警告: TCP文件接收服务端启动失败")
        
        # 发送广播，发现网络中的其他设备
        self._discover_devices()
    
    def _discover_devices(self):
        """发现网络中的设备"""
        # 发送设备发现广播，包含本地TCP端口
        local_ip = IPUtils.get_local_ip()
        # 获取TCP服务端的端口
        tcp_port = getattr(self.tcp_transfer, 'local_port', TCP_PORT)
        discover_message = f"FLINGFILE_DISCOVER:{local_ip}:{tcp_port}".encode('utf-8')
        self.udp_puncher.broadcast(discover_message)
        print(f"发送设备发现广播，本地IP: {local_ip}, TCP端口: {tcp_port}")
    
    def on_file_dropped(self, file_paths: list):
        """文件拖拽到窗口时的处理
        
        Args:
            file_paths: 拖拽的文件路径列表
        """
        print(f"文件拖入: {file_paths}")
        self.current_files = file_paths
        
        # 更新窗口文字，显示已拖入的文件名
        if file_paths:
            # 只显示第一个文件名，避免文字过多
            file_name = os.path.basename(file_paths[0])
            if len(file_paths) > 1:
                self.window.label.setText(f"已拖入 {len(file_paths)} 个文件\n第一个: {file_name}")
            else:
                self.window.label.setText(f"已拖入文件:\n{file_name}")
        else:
            self.window.label.setText("将文件拖入此处，\n甩出屏幕即可发送")
        
        # 提示用户可以抛扔文件
        print("提示: 拖入文件后，将窗口拖出屏幕边界即可发送文件")
    
    def on_udp_receive(self, data: bytes, address: tuple):
        """UDP数据接收回调
        
        Args:
            data: 接收到的数据
            address: 发送方地址
        """
        try:
            message = data.decode('utf-8')
            print(f"UDP接收: {message} 来自 {address}")
            
            # 处理设备发现消息
            if message.startswith("FLINGFILE_DISCOVER:"):
                parts = message.split(":")
                if len(parts) >= 3:
                    ip = parts[1]
                    # 过滤自己的IP
                    local_ip = IPUtils.get_local_ip()
                    if ip == local_ip:
                        print(f"忽略自己的发现消息: {ip}")
                        return
                    tcp_port = int(parts[2])
                    # 创建包含TCP端口的设备地址
                    device_address = (ip, tcp_port)
                    print(f"发现设备: {ip}, TCP端口: {tcp_port}")
                    # 确保只添加对方设备
                    if device_address not in self.discovered_devices:
                        self.discovered_devices.add(device_address)
                        print(f"设备已添加到列表: {device_address}")
                else:
                    print(f"收到格式不正确的发现消息: {message}")
                    return
        except UnicodeDecodeError:
            # 如果不是UTF-8编码的消息，可能是心跳包或其他二进制数据
            try:
                message = data.decode('ascii').strip()
                if message == 'HEARTBEAT':
                    # 处理心跳包
                    print(f"收到心跳包来自: {address}")
                else:
                    print(f"收到未知ASCII消息: {message} 来自: {address}")
            except:
                print(f"收到无法解码的数据: {data[:20]}... 来自: {address}")
        except Exception as e:
            print(f"处理UDP数据失败: {e}")
    
    def on_peer_detected(self, address: tuple):
        """对端设备检测回调
        
        Args:
            address: 对端设备地址
        """
        # 过滤自己的IP
        local_ip = IPUtils.get_local_ip()
        if address[0] == local_ip:
            print(f"忽略自己的设备: {address}")
            return
        
        # 转换为TCP端口
        if address[1] == UDP_PORT:  # 如果是UDP端口
            device_address = (address[0], TCP_PORT)  # 使用TCP端口
        else:
            device_address = address
        
        if device_address not in self.discovered_devices:
            self.discovered_devices.add(device_address)
            print(f"检测到新设备: {device_address}")
    
    def on_transfer_start(self, file_name: str, file_size: int, address: tuple, is_sending: bool):
        """传输开始回调
        
        Args:
            file_name: 文件名
            file_size: 文件大小
            address: 传输地址
            is_sending: 是否为发送方
        """
        print(f"传输开始: {file_name} ({file_size} bytes) {'发送' if is_sending else '接收'} 到 {address}")
        # 更新UI
        if is_sending:
            self.window.label.setText(f"文件传输中:\n{file_name}")
        else:
            # 接收方
            self.window.label.setText(f"正在接收文件:\n{file_name}")
        # 显示进度条
        self.window.show_progress(0)
    
    def on_transfer_progress(self, file_name: str, progress: int, address: tuple, is_sending: bool):
        """传输进度回调
        
        Args:
            file_name: 文件名
            progress: 进度百分比
            address: 传输地址
            is_sending: 是否为发送方
        """
        print(f"传输进度: {file_name} {progress}% {'发送' if is_sending else '接收'} 到 {address}")
        # 更新进度条
        self.window.show_progress(progress)
    
    def on_transfer_complete(self, file_name: str, file_path: str, address: tuple, is_sending: bool):
        """传输完成回调
        
        Args:
            file_name: 文件名
            file_path: 文件路径
            address: 传输地址
            is_sending: 是否为发送方
        """
        print(f"传输完成: {file_name} {'发送' if is_sending else '接收'} 到 {address}")
        # 隐藏进度条
        self.window.hide_progress()
        # 更新UI
        if is_sending:
            self.window.label.setText("文件发送成功！\n可以继续拖入文件")
            # 传输完成后清空文件列表
            self.current_files.clear()
            print("文件列表已清空")
        else:
            # 接收方
            self.window.label.setText("文件接收成功！\n可以继续接收文件")
        
        print(f"传输完成: {file_name}")
    
    def on_transfer_error(self, error_message: str, address: tuple, is_sending: bool):
        """传输错误回调
        
        Args:
            error_message: 错误信息
            address: 传输地址
            is_sending: 是否为发送方
        """
        print(f"传输错误: {error_message} {'发送' if is_sending else '接收'} 到 {address}")
        # 隐藏进度条
        self.window.hide_progress()
        # 更新UI
        if is_sending:
            self.window.label.setText(f"发送失败:\n{error_message}")
        else:
            self.window.label.setText(f"接收失败:\n{error_message}")
    
    def on_fling(self):
        """窗口抛扔时的处理
        
        当窗口被拖出屏幕边界时触发
        """
        print(f"抛扔触发，当前文件: {self.current_files}")
        print(f"已发现设备: {self.discovered_devices}")
        # 有文件且有设备时发送
        if self.current_files and self.discovered_devices:
            # 过滤出非本机的设备
            local_ip = IPUtils.get_local_ip()
            remote_devices = []
            for device in self.discovered_devices:
                if device[0] != local_ip:
                    remote_devices.append(device)
                    print(f"远程设备: {device}")
            
            if not remote_devices:
                print("没有发现远程设备，无法发送文件")
                self.window.label.setText("未发现远程设备\n请确保其他设备也在运行FlingFile")
                return
            
            # 显示发送准备信息
            self.window.label.setText("准备发送文件...")
            print(f"开始发送文件... 发现 {len(remote_devices)} 个远程设备")
            # 发送文件（后台线程）
            self._send_files()
        else:
            if not self.current_files:
                print("没有文件可发送")
                self.window.label.setText("没有文件可发送\n请先拖入文件")
            if not self.discovered_devices:
                print("未发现其他设备")
                self.window.label.setText("未发现其他设备\n请确保其他设备也在运行FlingFile")
    
    def _send_files(self):
        """发送文件"""
        # 保存当前文件列表的副本，避免在传输过程中被修改
        files_to_send = self.current_files.copy()
        
        # 过滤出非本机的设备
        local_ip = IPUtils.get_local_ip()
        remote_devices = []
        for device in self.discovered_devices:
            if device[0] != local_ip:
                remote_devices.append(device)
                print(f"远程设备: {device}")

        if not remote_devices:
            print("没有发现远程设备，无法发送文件")
            self.window.label.setText("未发现远程设备\n请确保其他设备也在运行FlingFile")
            return
        
        print(f"发现 {len(remote_devices)} 个远程设备")
        
        for file_path in files_to_send:
            for device in remote_devices:
                # 使用设备注册时提供的TCP端口
                print(f"发送文件 {file_path} 到 {device}")
                try:
                    self.tcp_transfer.send_file(file_path, device)
                except Exception as e:
                    print(f"发送文件失败: {e}")
        
        # 注意：不在此处清空文件列表，而是在传输完成回调中处理
        print("文件发送任务已提交")
    
    def _emit_transfer_start(self, file_name: str, file_size: int, address: tuple, *args):
        """发射传输开始信号
        
        Args:
            file_name: 文件名
            file_size: 文件大小
            address: 传输地址
            *args: 其他参数（如is_sending）
        """
        # 确定传输方向：如果提供了is_sending参数，则使用它，否则默认为True（发送）
        is_sending = args[0] if args else True
        # 直接使用信号连接，传递传输方向
        self.signal_handler.transfer_start_signal.emit(file_name, file_size, address, is_sending)
        
    def _emit_transfer_progress(self, file_name: str, progress: int, address: tuple, *args):
        """发射传输进度信号
        
        Args:
            file_name: 文件名
            progress: 进度百分比
            address: 传输地址
            *args: 其他参数（如is_sending）
        """
        # 确定传输方向：如果提供了is_sending参数，则使用它，否则默认为True（发送）
        is_sending = args[0] if args else True
        # 直接使用信号连接，传递传输方向
        self.signal_handler.transfer_progress_signal.emit(file_name, progress, address, is_sending)
        
    def _emit_transfer_complete(self, file_name: str, file_path: str, address: tuple, *args):
        """发射传输完成信号
        
        Args:
            file_name: 文件名
            file_path: 文件路径
            address: 传输地址
            *args: 其他参数（如is_sending）
        """
        # 确定传输方向：如果提供了is_sending参数，则使用它，否则默认为True（发送）
        is_sending = args[0] if args else True
        # 直接使用信号连接，传递传输方向
        self.signal_handler.transfer_complete_signal.emit(file_name, file_path, address, is_sending)
        
    def _emit_transfer_error(self, error_message: str, address: tuple, *args):
        """发射传输错误信号
        
        Args:
            error_message: 错误信息
            address: 传输地址
            *args: 其他参数（如is_sending）
        """
        # 确定传输方向：如果提供了is_sending参数，则使用它，否则默认为True（发送）
        is_sending = args[0] if args else True
        # 直接使用信号连接，传递传输方向
        self.signal_handler.transfer_error_signal.emit(error_message, address, is_sending)
    
    def run(self):
        """运行应用
        
        Returns:
            int: 退出码
        """
        try:
            # 显示窗口
            self.window.show()
            
            # 运行应用
            return self.app.exec()
        except Exception as e:
            print(f"应用运行失败: {e}")
            return 1
        finally:
            # 清理资源
            self._cleanup()
    
    def on_window_close(self):
        """窗口关闭时的处理"""
        print("窗口关闭，停止后台服务...")
        # 清理资源
        self._cleanup()
        # 退出应用
        self.app.quit()
    
    def _cleanup(self):
        """清理资源"""
        print("清理资源...")
        
        # 停止UDP打洞服务
        self.udp_puncher.stop()
        
        # 停止TCP传输服务
        self.tcp_transfer.stop_server()
        
        print("资源清理完成")


def main():
    """主函数"""
    import sys
    
    # 检查命令行参数，判断是否为防火墙模式
    if '--firewall-mode' in sys.argv:
        # 如果是防火墙模式，不启动界面，只用于显示提示
        print("防火墙放行模式 - 规则已在管理员权限下添加")
        return 0
    
    # 确保Download目录存在
    if not os.path.exists("Downloads"):
        os.makedirs("Downloads", exist_ok=True)
    
    # 创建应用实例
    app = FlingFileApp()
    
    # 运行应用
    sys.exit(app.run())


if __name__ == "__main__":
    main()