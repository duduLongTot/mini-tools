"""TCP文件传输模块 - 实现文件的发送和接收"""

import socket
import threading
import os
import struct
from config.settings import TCP_PORT, BUFF_SIZE, FILE_CHUNK_SIZE
from utils.path_utils import PathUtils


class TCPFileTransfer:
    """TCP文件传输类 - 实现文件的发送和接收"""
    
    def __init__(self):
        """初始化TCP文件传输器"""
        # 服务端套接字
        self.server_socket = None
        # 本地端口
        self.local_port = 0
        # 服务端线程
        self.server_thread = None
        # 运行状态
        self.running = False
        # 传输回调
        self.on_transfer_start_callback = None
        self.on_transfer_progress_callback = None
        self.on_transfer_complete_callback = None
        self.on_transfer_error_callback = None
    
    def start_server(self):
        """启动服务端
        
        Returns:
            bool: 是否启动成功
        """
        try:
            # 创建TCP套接字
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # 绑定到固定端口，确保其他机器能够连接
            self.server_socket.bind(('', TCP_PORT))
            
            # 设置本地端口为配置的TCP端口
            self.local_port = TCP_PORT
            
            # 开始监听
            self.server_socket.listen(5)
            
            # 设置运行状态
            self.running = True
            
            # 启动服务端线程
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            print(f"TCP服务端启动成功，监听端口: {self.local_port}")
            return True
        except Exception as e:
            print(f"TCP服务端启动失败: {e}")
            self.stop_server()
            return False
    
    def stop_server(self):
        """停止服务端"""
        try:
            # 设置运行状态
            self.running = False
            
            # 关闭服务端套接字
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            
            # 等待线程结束
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=2)
            
            print("TCP服务端已停止")
        except Exception as e:
            print(f"停止TCP服务端失败: {e}")
    
    def send_file(self, file_path: str, target_address: tuple):
        """发送文件
        
        Args:
            file_path: 要发送的文件路径
            target_address: 目标地址 (ip, port)
            
        Returns:
            bool: 是否开始发送
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                print(f"文件不存在: {file_path}")
                return False
            
            # 启动发送线程
            send_thread = threading.Thread(
                target=self._send_file_thread, 
                args=(file_path, target_address),
                daemon=True
            )
            send_thread.start()
            
            return True
        except Exception as e:
            print(f"开始发送文件失败: {e}")
            return False
    
    def _server_loop(self):
        """服务端主循环"""
        while self.running:
            try:
                # 接受连接
                client_socket, client_address = self.server_socket.accept()
                
                # 启动客户端处理线程
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"接受连接失败: {e}")
                break
    
    def _handle_client(self, client_socket: socket.socket, client_address: tuple):
        """处理客户端连接
        
        Args:
            client_socket: 客户端套接字
            client_address: 客户端地址
        """
        try:
            print(f"接收到来自 {client_address} 的连接")
            
            # 设置接收超时为30秒
            client_socket.settimeout(30.0)
            
            # 接收文件信息
            print("开始接收文件信息...")
            # 首先接收文件名长度（4字节）
            length_header = self._recv_all(client_socket, 4)
            if not length_header or len(length_header) != 4:
                print(f"接收文件名长度头部失败，实际接收到: {len(length_header) if length_header else 0} 字节")
                return
            
            # 解析文件名长度
            try:
                name_length = struct.unpack('I', length_header)[0]
                print(f"解析到文件名长度: {name_length}")
                
                # 验证文件名长度是否合理（最大255字符）
                if name_length > 255:
                    print(f"文件名长度异常: {name_length}，可能数据错误")
                    return
            except Exception as e:
                print(f"解析文件名长度失败: {e}")
                return
            
            # 接收文件名和文件大小（name_length + 8字节）
            info_body = self._recv_all(client_socket, name_length + 8)
            if not info_body or len(info_body) != name_length + 8:
                print(f"接收文件信息体失败，需要: {name_length + 8} 字节，实际接收到: {len(info_body) if info_body else 0} 字节")
                return
            
            # 组合完整文件信息
            file_info_data = length_header + info_body
            
            print(f"接收到文件信息，总长度: {len(file_info_data)} bytes")
            
            print(f"接收到文件信息，总长度: {len(file_info_data)} bytes")
            
            # 解析文件信息
            print("开始解析文件信息...")
            file_name, file_size = self._parse_file_info(file_info_data)
            if not file_name:
                print("解析文件信息失败")
                return
            print(f"解析文件信息成功: {file_name}, 大小: {file_size} bytes")
            
            # 构建保存路径
            save_path = PathUtils.get_default_save_path()
            file_save_path = os.path.join(save_path, file_name)
            print(f"保存路径: {file_save_path}")
            
            # 确保保存目录存在
            PathUtils.ensure_dir(save_path)
            
            # 触发传输开始回调
            if self.on_transfer_start_callback:
                try:
                    # 对于接收方，is_sending参数为False
                    self.on_transfer_start_callback(file_name, file_size, client_address, False)
                except Exception as e:
                    print(f"传输开始回调失败: {e}")

            # 发送确认
            print("发送确认消息...")
            client_socket.sendall(b'OK')
            # 刷新套接字缓冲区，确保确认消息立即发送
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            # 立即刷新输出，确保确认消息立即发送
            client_socket.flush() if hasattr(client_socket, 'flush') else None
            print("确认消息已发送")
            
            # 接收文件内容
            received_size = 0
            with open(file_save_path, 'wb') as f:
                while received_size < file_size:
                    # 计算本次接收的大小
                    remaining = file_size - received_size
                    chunk_size = min(FILE_CHUNK_SIZE, remaining)
                    
                    # 接收数据 - 从socket接收，但不要求固定大小
                    try:
                        # 不要求一次性接收满chunk_size的数据，接收多少处理多少
                        data = client_socket.recv(min(chunk_size, BUFF_SIZE))
                        if not data:  # 如果接收到空数据，表示连接已断开
                            print(f"接收文件数据失败，连接已断开，已接收: {received_size}, 总大小: {file_size}")
                            return
                    except socket.timeout:
                        print(f"接收文件数据超时，已接收: {received_size}, 总大小: {file_size}")
                        return
                    except Exception as e:
                        print(f"接收文件数据时发生错误: {e}")
                        return
                    
                    # 写入文件
                    f.write(data)
                    received_size += len(data)
                    
                    # 触发进度回调
                    if self.on_transfer_progress_callback:
                        try:
                            progress = int(received_size / file_size * 100)
                            # 对于接收方，is_sending参数为False
                            self.on_transfer_progress_callback(file_name, progress, client_address, False)
                        except Exception as e:
                            print(f"进度回调失败: {e}")
            
            # 触发传输完成回调
            if self.on_transfer_complete_callback:
                try:
                    # 对于接收方，is_sending参数为False
                    self.on_transfer_complete_callback(file_name, file_save_path, client_address, False)
                except Exception as e:
                    print(f"传输完成回调失败: {e}")
            
            print(f"文件接收完成: {file_name}, 大小: {file_size} bytes")
            
        except Exception as e:
            print(f"处理客户端失败: {e}")
            # 触发错误回调
            if self.on_transfer_error_callback:
                try:
                    # 对于接收方，is_sending参数为False
                    self.on_transfer_error_callback(str(e), client_address, False)
                except Exception as callback_error:
                    print(f"错误回调失败: {callback_error}")
        finally:
            # 关闭客户端套接字
            try:
                client_socket.close()
            except:
                pass
    
    def _send_file_thread(self, file_path: str, target_address: tuple):
        """发送文件线程
        
        Args:
            file_path: 文件路径
            target_address: 目标地址
        """
        client_socket = None
        try:
            print(f"开始连接到 {target_address}")
            # 创建客户端套接字
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # 设置连接超时为10秒
            client_socket.settimeout(10.0)
            
            # 连接服务器
            print(f"正在连接到 {target_address}...")
            client_socket.connect(target_address)
            print(f"成功连接到 {target_address}")
            
            # 设置文件传输的超时时间为30秒
            client_socket.settimeout(30.0)
            
            # 获取文件名和大小
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            print(f"文件信息: {file_name}, 大小: {file_size} bytes")
            
            # 发送文件信息
            file_info = self._pack_file_info(file_name, file_size)
            client_socket.sendall(file_info)
            # 刷新缓冲区，确保文件信息立即发送
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            print("已发送文件信息")
            
            # 等待确认（使用60秒超时，给接收端更多时间处理文件信息）
            print("等待服务器确认...")
            # 接收确认消息，使用recv而不是_recv_all以避免固定长度问题
            try:
                response = client_socket.recv(1024)  # 接收最多1024字节
                if not response:
                    print("接收服务器确认失败")
                    return
                if response != b'OK':
                    print(f"服务器确认失败，收到: {response}")
                    return
            except socket.timeout:
                print("接收服务器确认超时")
                return
            except Exception as e:
                print(f"接收服务器确认时发生错误: {e}")
                return
            print("服务器确认成功")
            
            # 触发传输开始回调
            if self.on_transfer_start_callback:
                try:
                    self.on_transfer_start_callback(file_name, file_size, target_address)
                    print("传输开始回调已触发")
                except Exception as e:
                    print(f"传输开始回调失败: {e}")
            
            # 发送文件内容
            sent_size = 0
            print("开始发送文件内容...")
            with open(file_path, 'rb') as f:
                while sent_size < file_size:
                    # 计算本次发送的大小
                    remaining = file_size - sent_size
                    chunk_size = min(FILE_CHUNK_SIZE, remaining)
                    
                    # 读取文件数据
                    data = f.read(chunk_size)
                    if not data:
                        print("读取文件数据失败")
                        return
                    
                    # 发送数据
                    client_socket.sendall(data)
                    sent_size += len(data)
                    
                    # 触发进度回调
                    if self.on_transfer_progress_callback:
                        try:
                            progress = int(sent_size / file_size * 100)
                            self.on_transfer_progress_callback(file_name, progress, target_address)
                        except Exception as e:
                            print(f"进度回调失败: {e}")
            
            # 通知对端发送完毕
            client_socket.shutdown(socket.SHUT_WR)
            print("已通知对端发送完毕")
            
            # 触发传输完成回调
            if self.on_transfer_complete_callback:
                try:
                    self.on_transfer_complete_callback(file_name, file_path, target_address)
                    print("传输完成回调已触发")
                except Exception as e:
                    print(f"传输完成回调失败: {e}")
            
            print(f"文件发送完成: {file_name}, 大小: {file_size} bytes")
            
        except socket.timeout:
            print(f"连接超时: {target_address}")
            # 触发错误回调
            if self.on_transfer_error_callback:
                try:
                    self.on_transfer_error_callback("连接超时", target_address)
                except Exception as callback_error:
                    print(f"错误回调失败: {callback_error}")
        except Exception as e:
            print(f"发送文件失败: {e}")
            # 触发错误回调
            if self.on_transfer_error_callback:
                try:
                    self.on_transfer_error_callback(str(e), target_address)
                except Exception as callback_error:
                    print(f"错误回调失败: {callback_error}")
        finally:
            # 关闭客户端套接字
            if client_socket:
                try:
                    client_socket.close()
                    print("客户端套接字已关闭")
                except:
                    pass
    
    def _recv_all(self, sock: socket.socket, size: int) -> bytes:
        """接收指定大小的数据
        
        Args:
            sock: 套接字
            size: 要接收的大小
            
        Returns:
            bytes: 接收到的数据
        """
        data = b''
        
        try:
            while len(data) < size:
                # 计算还需要接收多少数据
                remaining = size - len(data)
                chunk = sock.recv(min(remaining, BUFF_SIZE))
                if not chunk:
                    print(f"接收到空数据块，连接可能已断开，当前已接收: {len(data)}, 预期: {size}")
                    break  # 不直接返回空，而是跳出循环
                data += chunk
        except socket.timeout:
            print(f"接收数据超时，已接收: {len(data)}, 预期: {size}")
            return b''
        except Exception as e:
            print(f"接收数据时发生错误: {e}")
            return b''
        
        return data
    
    def _pack_file_info(self, file_name: str, file_size: int) -> bytes:
        """打包文件信息
        
        Args:
            file_name: 文件名
            file_size: 文件大小
            
        Returns:
            bytes: 打包后的数据
        """
        # 文件名编码
        file_name_bytes = file_name.encode('utf-8')
        # 文件名长度
        name_length = len(file_name_bytes)
        
        # 先打包文件名长度和文件名
        header_part = struct.pack(f'I{name_length}s', name_length, file_name_bytes)
        # 再打包文件大小
        size_part = struct.pack('Q', file_size)
        
        # 返回组合后的数据
        return header_part + size_part
    
    def _parse_file_info(self, data: bytes) -> tuple:
        """解析文件信息
        
        Args:
            data: 接收到的数据
            
        Returns:
            tuple: (文件名, 文件大小)
        """
        try:
            if len(data) < 12:  # 至少需要4字节长度 + 8字节大小
                print(f"数据长度不足，需要至少12字节，实际: {len(data)}")
                return None, 0
                
            # 解析文件名长度
            name_length = struct.unpack('I', data[:4])[0]
            
            # 检查数据长度是否足够
            if len(data) < 4 + name_length + 8:
                print(f"数据长度不足以解析完整信息，需要: {4 + name_length + 8}，实际: {len(data)}")
                return None, 0
                
            # 解析文件名
            file_name = data[4:4+name_length].decode('utf-8')
            # 解析文件大小
            file_size = struct.unpack('Q', data[4+name_length:4+name_length+8])[0]
            
            # 验证文件大小是否合理（最大1GB）
            if file_size > 1024 * 1024 * 1024:  # 1GB
                print(f"检测到异常大的文件大小: {file_size} 字节")
                return None, 0
                
            return file_name, file_size
        except UnicodeDecodeError:
            print("文件名解码失败，可能编码问题")
            return None, 0
        except Exception as e:
            print(f"解析文件信息失败: {e}")
            return None, 0
    
    def set_on_transfer_start_callback(self, callback):
        """设置传输开始回调
        
        Args:
            callback: 回调函数，格式为 callback(file_name, file_size, address, is_sending)
        """
        self.on_transfer_start_callback = callback
    
    def set_on_transfer_progress_callback(self, callback):
        """设置传输进度回调
        
        Args:
            callback: 回调函数，格式为 callback(file_name, progress, address, is_sending)
        """
        self.on_transfer_progress_callback = callback
    
    def set_on_transfer_complete_callback(self, callback):
        """设置传输完成回调
        
        Args:
            callback: 回调函数，格式为 callback(file_name, file_path, address, is_sending)
        """
        self.on_transfer_complete_callback = callback
    
    def set_on_transfer_error_callback(self, callback):
        """设置传输错误回调
        
        Args:
            callback: 回调函数，格式为 callback(error_message, address, is_sending)
        """
        self.on_transfer_error_callback = callback
    
    def is_running(self) -> bool:
        """检查服务端是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        return self.running