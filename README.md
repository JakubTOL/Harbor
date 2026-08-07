<p align="center">
  <img src="resources/harbor.png" alt="Harbor Logo" height="120"/>
</p>

<h1 align="center">Harbor</h1>
<p align="center">
  <b>A modular, cross-platform file explorer built with Python and PySide6</b><br>
  <i>Finder-inspired • Clean Architecture • Extensible by design</i>
  
  <br><br>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"/>
  </a>
</p>

---

## 📝 Summary

**Harbor** is a modern, customizable desktop file explorer designed for efficient navigation of complex directory structures. Blending tree-based browsing with Finder-style context and breadcrumb navigation, Harbor adopts a clear architecture (MVC + Domain/Service) to ensure maintainability and future feature growth.

---

## 🚀 Overview

- **Cross-Platform:** Runs anywhere Python & PySide6 are supported.
- **User-Centric UI:** Combines tree navigation, column (Finder) view, and breadcrumbs for clear directory traversal.
- **Modular Clean Architecture:** Clean code boundaries - domain logic, UI, filesystem, and services are well-separated.
- **Extensible:** Easily add new widgets, views, or integrations.
- **MIT Licensed:** Free and open for commercial or personal use.

---

## 🏛️ Architecture

Harbor employs a **domain-oriented modular architecture** inspired by Clean Architecture and MVC. This facilitates rapid development, scaling, and testing while maintaining clear code boundaries.

```
project/
│
├── main.py  
│  
├── core/                # Core constants and shared infrastructure
│   └── constants.py
│  
├── domains/
│   └── explorer/        # Main functional domain
│   │   ├── models/      # State/data structures
│   │   │   ├── explorer_state.py
│   │   │   └── search_results.py
│   │   ├── services/    # Business logic, e.g., filesystem operations
│   │   │   ├── filesystem_service.py
│   │   │   └── search_service.py
│   │   ├── controllers/ # Interface between UI and logic
│   │   │   └── explorer_controller.py
│   │   ├── widgets/     # Modular UI components
│   │   │   ├── breadcrumb_bar.py
│   │   │   ├── explorer_tree.py
│   │   │   ├── file_metadata_panel.py
│   │   │   ├── finder_column_view.py
│   │   │   ├── navigation_toolbar.py
│   │   │   ├── search_widget.py
│   │   │   └── status_bar.py
│   │   └── views/       # Composed/primary UI windows
│   │       └── explorer_window.py
│   └── application/        # Centralized application startup
|       ├── app.py/      # Application logic
|       └── favorites_manager.py/      # Favorites directories manager
│ 
├── resources/        # Folder for media storage
│   └── icons/        # files with .ico files
```

**Component Interactions:**
- **Models** capture UI and navigation state.
- **Services** handle domain-specific logic and filesystem manipulation.
- **Controllers** mediate between views and logic, processing user actions.
- **Widgets** provide focused UI building blocks.
- **Views** assemble widgets, orchestrating complete windows/dialogs.

> **Tip:** This design supports testability (especially of service/controller layers) and simplifies onboarding for new contributors.

---

## 🖥️ Getting Started

### Requirements

- Python 3.10+
- [PySide6](https://pypi.org/project/PySide6/)
- PyInstaller (optional; required only for code conversion)

### Installation

```bash
pip install PySide6
```

### Running Harbor

```bash
python main.py
```

### Converting to executable with use of .venv (Windows)

- Install a PyInstaller
```bash
pip install pyinstaller
```
- Run the converter command from active .venv
```bash
.venv\Scripts\python -m PyInstaller --onefile --windowed --icon=resources/icons/harbor.ico --add-data "resources/icons/harbor.ico;resources/icons" --add-data "resources/harbor_splash2.png;resources" main.py
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
