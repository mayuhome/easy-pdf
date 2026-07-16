# 🎉 Easy PDF - 完整安装和使用指南

## 📋 项目概述

**Easy PDF** 现已支持跨平台（macOS、Windows、Linux）的现代 GUI 应用，同时保留强大的命令行工具。

## 📦 可安装文件

项目已成功构建，生成以下可安装文件：

- **wheel 包**: `dist/easy_pdf-0.1.0-py3-none-any.whl` (推荐用于安装)
- **源代码包**: `dist/easy_pdf-0.1.0.tar.gz` (可用于源代码分发)

## 🚀 快速开始（推荐方式）

### 1️⃣ macOS / Linux

```bash
# 创建虚拟环境
python3 -m venv easy_pdf_env
source easy_pdf_env/bin/activate

# 安装应用（包含 GUI + PDF 功能）
pip install dist/easy_pdf-0.1.0-py3-none-any.whl[pdf,gui]

# 启动 GUI 应用
easy-pdf-gui
```

### 2️⃣ Windows

```cmd
# 创建虚拟环境
python -m venv easy_pdf_env
easy_pdf_env\Scripts\activate

# 安装应用
pip install dist/easy_pdf-0.1.0-py3-none-any.whl[pdf,gui]

# 启动 GUI 应用
easy-pdf-gui
```

## ✨ GUI 功能特性

### 🎨 三个主要选项卡

#### 1. **Add Watermark** (添加水印)
- 选择 PDF 文件
- 配置水印文本、不透明度和字体大小
- 生成带有水印的 PDF
- 输出文件: `原文件名_watermarked.pdf`

#### 2. **Merge PDFs** (合并PDF)
- 支持多文件选择
- 拖拽排序或使用上/下按钮调整顺序
- 一次性合并所有 PDF
- 输出文件: `merged.pdf`

#### 3. **Batch Process** (批量处理)
- 选择包含多个 PDF 的目录
- 可选：对所有 PDF 应用水印
- 批量处理所有文件
- 所有结果保存到输出目录

## 💻 命令行工具

原有的强大命令行工具仍然可用：

```bash
# 查看所有命令
easy-pdf --help

# 健康检查
easy-pdf health

# 其他命令
easy-pdf open <file>
easy-pdf summary <file>
easy-pdf detect <file>
# ... 更多命令见帮助文档
```

## 📊 安装变体

### 最小安装（仅核心功能）
```bash
pip install dist/easy_pdf-0.1.0-py3-none-any.whl
```

### PDF 功能（不包含 GUI）
```bash
pip install dist/easy_pdf-0.1.0-py3-none-any.whl[pdf]
```

### GUI 功能（不包含 PDF 功能）
```bash
pip install dist/easy_pdf-0.1.0-py3-none-any.whl[gui]
```

### 完整安装（推荐）
```bash
pip install dist/easy_pdf-0.1.0-py3-none-any.whl[pdf,gui]
```

## 🔧 系统要求

- **Python**: 3.11 或更高版本
- **操作系统**: macOS (ARM64/Intel), Windows, Linux
- **GUI 库**: PyQt6 (自动安装)
- **PDF 库**: PyMuPDF, pikepdf, OpenCV (可选，用于 PDF 功能)

## 🛠️ 开发和测试

### 运行测试脚本
```bash
chmod +x test_gui.sh
./test_gui.sh
```

### 项目结构
```
easy_pdf/
├── gui/                        # ✨ GUI 应用代码
│   ├── main_window.py         # 主窗口
│   ├── widgets.py             # 可重用 UI 组件
│   ├── worker.py              # 后台线程处理
│   └── tabs/                  # 功能选项卡
│       ├── base_tab.py
│       ├── watermark_tab.py
│       ├── merge_tab.py
│       └── batch_tab.py
├── services/                  # 核心业务逻辑
│   ├── watermark_service.py
│   ├── page_edit_service.py
│   ├── document_service.py
│   └── bootstrap.py           # 依赖注入
├── domain/                    # 领域模型
│   ├── models.py
│   └── errors.py
├── app.py                     # CLI 入口点
└── ...
```

## 📝 依赖项详情

### 核心依赖
- `pydantic>=2.8.0` - 数据验证
- `typer>=0.12.3` - CLI 框架
- `rich>=13.7.1` - 终端美化

### GUI 依赖 (`[gui]`)
- `PyQt6>=6.6.0` - 跨平台 GUI 框架
- `PyQt6-sip>=13.6.0` - PyQt6 支持库

### PDF 依赖 (`[pdf]`)
- `PyMuPDF>=1.24.5` - PDF 处理
- `pikepdf>=9.0.0` - PDF 操作
- `opencv-python>=4.10.0.84` - 图像处理

## 🐛 故障排除

### 问题: `No module named 'PyQt6'`
**解决**: `pip install PyQt6>=6.6.0`

### 问题: `No module named 'fitz'` (PyMuPDF)
**解决**: `pip install PyMuPDF>=1.24.5`

### 问题: GUI 窗口不显示（Linux）
**解决**: 安装系统依赖
```bash
# Ubuntu/Debian
sudo apt-get install libqt6gui6 libqt6core6

# Fedora
sudo dnf install qt6-qtbase
```

### 问题: 导入错误或包不完整
**解决**: 重新构建并安装
```bash
# 清理旧构建
rm -rf build dist *.egg-info

# 重新构建
python -m build

# 在新虚拟环境中安装
python3 -m venv fresh_env
source fresh_env/bin/activate
pip install dist/easy_pdf-0.1.0-py3-none-any.whl[pdf,gui]
```

## 📚 相关文档

- [GUI 详细设置指南](GUI_SETUP.md)
- [API 契约](docs/API_CONTRACT.md)
- [数据模式](docs/DATA_SCHEMA.md)
- [模块设计](docs/MODULE_DESIGN.md)

## 🎯 下一步

1. ✅ 安装应用
2. ✅ 运行 GUI: `easy-pdf-gui`
3. ✅ 测试各功能
4. ✅ 查看帮助: `easy-pdf --help`
5. ✅ 分享给朋友！

## 📞 支持

遇到问题？查看故障排除部分或检查文档文件。

---

**版本**: 0.1.0  
**发布日期**: 2026-07-16  
**状态**: ✅ 可安装和可测试
