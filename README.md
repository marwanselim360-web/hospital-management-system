# 🏥 Hospital Management System

A professional Hospital Management System developed using **Python**, **Tkinter**, and **MySQL** for managing hospital operations efficiently through a graphical user interface (GUI).

This project was created as a university Database Systems project and includes advanced hospital features such as patient registration, appointment scheduling, billing, room management, doctor scheduling, and AI-powered SQL querying.

---

# ✨ Features

## 👨‍⚕️ Patient Management
- Register new patients
- Update patient information
- Delete patients
- View all registered patients
- Blood type and gender validation

---

## 📅 Appointment System
- Smart appointment booking
- Doctor specialization filtering
- Automatic least-loaded doctor suggestion
- Real-time available slot detection
- Rescheduling appointments
- Appointment cancellation
- Appointment status tracking:
  - Scheduled
  - Pending
  - Completed
  - Cancelled

---

## 🩺 Doctor Panel
- View doctor patients
- Add medical tests
- Prescribe medications
- Manage patient treatments

---

## 📆 Doctor Scheduling
- Set doctor working days
- Add doctor days off
- Automatic appointment conflict handling

---

## 🛏️ Room & Admission Management
- Admit patients
- Assign hospital rooms
- Discharge patients
- Track room availability and capacity

---

## 💳 Billing & Payments
- Calculate patient bills
- Track payments
- Payment status management
- Invoice & receipt generation
- Export receipts as PDF

---

## 🤖 AI Hospital Assistant
- Converts natural language questions into SQL queries
- Supports English and Arabic prompts
- Uses Groq AI integration

### Example:
```text
How many appointments were booked today?
````

---

# 🛠️ Technologies Used

* Python
* Tkinter
* MySQL
* mysql.connector
* SQL
* Groq API
* PDF Export System

---

# 🗂️ Database Design

The database includes entities such as:

* Patient
* Doctor
* Nurse
* Staff
* Department
* Appointment
* Payment
* Medication
* Test
* Room
* Admission
* Prescribed

The project also includes:

* ERD Diagram
* Relational Model
* Requirement Analysis Documentation

---

# 📸 System Modules

* Patient Registration
* Appointment Booking
* Appointment Management
* Doctor Panel
* Doctor Scheduling
* Room Admission
* Payments
* Invoices & Receipts
* AI Assistant
* Search System

---

# ⚙️ Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/hospital-management-system.git
```

---

## 2️⃣ Open Project Folder

```bash
cd hospital-management-system
```

---

## 3️⃣ Install Required Packages

```bash
pip install mysql-connector-python
```

---

## 4️⃣ Setup MySQL Database

1. Open MySQL Workbench
2. Create a database named:

```sql
CREATE DATABASE hospital;
```

3. Run the SQL file included in the project.

---

## 5️⃣ Configure Database Connection

Inside the Python file, update:

```python
host="localhost",
user="root",
password="YOUR_PASSWORD",
database="hospital"
```

---

## 6️⃣ Run the Project

```bash
python "DB GUI 2.py"
```

---

# 🔐 Security Note

Do NOT upload:

* API keys
* Database passwords
* `.env` files

Add them to `.gitignore`.

Example:

```gitignore
__pycache__/
*.pyc
.env
groq_key.txt
```

---

# 📚 Documentation Included

* Requirement Analysis
* ERD Diagram
* Relational Model
* SQL File
* GUI Source Code

---

# 🎯 Project Objectives

* Apply database concepts in a real-world system
* Build a professional GUI application
* Demonstrate SQL integration with Python
* Implement hospital workflow automation
* Practice software engineering and database design

---

# 👩‍💻 Developed By

**Marwan selim**
Computer Science Student — AI Major

---

# 📄 License

This project is for educational purposes only.