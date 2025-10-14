```markdown
# ASM BoardHistory Viewer

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
- **Copy Functionality**: Easy data copying from tables

## 🚀 Installation

### Prerequisites
- Python 3.6 or higher
- PyQt5 library

### Quick Start
1. **Clone the repository**
   ```bash
   git clone https://github.com/anhutc/asm-boardhistory-viewer.git
   cd asm-boardhistory-viewer
   ```

2. **Install dependencies**
   ```bash
   pip install PyQt5
   ```

3. **Run the application**
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

## 🤝 Contributing

We welcome contributions! Please feel free to submit pull requests, report bugs, or suggest new features.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Developer

**DANG VAN ANH**  
- Website: [https://anhutc.github.io](https://anhutc.github.io)
- GitHub: [@anhutc](https://github.com/anhutc)

---

<div align="center">

**If you find this tool useful, please consider giving it a ⭐ on GitHub!**

</div>
```