# 📇 Contact Management System (Mini CRM)

A professional CLI Contact Manager built with a clean **3-Layer Architecture**.

## 🏗 Architecture

| Layer  | File           | Responsibility                                |
|--------|----------------|-----------------------------------------------|
| UI     | `main.py`      | Menus, input/output                           |
| Logic  | `controller.py`| Validation, search, filter, CRUD rules        |
| Data   | `storage.py`   | Read/write JSON & CSV                         |
| Config | `config.py`    | Constants (file paths, page size, regex)      |

## ▶️ Run

```bash
python main.py