"""
controller.py
-------------
Logic Layer: Contains the brain of the application.
Handles validation, searching, filtering, and CRUD logic.
Does NOT touch UI (no print/input) and does NOT touch files directly.
"""

import re
import uuid
from datetime import datetime
from config import EMAIL_REGEX, PHONE_REGEX
from storage import save_contacts


# -------------------- VALIDATION --------------------
def is_valid_email(email: str) -> bool:
    return bool(re.match(EMAIL_REGEX, email or ""))


def is_valid_phone(phone: str) -> bool:
    return bool(re.match(PHONE_REGEX, phone or ""))


def is_non_empty(value: str) -> bool:
    return bool(value and value.strip())


def validate_contact(name, phone, email, city, company) -> tuple[bool, str]:
    """Returns (is_valid, error_message)."""
    if not all(map(is_non_empty, [name, phone, email, city, company])):
        return False, "All fields are required."
    if not is_valid_phone(phone):
        return False, "Invalid phone (digits only, 7–15 chars, optional +)."
    if not is_valid_email(email):
        return False, "Invalid email format."
    return True, ""


# -------------------- CRUD --------------------
def create_contact(contacts, name, phone, email, city, company) -> dict:
    """Create a new contact dict, append, save, and return it."""
    contact = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "phone": phone.strip(),
        "email": email.strip(),
        "city": city.strip(),
        "company": company.strip(),
        "favorite": False,
        "created_at": datetime.now().isoformat(),
    }
    contacts.append(contact)
    save_contacts(contacts)
    return contact


def update_contact(contacts, contact_id, updates: dict) -> bool:
    """Update fields of a contact. Returns True if updated."""
    contact = find_by_id_or_name(contacts, contact_id)
    if not contact:
        return False
    for key, value in updates.items():
        if value:  # ignore empty
            contact[key] = value
    save_contacts(contacts)
    return True


def delete_contact(contacts, identifier) -> bool:
    """Delete a contact by ID or name."""
    contact = find_by_id_or_name(contacts, identifier)
    if not contact:
        return False
    contacts.remove(contact)
    save_contacts(contacts)
    return True


def toggle_favorite(contacts, identifier) -> dict | None:
    contact = find_by_id_or_name(contacts, identifier)
    if not contact:
        return None
    contact["favorite"] = not contact.get("favorite", False)
    save_contacts(contacts)
    return contact


# -------------------- SEARCH / FILTER --------------------
def find_by_id_or_name(contacts, identifier: str):
    """Find a contact by full ID, short ID (8 chars), or exact name (case-insensitive)."""
    if not identifier:
        return None
    ident = identifier.strip().lower()
    for c in contacts:
        if (
            c["id"].lower() == ident
            or c["id"][:8].lower() == ident
            or c["name"].lower() == ident
        ):
            return c
    return None


def search_contacts(contacts, field: str, query: str) -> list:
    """Case-insensitive partial search by 'name', 'phone', or 'email'."""
    if field not in ("name", "phone", "email"):
        return []
    q = query.strip().lower()
    return [c for c in contacts if q in c.get(field, "").lower()]


def filter_contacts(contacts, field: str, value: str) -> list:
    """Filter contacts by 'city' or 'company' (exact match, case-insensitive)."""
    if field not in ("city", "company"):
        return []
    v = value.strip().lower()
    return [c for c in contacts if c.get(field, "").lower() == v]


def filter_favorites(contacts) -> list:
    return [c for c in contacts if c.get("favorite")]


# -------------------- SORTING --------------------
def sort_contacts(contacts, mode: str) -> list:
    """Modes: 'az', 'za', 'recent'."""
    if mode == "az":
        return sorted(contacts, key=lambda c: c["name"].lower())
    if mode == "za":
        return sorted(contacts, key=lambda c: c["name"].lower(), reverse=True)
    if mode == "recent":
        return sorted(contacts, key=lambda c: c.get("created_at", ""), reverse=True)
    return contacts


# -------------------- IMPORT NORMALIZATION --------------------
def normalize_imported(rows: list) -> list:
    """Ensure imported CSV rows have required fields."""
    normalized = []
    for row in rows:
        row.setdefault("id", str(uuid.uuid4()))
        row.setdefault("favorite", False)
        row.setdefault("created_at", datetime.now().isoformat())
        normalized.append(row)
    return normalized