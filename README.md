# FinancePro: Enterprise-Grade Expense Tracker

A professional, secure, and feature-rich financial management application built with Streamlit and SQLite.

## ✨ Features

- **Executive Dashboard**: Real-time spending trends, category distribution, and KPI insights.
- **Secure Authentication**: Bcrypt-backed password hashing and isolated user databases.
- **Advanced CRUD**: Manage transactions, accounts, and categories with precision.
- **Budgeting System**: Set monthly/yearly limits with automated threshold alerts (75%/90%).
- **Financial Analytics**: Deep dive into spending habits with Plotly-powered visualizations.
- **Smart Insights**: Rule-based intelligence for detecting unusual spikes and saving tips.
- **Import/Export**: Bulk data management via CSV and Excel.
- **Premium UI**: Clean, monochromatic design with focus on readability and modern typography.

## 🛠️ Tech Stack

- **Frontend/Framework**: [Streamlit](https://streamlit.io/)
- **Database**: SQLite3
- **Data Analysis**: Pandas, NumPy
- **Visualizations**: Plotly Express
- **Security**: Bcrypt

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run streamlit_app.py
```

### 3. Login
- **Username**: `testuser`
- **Password**: `password123`
*(Or Register a new account)*

## 📂 Project Structure

- `main.py`: Entry point and navigation router.
- `src/auth/`: Security and session management.
- `src/database/`: Schema definitions and CRUD logic.
- `src/pages/`: Individual module implementations.
- `src/components/`: Reusable UI elements and charts.
- `src/utils/`: Formatting and validation helpers.
