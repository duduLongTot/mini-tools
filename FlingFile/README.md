# FlingFile（抛传）

轻量级内网点对点文件互传工具，基于Python+PyQt6开发，实现设备自动发现、拖拽发送、悬浮窗交互、点对点传输。

## 项目简介

FlingFile是一款专为局域网环境设计的轻量级文件传输工具。通过自动设备发现和直观的拖拽操作，用户可以快速在局域网内的设备间传输文件。软件采用悬浮窗设计，支持置顶显示，操作简便高效。

## 核心功能

- **局域网设备自动发现**：通过UDP端口50000 自动发现同一局域网内的设备
- **文件拖拽发送**：支持直接拖拽文件到悬浮窗进行发送
- **TCP可靠文件传输**：使用TCP端口50001 进行可靠的数据传输
- **悬浮窗界面**：支持置顶、移动、关闭、最小化等操作
- **发送/接收状态区分**：清晰显示传输方向和状态

## 运行环境与启动方式

**运行环境：**
- Windows操作系统
- Python3.11.5
- PyQt6库

**启动方式：**
```bash
# 直接运行
python main.py

# 或打包后运行可执行文件
.\dist\FlingFile.exe
```

## 防火墙配置

在Windows系统中，需要手动配置防火墙规则以允许 FlingFile 的网络通信：

**添加入站规则：**
```cmd
# UDP入站规则
netsh advfirewall firewall add rule name="FlingFile_UDP_In" dir=in action=allow protocol=UDP localport=50000

# TCP入站规则
netsh advfirewall firewall add rule name="FlingFile_TCP_In" dir=in action=allow protocol=TCP localport=50001
```

**添加出站规则：**
```cmd
# UDP出站规则
netsh advfirewall firewall add rule name="FlingFile_UDP_Out" dir=out action=allow protocol=UDP localport=50000

# TCP出站规则
netsh advfirewall firewall add rule name="FlingFile_TCP_Out" dir=out action=allow protocol=TCP localport=50001
```

## 使用步骤

1. 在所有需要传输文件的设备上运行FlingFile
2. 确保所有设备处于同一局域网环境中
3. 等待设备自动发现
4. 将文件拖拽到悬浮窗上，然后将悬浮窗拖出屏幕边界（任意方向）即可自动发送文件到发现的设备
5. 接收方确认接收文件
6. 查看传输进度和完成状态

## 已知缺陷与限制

- **仅支持Windows系统**：当前版本仅在Windows平台上测试和开发
- **必须手动配置防火墙端口**：无法自动配置防火墙，需要用户手动添加端口放行规则
- **管理员权限运行限制**：以管理员权限运行会导致拖拽功能失效，需以普通用户权限运行
- **局域网限制**：仅支持同一局域网内的设备发现与文件传输
- **功能限制**：暂不支持断点续传、传输速度显示等功能
- **无文件校验**：传输完成后无自动文件完整性校验机制

## 注意事项

- 请确保所有设备在同一局域网内，跨网段可能无法正常发现设备
- 需要手动配置防火墙规则才能正常使用
- 建议以普通用户权限运行，避免拖拽功能失效
- 大文件传输时请耐心等待，避免中途关闭程序
- 传输敏感文件时请注意网络安全

## 许可证

MIT License

Copyright (c) 2024 FlingFile Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.