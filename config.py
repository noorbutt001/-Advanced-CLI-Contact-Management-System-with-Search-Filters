"""
config.py
---------
Central configuration for the Contact Management System.
Keeping constants here means you only change them in ONE place.
"""

DATA_FILE = "contacts.json"
EXPORT_FILE = "contacts_export.csv"
PAGE_SIZE = 5

# Validation patterns
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
PHONE_REGEX = r"^\+?\d{7,15}$"