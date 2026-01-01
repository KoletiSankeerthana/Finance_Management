# 💰 Expense Tracker: Professional Financial Intelligence

A high-performance, executive-grade financial management application built with **Streamlit**, **Pandas**, and **Plotly**. Designed for individuals who demand precision and clarity in their financial tracking.

## ✨ Core Intelligence

- **Executive Dashboard**: Real-time spending trajectory with WoW/MoM analysis.
- **Strategic Budgeting**: Intelligent limit management with automated overflow alerts.
- **Categorical Insights**: Dynamic transaction identification and precise grouping.
- **Mobile-Responsive UI**: Premium typography (Times New Roman) and glassmorphism design.
- **Data Integrity**: Secure SQLite storage with strict schema enforcement.

---

## 🚀 Deployment Guide

### Option 1: Streamlit Cloud (Recommended)
This is the fastest way to host your tracker for free.

1. **Push to GitHub**: Ensure all code is pushed to your repository.
2. **Connect to Streamlit**: Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub account.
3. **Deploy**: Select this repository and the `streamlit_app.py` file.
4. **Done**: Your app will be live at a custom URL!

### Option 2: Local Setup
1. **Clone the Repo**
   ```bash
   git clone https://github.com/KoletiSankeerthana/Expense_Tracker.git
   cd Expense_Tracker
   ```
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Application**
   ```bash
   streamlit run streamlit_app.py
   ```

---

## 🛠️ Architecture
- **`src/database/`**: Robust CRUD layer and schema initialization.
- **`src/pages/`**: Modularized view components for different features.
- **`src/utils/`**: Shared navigation logic and UI constants.

---
*Created by [Sankeerthana Koleti](https://github.com/KoletiSankeerthana)*
