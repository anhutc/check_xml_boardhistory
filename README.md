# ASM BoardHistory
A professional desktop application for viewing and analyzing ASM board history XML files with an intuitive graphical interface.

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-lightgrey.svg)

## 📖 Overview

ASM BoardHistory Viewer is a powerful tool designed to parse, analyze, and visualize ASM machine board history data from XML files. It provides detailed insights into Pickup and Placement operations with a modern, user-friendly interface.

## ✨ Features

### 🔍 Data Import & Management
- **Multi-file Import**: Import multiple XML files simultaneously
- **Smart Filtering**: Real-time filtering for barcodes, references, and panels
- **Data Persistence**: Maintains imported file history across sessions

### 📊 Detailed Analysis
- **Pickup Information**: Comprehensive pickup data including time, machine, head, segment, nozzle, and component details
- **Placement Details**: Complete placement information with measurements, vacuum data, and error analysis
- **Visual Indicators**: Color-coded data presentation for better readability

### 🎨 Modern Interface
- **Responsive Design**: Clean, modern UI with gradient themes
- **Progress Tracking**: Visual progress bar for file import operations
- **Context Menus**: Right-click functionality for quick actions

## 🚀 Installation

### Quick Start
- Download ASM BoardHistory: [releases (ASM.BoardHistory.x.x.x.exe)](https://github.com/anhutc/check_xml_boardhistory/releases)

### Getting Started with Python
1. **Prerequisites**
- Python 3.6 or higher
- PyQt5 library
2. **Clone the repository**
   ```bash
   git clone https://github.com/anhutc/check_xml_boardhistory.git
   ```

3. **Install dependencies**
   ```bash
   pip install PyQt5
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## 📖 How to Use

### Basic Workflow
1. **Import Files**: Click "Import Board (xml)" to select XML files
2. **Select Barcode**: Choose a barcode from the left panel
3. **Filter Data**: Use search boxes to filter barcodes, refs, or panels
4. **View Details**: Click on ref and panel items to see detailed Pickup and Placement data
5. **Copy Data**: Double-click any table cell to copy its value

### Interface Overview
- **Left Panel**: File management and data filtering
- **Right Panel**: Detailed Pickup and Placement information
- **Bottom Bar**: Progress indicators and version information

## 🗂️ Supported File Format

The application processes standard ASM Board History XML files containing:
- Board identification data
- Pickup and placement histories
- Machine configuration information
- Component measurement data

## 📈 Version History

### Version 1.1.1 (Current)
- Add version history view feature
- Improved user interface
- Fix content display error
- Fix x-out placement data

### Version 1.1.0
- Fix high RAM error when importing multiple files

### Version 1.0.0
- First version
- Read and parse XML Board History file
- Display basic Pickup and Placement information

## 🛠️ Technical Details

### Built With
- **Python** - Core programming language
- **PyQt5** - GUI framework
- **XML.etree** - XML parsing library

## 👨‍💻 Developer

**DANG VAN ANH**  
- Website: [https://anhutc.github.io](https://anhutc.github.io)
- GitHub: [@anhutc](https://github.com/anhutc)

---

<div align="center">

**If you find this tool useful, please consider giving it a ⭐ on GitHub!**

</div>
