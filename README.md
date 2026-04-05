# 🛠️ mini-tools
Personal collection of small tools & widgets for daily use.

---

## 📖 项目简介
`mini-tools` 是个人开发的轻量级效率工具合集，专注于解决日常办公、学习、开发中的小痛点，主打**开箱即用、无冗余、高实用性**。所有工具均基于 Python 开发，适配 Windows 系统，开源免费，可自由使用与二次开发。

---

## 🚀 工具列表
### 1. FlingFile（抛传）
一款专为局域网设计的点对点文件互传工具，拖拽即发，秒速传输。
- **核心功能**：局域网设备自动发现、文件拖拽发送、TCP 可靠传输、悬浮窗交互
- **适用场景**：同局域网内电脑间快速传文件，替代U盘、微信/QQ传文件限制
- **项目路径**：`/FlingFile/`
- **详细文档**：[FlingFile README](sslocal://flow/file_open?url=.%2FFlingFile%2FREADME.md&flow_extra=eyJsaW5rX3R5cGUiOiJjb2RlX2ludGVycHJldGVyIn0=)

---

## 📦 环境要求
- 操作系统：Windows 10/11
- Python 版本：3.11.5+
- 依赖库：PyQt6 等（各工具单独标注）

---

## 🔧 使用说明
### 通用步骤
1. 克隆仓库到本地
```bash
git clone https://github.com/duduLongTot/mini-tools.git
cd mini-tools
```
2. 进入对应工具目录，安装依赖
```bash
# 以FlingFile为例
cd FlingFile
pip install -r requirements.txt
```
3. 运行程序
```bash
python main.py
```
4. 按工具README完成前置配置（如防火墙放行）

---

## ⚠️ 注意事项
1.  部分工具需手动配置防火墙规则，否则无法正常使用网络功能
2.  建议以普通用户权限运行，避免管理员权限导致拖拽等功能失效
3.  所有工具仅在本地/局域网运行，不上传数据到云端，保障隐私安全
4.  本项目为个人开源项目，仅用于学习与交流，不承担商用风险

---

## 📄 许可证
本项目所有代码均基于 **MIT License** 开源，详细协议见各工具目录下的 LICENSE 文件，或根目录 [LICENSE](sslocal://flow/file_open?url=.%2FLICENSE&flow_extra=eyJsaW5rX3R5cGUiOiJjb2RlX2ludGVycHJldGVyIn0=)。

---

## 🤝 贡献与反馈
欢迎提交 Issue 反馈问题、提出功能建议，也欢迎 Fork 仓库进行二次开发。

---

## 📌 后续规划
持续更新更多实用小工具，包括但不限于：
- 桌面效率组件
- 自动化脚本
- 数据处理工具
- 学习辅助插件

---
