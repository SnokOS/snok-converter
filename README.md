<div align="center">

# 🎬 Snok-Converter

**A powerful, all-in-one file converter for the Thunar file manager**

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/SnokOS/snok-converter)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/SnokOS/snok-converter)
[![Platform](https://img.shields.io/badge/platform-Linux-orange.svg)](https://github.com/SnokOS/snok-converter)
[![Made for SnokOS](https://img.shields.io/badge/made%20for-SnokOS-purple.svg)](https://github.com/SnokOS)

A simple, lightweight tool for converting and compressing files directly from the right-click context menu of your file manager.  
Designed specifically for **SnokOS Linux**.

[📥 Quick Install](#-quick-install) · [📖 Usage](#-usage) · [⚙️ Settings](#️-settings) · [🐛 Report a Bug](https://github.com/SnokOS/snok-converter/issues)

</div>

---

## ✨ Features

- 🖱️ **Full Thunar integration** — convert directly from the right-click menu
- 🎨 **Lightweight UI** — designed for speed and simplicity
- 📊 **Real progress bar** — shows elapsed time for each operation
- 🎯 **Broad format support** — images, audio, video, documents, and SVG
- ⚙️ **Highly customizable** — full control over visible formats and conversion options
- 🗑️ **Delete original option** — individually per format
- 🎛️ **Advanced options** — quality, DPI, Bitrate, CRF, and SVG optimization
- 🌐 **Bilingual interface** — English and Arabic

---

## 📋 Supported Formats

| Category | Output Formats | Input Formats |
|:---:|:---|:---|
| 🎵 **Audio** | `flac`, `aac`, `ogg`, `mp3`, `wav` | `3gp`, `3gpp`, `aac`, `aiff`, `ape`, `avi`, `bik`, `cda`, `flac`, `flv`, `gif`, `m4v`, `mkv`, `mp4`, `m4a`, `m4b`, `mp3`, `mpg`, `mpeg`, `mov`, `oga`, `ogg`, `ogv`, `opus`, `rm`, `ts`, `vob`, `wav`, `webm`, `wma`, `wmv` |
| 🎬 **Video** | `webm`, `mkv`, `mp4`, `ogv`, `avi`, `gif` | `3gp`, `3gpp`, `avi`, `bik`, `flv`, `gif`, `m4v`, `mkv`, `mp4`, `mpg`, `mpeg`, `mov`, `ogv`, `rm`, `ts`, `vob`, `webm`, `wmv` |
| 🖼️ **Image** | `svg`, `png`, `jpg`, `ico`, `webp`, `avif` | `arw`, `avif`, `bmp`, `cr2`, `dds`, `dns`, `exr`, `heic`, `ico`, `jfif`, `jpg`, `jpeg`, `nef`, `png`, `psd`, `raf`, `svg`, `tif`, `tiff`, `tga`, `webp`, `pdf`, `doc*`, `docx*`, `odt*`, `odp*`, `ods*`, `ppt*`, `pptx*`, `xls*`, `xlsx*` |
| 📄 **Document** | `pdf` | `doc*`, `docx*`, `odt*`, `odp*`, `ods*`, `ppt*`, `pptx*`, `xls*`, `xlsx*`, `arw`, `bmp`, `cr2`, `dds`, `dns`, `exr`, `heic`, `ico`, `jfif`, `jpg`, `jpeg`, `nef`, `png`, `psd`, `raf`, `svg`, `tif`, `tiff`, `tga`, `webp` |

> 💡 You can fully customize the application: add or remove preset conversion profiles from the file context menu, or modify existing settings to change conversion options.

---

## 🚀 Quick Install

### Option 1: One-line installer (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/SnokOS/snok-converter/main/install.sh | sudo bash