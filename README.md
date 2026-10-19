<div align="center">

# ⃤ I M A G E F O R G E ⃤

### *Convert, resize, and optimize images in bulk - one command.*

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![OS](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Stars](https://img.shields.io/github/stars/MrHacker-X/imageforge?style=flat-square&color=orange)
![Forks](https://img.shields.io/github/forks/MrHacker-X/imageforge?style=flat-square&color=cyan)

</div>

---

## 📋 Table of Contents

- [🎯 Why ImageForge?](#-why-imageforge)
- [🧭 What It Does](#-what-it-does)
- [🚀 Quick Start](#-quick-start)
- [🖼️ Preview](#-preview)
- [📦 Installation](#-installation)
- [✨ Features](#-features)
- [⌨️ Usage](#%EF%B8%8F-usage)
- [⚙️ Configuration](#%EF%B8%8F-configuration)
- [🧰 Tech Stack](#-tech-stack)
- [⚠️ Disclaimer](#%EF%B8%8F-disclaimer)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)
- [👨‍💻 Developer](#-developer)

---

## 🎯 Why ImageForge?

> Batch-converting ten screenshots to WebP shouldn't mean hunting for a web uploader one file at a time. **ImageForge does it in two commands**: point it at one image or a whole folder and it converts, resizes, and compresses them - locally, in bulk, with a before/after size report.
>
> **No accounts, no uploads, no watermarks.** Everything happens on your machine with Pillow doing the heavy lifting.

---

## 🧭 What It Does

| # | Task | What it gives you |
|---|------|-------------------|
| 1️⃣ | Convert formats | PNG / JPG / WebP / BMP / TIFF - single file or an entire directory, in one pass |
| 2️⃣ | Resize & crop | Exact pixels (aspect preserved or not), center-crop to an aspect ratio |
| 3️⃣ | Rotate & flip | Rotate by any angle, flip horizontal / vertical / both |
| 4️⃣ | Batch rename | Prefix / suffix / numbered renaming with dimension-based filtering |
| 5️⃣ | Interactive or direct CLI | Same operations through a friendly menu or a flag-driven command |

---

## 🚀 Quick Start

```bash
git clone https://github.com/MrHacker-X/imageforge.git
cd imageforge
pip install -r requirements.txt
python imageforge.py                 # interactive menu
```

---

## 🖼️ Preview

<div align="center">

![ImageForge Preview](https://i.ibb.co/pvcLMjQW/imageforge.png)

</div>

---

## 📦 Installation

```bash
# 1. clone
git clone https://github.com/MrHacker-X/imageforge.git
cd imageforge

# 2. install dependencies
pip install -r requirements.txt

# 3. run
python imageforge.py
```

### Supported Systems

| OS | Status | Notes |
|----|--------|-------|
| 🐧 Linux | ✅ Fully supported | Any distro with Python 3.8+ |
| 🪟 Windows | ✅ Fully supported | Python from python.org, then the steps above |
| 🍎 macOS | ✅ Fully supported | `brew install python`, then the steps above |
| 📱 Termux (Android) | ✅ Fully supported | `pkg install python`, then the steps above |

> 💡 ImageForge never uploads your images anywhere - all conversion and compression happens locally via Pillow.

---

## ✨ Features

| | Feature | Description |
|---|---------|-------------|
| 🔄 | **Format conversion** | PNG, JPG/JPEG, WebP, BMP, TIFF, GIF - any direction the format supports |
| 📐 | **Smart resizing** | Exact pixels, percentage scale, or fit-within-box, with high-quality resampling |
| 🗜️ | **Quality control** | Adjustable compression (e.g. WebP/JPEG quality) with an optimized-save path |
| 📁 | **Batch mode** | Drop a directory and every supported image in it gets processed in one pass |
| 📊 | **Savings report** | Per-file original → result byte counts and a total spacesaved summary |
| 🎛️ | **Two modes** | A guided interactive menu or a fully flag-driven direct CLI |
| 🩹 | **Fail-fast validation** | A corrupt or unsupported file is skipped with one clear message |
| 🪶 | **Minimal dependencies** | `Pillow` + `rich`, nothing else |

---

## ⌨️ Usage

```bash
python imageforge.py                 # interactive menu
python imageforge.py -h              # help
python imageforge.py -v              # version
```

### Direct CLI

```bash
# convert a single image to webp
python imageforge.py photo.png -f webp

# convert every image in a folder to jpg at quality 85
python imageforge.py ./screens -f jpg -q 85

# resize a folder of images to 1280px wide, keeping aspect
python imageforge.py ./photos --width 1280

# center-crop to 16:9 and rotate 90 degrees
python imageforge.py photo.png --crop-aspect 16:9 --rotate 90
```

| Option | Values / Example | Meaning |
|--------|------------------|---------|
| `targets` | file(s) or directory (positional) | Images to process |
| `-f` / `--format` | `jpg` / `png` / `webp` / `bmp` / `tiff` | Target format for conversion |
| `--width` / `--height` | pixels | Resize target (aspect preserved unless `--no-aspect`) |
| `--crop` / `--crop-aspect` | `0,0,400,300` / `16:9` | Crop box or center-crop ratio |
| `--rotate` / `--flip` | degrees / `horizontal` `vertical` `both` | Orientation transforms |
| `-q` / `--quality` | 1–100 | Compression quality (lossy formats only) |
| `--prefix` / `--suffix` / `--number-pad` | strings / digits | Batch-rename options |
| `-o` / `--output-dir` | directory | Where results land |

---

## ⚙️ Configuration

Conversion behavior lives in [`core/config.py`](core/config.py):

| Setting | Default | Effect |
|---------|---------|--------|
| Format capabilities map | supported I/O per format | Which conversions each format allows |
| Default quality | high | Starting compression level for lossy saves |
| Resampling filter | LANCZOS | Quality of pixel resampling during resize |
| Output naming | `<name>_converted.<ext>` | Filename pattern for converted copies |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.8+ |
| Imaging | `Pillow` (format I/O, resize, optimize) |
| UI | `rich` (menus, colored tables, prompts) |

---

## ⚠️ Disclaimer

> ### Read this before using ImageForge.
>
> 1. **Work on your own images.** Only process files you own or are licensed to modify - converting someone else's copyrighted image doesn't transfer any rights to you.
> 2. **Keep originals.** ImageForge writes new files rather than overwriting, but a disk crash or a wrong `--out` is still your responsibility to recover from.
> 3. **Respect transparency.** Formats like JPEG have no alpha channel; converting a transparent PNG to JPG flattens it. The tool won't warn forever - check the result before deleting the original.
> 4. **No warranty.** ImageForge is provided "as is", with no warranty of any kind. The author is **not liable** for misuse or data loss from using this tool.

---

## 🤝 Contributing

Contributions are welcome!

```bash
# 1. fork it
# 2. create your branch
git checkout -b feature/amazing-feature
# 3. commit
git commit -m "Add amazing feature"
# 4. push
git push origin feature/amazing-feature
# 5. open a Pull Request
```

---

## 📜 License

ImageForge is the original project by MrHacker-X - see the [`LICENSE`](https://github.com/MrHacker-X/imageforge) file in the upstream repository for details.

---

## 👨‍💻 Developer

| | |
|---|---|
| **Dev** | MrHacker-X |
| **GitHub** | [github.com/MrHacker-X](https://github.com/MrHacker-X) |
| **Email** | [contact@vritrasec.com](mailto:contact@vritrasec.com) |
| **Website** | [vritrasec.com](https://vritrasec.com) |
| **Network** | [link.vritrasec.com](https://link.vritrasec.com) |

---

<div align="center">

### ⭐ Star the repo if ImageForge tamed your image pile ⭐

*Built by MrHacker-X - forge locally, save visibly.*

</div>
