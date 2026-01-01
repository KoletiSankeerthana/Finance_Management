# src/utils/constants.py

# --- UI Branding ---
APP_TITLE = "EXPENSE TRACKER"
APP_SUBTITLE = "Smart & Simple Personal Finance Manager"
PRIMARY_COLOR = "#008080"  # Teal
SECONDARY_COLOR = "#0d1117"
ACCENT_SUCCESS = "#2ecc71"
ACCENT_ERROR = "#e74c3c"
ACCENT_WARNING = "#f1c40f"

# --- Categories & Icons ---
# Mapping category names to their professional icons
CATEGORY_ICONS = {
    "Online Shopping": "",
    "Grocery": "🥦",
    "Healthcare": "🏥",
    "Entertainment": "🎬",
    "Bills": "💡",
    "Donation": "🤝",
    "Recharge": "📱",
    "Subscriptions": "🔁",
    "Transportation": "",
    "Food & Dining": "🍽️",
    "Utilities": "🛠️",
    "Shopping": "🛍️",
    "Others": "🏷️"
}

CATEGORIES = list(CATEGORY_ICONS.keys())

# --- Payment Modes ---
PAYMENT_MODES = ["Cash", "UPI", "Card", "Bank Transfer"]

# --- Budgeting ---
BUDGET_PERIODS = ["Weekly", "Monthly"]
BUDGET_THRESHOLDS = {
    "safe": 0.70,     # Green < 70%
    "warning": 0.90,  # Yellow 70-90%
    "danger": 1.0     # Red > 100%
}
