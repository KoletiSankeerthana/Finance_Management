import streamlit as st

def format_currency(amount, currency="₹"):
    # V3 requirement: Display as positive, use color for logic
    return f"{currency} {abs(amount):,.2f}"

def get_status_color(amount, type="Expense"):
    if type == "Expense":
        return "#ff4b4b" # Red
    return "#00d1b2" # Teal/Green

def format_date(date_obj, fmt="YYYY-MM-DD"):
    if fmt == "DD/MM/YYYY":
        return date_obj.strftime("%d/%m/%Y")
    elif fmt == "MM/DD/YYYY":
        return date_obj.strftime("%m/%d/%Y")
    return date_obj.strftime("%Y-%m-%d")
