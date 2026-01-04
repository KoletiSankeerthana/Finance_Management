
# 💰 Expense Tracker – Professional Personal Finance Manager

Expense Tracker is a **web-based personal finance management application** built using **Python, Streamlit, and SQLite**.  
It helps users **record daily expenses, manage budgets, and analyze spending patterns** through a clean, professional, and user-friendly interface.

This project is designed with a strong focus on **real-world usability, accurate data handling, responsive UI, and smooth navigation**, making it suitable for **portfolio presentation and internship evaluation**.

---

## 📌 Project Objective

The main objective of this project is to provide a simple yet effective way to:
- Track personal expenses
- Understand spending habits
- Manage budgets efficiently
- Visualize financial data clearly

---

## 🚀 Features

### 🔐 Authentication
- Secure login and logout
- Password update with confirmation
- User-specific data handling

---

### 🏠 Home Page
- Introduction to the Expense Tracker
- Clear explanation of:
  - What the application does
  - How to use each section
- Designed to help new users understand the app easily

---

### 📊 Dashboard
- Financial overview with:
  - Weekly expense summary
  - Monthly expense summary (with month and year)
  - Yearly expense summary
  - Highest single expense
- Budget status display:
  - Total budget
  - Amount spent
  - Remaining or overspent amount
- Daily spending trend visualization
- Responsive and professional layout

---

### 💸 Expenses
- Add expenses with:
  - Category
  - Amount (default value set to 0)
  - Payment method
  - Date selection
  - Optional description
- View all expenses in a clean table format
- Edit existing expense records
- Delete selected expense records
- Expandable sections to avoid clutter

---

### 🗂 Categories
- List of expense categories with icons
- Dynamic transaction count:
  - Counts are calculated based on actual expenses
  - No hardcoded or default values
- Safe deletion logic:
  - Categories linked to expenses cannot be deleted
- Compact and well-organized layout

---

### 📈 Analytics
- Category-wise expense distribution
- Payment method analysis
- Daily and monthly spending trends
- Clean charts with readable legends
- No duplicated or misleading data

---

### 🎯 Budgets
- Set monthly budgets (global or category-wise)
- Track:
  - Total budget
  - Amount spent
  - Remaining or overspent budget
- Budget values update automatically based on expenses

---

### ⚙️ Settings
- View user account information
- Change password securely
- Currency preference
- Data management options

---

## 🧭 Navigation
- Persistent sidebar across all pages
- Toggle button always visible
- Sidebar can be opened or closed by user choice
- Smooth navigation between:
  - Home
  - Dashboard
  - Expenses
  - Categories
  - Analytics
  - Budgets
  - Settings

---

## 🛠 Technology Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** SQLite
- **Data Processing:** Pandas
- **Visualization:** Matplotlib / Plotly
- **Version Control:** Git & GitHub
- **Deployment:** Streamlit Cloud

---

## 📂 Project Structure

```

expense-tracker/
│
├── streamlit_app.py
├── requirements.txt
├── expenses.db
│
├── src/
│   ├── pages/
│   │   ├── home.py
│   │   ├── dashboard.py
│   │   ├── expenses.py
│   │   ├── categories.py
│   │   ├── analytics.py
│   │   ├── budgets.py
│   │   └── settings.py
│   │
│   ├── auth/
│   │   └── security.py
│   │
│   └── utils/
│       ├── db.py
│       ├── helpers.py
│       └── constants.py
│
└── README.md

````

---

## ▶️ How to Run the Project Locally

### Step 1: Clone the Repository
```bash
git clone https://github.com/<your-username>/expense-tracker.git
````

### Step 2: Navigate to Project Directory

```bash
cd expense-tracker
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
streamlit run streamlit_app.py
```

The application will open in your browser at:

```
http://localhost:8501
```

---

## 🌐 Deployment

The application is deployed using **Streamlit Cloud**, connected directly to the GitHub repository for seamless updates and easy access.

* **Live Application:** https://expensetracker-g7zeguupnkodzsm9fhuyge.streamlit.app/
* 

```
