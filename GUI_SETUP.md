# Easy PDF - GUI Application Setup & Testing Guide

## Overview

Easy PDF 现已支持跨平台（macOS/Windows/Linux）的现代 PyQt6 GUI 应用，除了原有的命令行工具外。

## 功能特性

GUI 应用支持以下功能：

- **Add Watermark** - 给 PDF 文件添加水印
- **Merge PDFs** - 合并多个 PDF 文件（支持拖拽排序）
- **Batch Process** - 批量处理多个 PDF 文件

## 安装方式

### 方法 1: 安装完整版本（包含 PDF 功能）

```bash
# 推荐：安装 wheel 包及所有 PDF 依赖
pip install dist/easy_pdf-0.1.0-py3-none-any.whl[pdf,gui]
```

### 方法 2: 分步安装

```bash
# 仅安装核心应用
pip install dist/easy_pdf-0.1.0-py3-none-any.whl

# 后续添加 PDF 功能
pip install easy-pdf[pdf,gui]
```

## 运行 GUI 应用

### macOS / Linux

```bash
# 启动 GUI 应用
easy-pdf-gui
```

### Windows

```cmd
easy-pdf-gui
```

## 快速测试步骤

### 1. 创建测试虚拟环境

```bash
# 创建新的虚拟环境用于测试
python3 -m venv test_env
source test_env/bin/activate  # macOS/Linux
# 或
test_env\Scripts\activate  # Windows
```

### 2. 安装应用

```bash
# 安装完整版本（包含 GUI + PDF 功能）
pip install /path/to/dist/easy_pdf-0.1.0-py3-none-any.whl[pdf,gui]

# 验证命令行工具
easy-pdf --help

# 验证 health check
easy-pdf health
```

### 3. 启动 GUI 应用

```bash
easy-pdf-gui
```

应用窗口应该弹出，显示三个选项卡：
- **Add Watermark** - 添加水印
- **Merge PDFs** - 合并 PDF
- **Batch Process** - 批量处理

## 使用指南

### 添加水印 (Add Watermark)

1. 选择一个 PDF 文件
2. 设置水印文本、不透明度和字体大小
3. 选择输出目录
4. 点击 "Apply Watermark" 按钮
5. 结果文件会保存为 `原文件名_watermarked.pdf`

### 合并 PDF (Merge PDFs)

1. 点击 "Add PDFs" 选择要合并的 PDF 文件
2. 使用 "Move Up/Down" 调整文件顺序
3. 选择输出目录
4. 点击 "Merge PDFs" 按钮
5. 结果文件为 `merged.pdf`

### 批量处理 (Batch Process)

1. 选择包含 PDF 文件的输入目录
2. （可选）勾选 "Apply Watermark to All PDFs" 并配置水印参数
3. 选择输出目录
4. 点击 "Start Batch Processing" 按钮
5. 所有 PDF 文件会被处理并保存到输出目录

## 故障排除

### PyQt6 导入错误

**问题**: `ModuleNotFoundError: No module named 'PyQt6'`

**解决**:
```bash
pip install PyQt6>=6.6.0
```

### PDF 操作失败

**问题**: `ModuleNotFoundError: No module named 'fitz'` 或其他 PDF 库

**解决**:
```bash
pip install easy-pdf[pdf]
```

### GUI 窗口无法显示（Linux）

如果在 Linux 环境中 GUI 无法显示，可能需要安装额外的系统依赖：

```bash
# Ubuntu/Debian
sudo apt-get install libqt6gui6 libqt6core6

# Fedora
sudo dnf install qt6-qtbase
```

## 命令行工具

原有的命令行工具仍然可用：

```bash
# 查看帮助
easy-pdf --help

# 健康检查
easy-pdf health
```

## 项目结构

```
easy_pdf/
├── gui/                          # GUI 相关代码
│   ├── __init__.py
│   ├── main_window.py           # 主窗口
│   ├── widgets.py               # 可重用 UI 组件
│   ├── worker.py                # 后台线程处理
│   └── tabs/                    # 功能选项卡
│       ├── base_tab.py          # 基类
│       ├── watermark_tab.py     # 水印功能
│       ├── merge_tab.py         # 合并功能
│       └── batch_tab.py         # 批量处理
├── services/                    # 核心服务（共享）
├── domain/                      # 领域模型
├── api/                         # API 契约
└── app.py                       # CLI 入口点
```

## 开发注意事项

### 添加新功能

1. 在 `easy_pdf/gui/tabs/` 中创建新的选项卡类
2. 继承自 `BaseTab`
3. 在 `main_window.py` 中注册新选项卡
4. 重新构建和安装包

### 样式定制

可以通过修改 `main_window.py` 和 `widgets.py` 中的 PyQt6 样式表来自定义外观。

## 依赖项

### 核心依赖
- pydantic>=2.8.0
- typer>=0.12.3
- rich>=13.7.1

### GUI 依赖 (`[gui]`)
- PyQt6>=6.6.0
- PyQt6-sip>=13.6.0

### PDF 依赖 (`[pdf]`)
- PyMuPDF>=1.24.5
- pikepdf>=9.0.0
- opencv-python>=4.10.0.84

## 许可证

详见项目主目录的 LICENSE 文件。
