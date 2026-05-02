"""
main.py
-------
UI Layer: The user-facing entry point.
Handles ALL input/output. Calls controller for logic, storage for persistence.
"""

from config import PAGE_SIZE, EXPORT_FILE
from storage import load_contacts, export_to_csv, import_from_csv
from controller import (
    validate_contact,
    create_contact,
    update_contact,
    delete_contact,
    toggle_favorite,
    search_contacts,
    filter_contacts,
    filter_favorites,
    sort_contacts,
    find_by_id_or_name,
    is_valid_email,
    is_valid_phone,
    is_non_empty,
    normalize_imported,
)
from storage import save_contacts


# -------------------- UI HELPERS --------------------
def prompt(label: str, validator=None, error_msg: str = "Invalid input.") -> str:
    """Generic input prompt with optional validation."""
    while True:
        value = input(label).strip()
        if validator is None:
            if is_non_empty(value):
                return value
            print("⚠️ Field cannot be empty.")
        else:
            if validator(value):
                return value
            print(f"⚠️ {error_msg}")


def print_table(contacts: list) -> None:
    if not contacts:
        print("\nNo contacts to display.\n")
        return

    headers = ["ID", "★", "Name", "Phone", "Email", "City", "Company"]
    rows = [
        [
            c["id"][:8],
            "★" if c.get("favorite") else " ",
            c["name"],
            c["phone"],
            c["email"],
            c["city"],
            c["company"],
        ]
        for c in contacts
    ]

    widths = [max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))]
    sep = "+".join("-" * (w + 2) for w in widths)

    print(f"\n+{sep}+")
    print("| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |")
    print(f"+{sep}+")
    for r in rows:
        print("| " + " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(r)) + " |")
    print(f"+{sep}+\n")


def paginate(contacts: list) -> None:
    total = len(contacts)
    if total == 0:
        print_table(contacts)
        return

    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    page = 0
    while True:
        start, end = page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE
        print(f"\nPage {page + 1}/{pages}")
        print_table(contacts[start:end])
        if pages <= 1:
            break
        nav = input("[n]ext  [p]rev  [q]uit: ").strip().lower()
        if nav == "n" and page < pages - 1:
            page += 1
        elif nav == "p" and page > 0:
            page -= 1
        elif nav == "q":
            break


# -------------------- UI ACTIONS --------------------
def ui_add(contacts):
    print("\n--- ➕ Add Contact ---")
    name = prompt("Full Name: ")
    phone = prompt("Phone: ", is_valid_phone, "Invalid phone (7–15 digits, optional +).")
    email = prompt("Email: ", is_valid_email, "Invalid email format.")
    city = prompt("City: ")
    company = prompt("Company: ")

    valid, err = validate_contact(name, phone, email, city, company)
    if not valid:
        print(f"⚠️ {err}")
        return

    contact = create_contact(contacts, name, phone, email, city, company)
    print(f"✅ Added '{contact['name']}' (ID: {contact['id'][:8]})\n")


def ui_view(contacts):
    print("\n--- 📒 View Contacts ---")
    if not contacts:
        print("No contacts.\n")
        return
    print("Sort: 1) A-Z  2) Z-A  3) Recent  (Enter to skip)")
    mode = {"1": "az", "2": "za", "3": "recent"}.get(input("Choose: ").strip(), "default")
    paginate(sort_contacts(contacts, mode))


def ui_search(contacts):
    print("\n--- 🔍 Search ---")
    print("1) Name  2) Phone  3) Email")
    field = {"1": "name", "2": "phone", "3": "email"}.get(input("Choose: ").strip())
    if not field:
        print("⚠️ Invalid choice.")
        return
    query = input("Search term: ").strip()
    results = search_contacts(contacts, field, query)
    print(f"\nFound {len(results)} result(s).")
    print_table(results)


def ui_filter(contacts):
    print("\n--- 🎛 Filter ---")
    print("1) City  2) Company  3) Favorites")
    choice = input("Choose: ").strip()
    if choice == "1":
        results = filter_contacts(contacts, "city", input("City: "))
    elif choice == "2":
        results = filter_contacts(contacts, "company", input("Company: "))
    elif choice == "3":
        results = filter_favorites(contacts)
    else:
        print("⚠️ Invalid choice.")
        return
    print(f"\nFound {len(results)} result(s).")
    print_table(results)


def ui_update(contacts):
    print("\n--- ✏️ Update Contact ---")
    ident = input("Contact ID or Name: ").strip()
    contact = find_by_id_or_name(contacts, ident)
    if not contact:
        print("⚠️ Not found.")
        return

    print("Press Enter to keep existing value.")
    updates = {}
    for field in ["name", "phone", "email", "city", "company"]:
        new_val = input(f"{field.capitalize()} [{contact[field]}]: ").strip()
        if not new_val:
            continue
        if field == "phone" and not is_valid_phone(new_val):
            print("⚠️ Invalid phone — skipped.")
            continue
        if field == "email" and not is_valid_email(new_val):
            print("⚠️ Invalid email — skipped.")
            continue
        updates[field] = new_val

    if updates and update_contact(contacts, contact["id"], updates):
        print("✅ Updated.\n")
    else:
        print("Nothing changed.\n")


def ui_delete(contacts):
    print("\n--- 🗑 Delete Contact ---")
    ident = input("Contact ID or Name: ").strip()
    contact = find_by_id_or_name(contacts, ident)
    if not contact:
        print("⚠️ Not found.")
        return
    confirm = input(f"Delete '{contact['name']}'? (y/n): ").strip().lower()
    if confirm == "y" and delete_contact(contacts, ident):
        print("✅ Deleted.\n")
    else:
        print("Cancelled.\n")


def ui_favorite(contacts):
    print("\n--- ⭐ Toggle Favorite ---")
    ident = input("Contact ID or Name: ").strip()
    contact = toggle_favorite(contacts, ident)
    if not contact:
        print("⚠️ Not found.")
        return
    state = "added to" if contact["favorite"] else "removed from"
    print(f"✅ '{contact['name']}' {state} favorites.\n")


def ui_export(contacts):
    fname = input(f"Export filename (default: {EXPORT_FILE}): ").strip() or EXPORT_FILE
    if export_to_csv(contacts, fname):
        print(f"✅ Exported to {fname}\n")
    else:
        print("⚠️ Export failed (no contacts?).\n")


def ui_import(contacts):
    fname = input("CSV file path: ").strip()
    try:
        rows = import_from_csv(fname)
        new_rows = normalize_imported(rows)
        contacts.extend(new_rows)
        save_contacts(contacts)
        print(f"✅ Imported {len(new_rows)} contacts.\n")
    except Exception as e:
        print(f"⚠️ {e}\n")


# -------------------- MENU --------------------
def show_menu():
    print("=" * 50)
    print("📇  CONTACT MANAGEMENT SYSTEM (Mini CRM)")
    print("=" * 50)
    print(" 1. Add Contact")
    print(" 2. View All Contacts")
    print(" 3. Search Contacts")
    print(" 4. Filter Contacts")
    print(" 5. Update Contact")
    print(" 6. Delete Contact")
    print(" 7. Toggle Favorite ⭐")
    print(" 8. Export to CSV")
    print(" 9. Import from CSV")
    print(" 0. Exit")
    print("=" * 50)


def main():
    contacts = load_contacts()
    actions = {
        "1": ui_add,
        "2": ui_view,
        "3": ui_search,
        "4": ui_filter,
        "5": ui_update,
        "6": ui_delete,
        "7": ui_favorite,
        "8": ui_export,
        "9": ui_import,
    }

    while True:
        try:
            show_menu()
            choice = input("Enter choice: ").strip()
            if choice == "0":
                print("👋 Goodbye!")
                break
            action = actions.get(choice)
            if action:
                action(contacts)
            else:
                print("⚠️ Invalid option.\n")
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}\n")


if __name__ == "__main__":
    main()