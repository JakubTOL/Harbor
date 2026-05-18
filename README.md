# Harbor

A modular, Finder-inspired file explorer built with Python and PySide6, designed with clean architecture principles (MVC + service layer separation).

---

## Overview

**Harbor** is a desktop file explorer designed to improve navigation clarity and speed when working with complex directory structures. It blends two interaction models:

- **Tree-based navigation** for structural overview
- **Finder-style** for contextual browsing
- **Breadcrumb** navigation
- Clean architectural separation

The goal is to provide a clean, modular, and extensible architecture suitable for further feature expansion.

---

## Architecture

Harbor follows a **domain-oriented modular architecture**, designed to isolate UI, logic, and filesystem operations.

### High-level structure

project/
│
├── main.py  
│  
├── core/  
│   └── constants.py  
│  
├── domains/  
│   └── explorer/  
│       ├── models/  
│       │   └── explorer_state.py  
│       │  
│       ├── services/  
│       │   └── filesystem_service.py  
│       │  
│       ├── controllers/  
│       │   └── explorer_controller.py  
│       │  
│       ├── widgets/  
│       │   ├── breadcrumb_bar.py  
│       │   ├── navigation_toolbar.py  
│       │   ├── explorer_tree.py  
│       │   ├── finder_column_view.py  
│       │   └── status_bar.py  
│       │  
│       └── views/  
│           └── explorer_window.py  


---

## Running the project

- Requirements:
  - Python 3.10+
  - PySide6

- Install dependencies
```bash
pip install PySide6
```
- Run:
```bash
python main.py
```
## License
The project is under MIT license.
