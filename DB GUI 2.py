import tkinter as tk
import re
import os
import json
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from datetime import datetime, timedelta

# ================= DB =================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Orange$2020",
        database="hospital"
    )


# ================= APP =================
class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System")
        self.root.geometry("1250x780")
        self.root.minsize(1150, 720)
        self.root.configure(bg="#F4F7FA")

        self.colors = {
            "bg": "#F4F7FA",
            "card": "#FFFFFF",
            "primary": "#2563EB",
            "primary_dark": "#1E3A8A",
            "accent": "#0EA5E9",
            "success": "#16A34A",
            "warning": "#F59E0B",
            "danger": "#DC2626",
            "text": "#111827",
            "muted": "#64748B",
            "border": "#D9E2EC",
            "table": "#F8FAFC",
            "sidebar": "#0F172A"
        }

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.setup_styles()
        self.login_screen()

    # ================= STYLE HELPERS =================
    def setup_styles(self):
        c = self.colors

        self.style.configure("TFrame", background=c["bg"])
        self.style.configure("Card.TFrame", background=c["card"])
        self.style.configure("Sidebar.TFrame", background=c["sidebar"])

        self.style.configure(
            "TLabel",
            background=c["bg"],
            foreground=c["text"],
            font=("Segoe UI", 10)
        )

        self.style.configure(
            "Card.TLabel",
            background=c["card"],
            foreground=c["text"],
            font=("Segoe UI", 10)
        )

        self.style.configure(
            "Title.TLabel",
            background=c["bg"],
            foreground=c["primary_dark"],
            font=("Segoe UI", 24, "bold")
        )

        self.style.configure(
            "Subtitle.TLabel",
            background=c["bg"],
            foreground=c["muted"],
            font=("Segoe UI", 10)
        )

        self.style.configure(
            "SidebarTitle.TLabel",
            background=c["sidebar"],
            foreground="white",
            font=("Segoe UI", 18, "bold")
        )

        self.style.configure(
            "SidebarSubtitle.TLabel",
            background=c["sidebar"],
            foreground="#CBD5E1",
            font=("Segoe UI", 10)
        )

        self.style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 8),
            background=c["primary"],
            foreground="white",
            borderwidth=0
        )
        self.style.map("TButton", background=[("active", c["primary_dark"])], foreground=[("active", "white")])

        self.style.configure("Success.TButton", background=c["success"], foreground="white")
        self.style.map("Success.TButton", background=[("active", "#15803D")])

        self.style.configure("Danger.TButton", background=c["danger"], foreground="white")
        self.style.map("Danger.TButton", background=[("active", "#991B1B")])

        self.style.configure("Warning.TButton", background=c["warning"], foreground="white")
        self.style.map("Warning.TButton", background=[("active", "#B45309")])

        self.style.configure("TEntry", padding=7, fieldbackground="white", background="white")
        self.style.configure("TCombobox", padding=7, fieldbackground="white", background="white")

        self.style.configure(
            "TLabelframe",
            background=c["card"],
            foreground=c["primary_dark"],
            borderwidth=1,
            relief="solid"
        )
        self.style.configure(
            "TLabelframe.Label",
            background=c["card"],
            foreground=c["primary_dark"],
            font=("Segoe UI", 11, "bold")
        )

        self.style.configure(
            "Treeview",
            background=c["table"],
            fieldbackground=c["table"],
            foreground=c["text"],
            rowheight=30,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        self.style.configure(
            "Treeview.Heading",
            background=c["primary_dark"],
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padding=8
        )
        self.style.map("Treeview", background=[("selected", "#BFDBFE")], foreground=[("selected", c["text"])])

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def page(self, title, subtitle=""):
        self.clear()
        container = ttk.Frame(self.root, padding=24)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=title, style="Title.TLabel").pack(anchor="w", pady=(0, 3))
        if subtitle:
            ttk.Label(container, text=subtitle, style="Subtitle.TLabel").pack(anchor="w", pady=(0, 16))

        return container

    def card(self, parent, **pack_options):
        frame = ttk.Frame(parent, padding=18, style="Card.TFrame")
        if pack_options:
            frame.pack(**pack_options)
        return frame

    def normalize_date(self, date_text):
        date_text = date_text.strip().replace("/", "-")
        for fmt in ("%Y-%m-%d", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_text, fmt).strftime("%Y-%m-%d")
            except Exception:
                pass
        return None

    def get_available_dates(self, days=21):
        today = datetime.today()
        return [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

    def get_slots(self, shift):
        # More realistic appointment capacity: 8 half-hour slots per shift.
        # Morning: 09:00-12:30, Afternoon: 13:00-16:30, Night: 18:00-21:30
        shift_slots = {
            "morning": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30"],
            "afternoon": ["13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"],
            "night": ["18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30"]
        }
        return shift_slots.get(str(shift).lower(), shift_slots["night"])

    def get_day_name(self, date_value):
        return datetime.strptime(date_value, "%Y-%m-%d").strftime("%A")

    def status_color_tag(self, tree):
        tree.tag_configure("Scheduled", background="#DBEAFE", foreground="#1E3A8A")
        tree.tag_configure("Pending", background="#FEF3C7", foreground="#92400E")
        tree.tag_configure("Completed", background="#DCFCE7", foreground="#166534")
        tree.tag_configure("Cancelled", background="#FEE2E2", foreground="#991B1B")
        tree.tag_configure("Paid", background="#DCFCE7", foreground="#166534")
        tree.tag_configure("Unpaid", background="#FEE2E2", foreground="#991B1B")

    # ================= DATABASE HELPERS =================
    def is_doctor_working_on_date(self, doctor_id, date_value):
        day_name = self.get_day_name(date_value)
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT COUNT(*)
                FROM doctor_working_day
                WHERE doctor_id=%s AND day_name=%s
            """, (doctor_id, day_name))
            works_that_day = cur.fetchone()[0] > 0

            cur.execute("""
                SELECT COUNT(*)
                FROM doctor_day_off
                WHERE doctor_id=%s AND off_date=%s
            """, (doctor_id, date_value))
            is_off = cur.fetchone()[0] > 0

            return works_that_day and not is_off
        except Exception:
            # Keeps old database usable before running the upgrade SQL.
            return True
        finally:
            conn.close()

    def get_doctor_shift(self, doctor_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT shift FROM doctor WHERE essn=%s", (doctor_id,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    def get_available_slots(self, doctor_id, date_value, exclude_appointment_id=None):
        shift = self.get_doctor_shift(doctor_id)
        if not shift:
            return []

        if not self.is_doctor_working_on_date(doctor_id, date_value):
            return []

        slots = self.get_slots(shift)
        conn = get_connection()
        cur = conn.cursor()

        if exclude_appointment_id:
            cur.execute("""
                SELECT TIME_FORMAT(appointment_time, '%H:%i')
                FROM appointment
                WHERE doctor_id=%s
                  AND appointment_date=%s
                  AND appointment_id <> %s
                  AND status <> 'Cancelled'
            """, (doctor_id, date_value, exclude_appointment_id))
        else:
            cur.execute("""
                SELECT TIME_FORMAT(appointment_time, '%H:%i')
                FROM appointment
                WHERE doctor_id=%s
                  AND appointment_date=%s
                  AND status <> 'Cancelled'
            """, (doctor_id, date_value))

        booked = [r[0] for r in cur.fetchall()]
        conn.close()

        # If the selected date is today, do not show time slots that already passed.
        # Example: if it is 12:30 now, 09:00, 10:00, 11:30, and 12:00 should not appear.
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        available_slots = []

        for slot in slots:
            if slot in booked:
                continue

            if date_value == today:
                slot_datetime = datetime.strptime(f"{date_value} {slot}", "%Y-%m-%d %H:%M")
                if slot_datetime <= now:
                    continue

            available_slots.append(slot)

        return available_slots

    def get_doctors_with_availability(self, specialization, date_value):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT d.essn, s.name, d.shift, d.email
            FROM doctor d
            JOIN staff s ON d.essn = s.ssn
            WHERE d.specialization = %s
            ORDER BY s.name
        """, (specialization,))

        doctors = cur.fetchall()
        conn.close()

        available_doctors = []
        for doc_id, name, shift, email in doctors:
            free_slots = self.get_available_slots(doc_id, date_value)
            if not free_slots:
                continue

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*)
                FROM appointment
                WHERE doctor_id=%s
                  AND appointment_date=%s
                  AND status <> 'Cancelled'
            """, (doc_id, date_value))
            booked_today = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM appointment
                WHERE doctor_id=%s
                  AND status <> 'Cancelled'
            """, (doc_id,))
            total_load = cur.fetchone()[0]
            conn.close()

            available_doctors.append({
                "id": doc_id,
                "name": name,
                "shift": shift,
                "email": email,
                "free_slots": free_slots,
                "booked_today": booked_today,
                "total_load": total_load
            })

        available_doctors.sort(key=lambda d: (d["booked_today"], d["total_load"], d["name"]))
        return available_doctors

    def get_test_price(self, test_type):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT price FROM test_price WHERE test_type=%s", (test_type,))
            row = cur.fetchone()
            return float(row[0]) if row else 200.0
        except Exception:
            return 200.0
        finally:
            conn.close()

    def get_patient_charges(self, patient_id):
        """Return all billable charges for a patient before subtracting payments."""
        total = 0.0
        lines = []
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT a.appointment_id, d.specialization, a.appointment_date, TIME_FORMAT(a.appointment_time, '%H:%i')
            FROM appointment a
            JOIN doctor d ON a.doctor_id = d.essn
            WHERE a.patient_id=%s AND a.status <> 'Cancelled'
        """, (patient_id,))
        for appt_id, spec, date_value, time_value in cur.fetchall():
            cost = 300.0
            lines.append(("Appointment", f"Appointment #{appt_id} - {spec} on {date_value} at {time_value}", cost))
            total += cost

        try:
            cur.execute("""
                SELECT t.test_type, COALESCE(tp.price, 200)
                FROM test t
                JOIN appointment a ON t.appointment_id = a.appointment_id
                LEFT JOIN test_price tp ON t.test_type = tp.test_type
                WHERE a.patient_id=%s
            """, (patient_id,))
        except Exception:
            cur.execute("""
                SELECT t.test_type, 200
                FROM test t
                JOIN appointment a ON t.appointment_id = a.appointment_id
                WHERE a.patient_id=%s
            """, (patient_id,))

        for test_type, price in cur.fetchall():
            cost = float(price)
            lines.append(("Test", test_type, cost))
            total += cost

        cur.execute("""
            SELECT m.name, m.price, pr.amount
            FROM prescribed pr
            JOIN medication m ON pr.med_id = m.med_id
            WHERE pr.patient_id=%s
        """, (patient_id,))
        for med_name, price, amount in cur.fetchall():
            cost = float(price) * int(amount)
            lines.append(("Medication", f"{med_name} x{amount}", cost))
            total += cost

        conn.close()
        return lines, total

    def get_patient_paid_total(self, patient_id):
        """Total successful payments already recorded for this patient."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM payment
            WHERE patient_id=%s AND status='Paid'
        """, (patient_id,))
        paid = float(cur.fetchone()[0] or 0)
        conn.close()
        return paid

    def get_patient_bill(self, patient_id):
        """Return charge lines and current outstanding balance.
        This prevents the same patient from paying the same bill repeatedly.
        """
        lines, charges_total = self.get_patient_charges(patient_id)
        paid_total = self.get_patient_paid_total(patient_id)
        outstanding = max(charges_total - paid_total, 0.0)
        return lines, outstanding

    def build_receipt_text(self, patient_id, method="Not paid yet"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, phone_num FROM patient WHERE patient_id=%s", (patient_id,))
        patient = cur.fetchone()
        conn.close()

        if not patient:
            return None, 0.0

        lines, charges_total = self.get_patient_charges(patient_id)
        paid_total = self.get_patient_paid_total(patient_id)
        outstanding = max(charges_total - paid_total, 0.0)

        receipt = []
        receipt.append("=" * 66)
        receipt.append("                         HOSPITAL RECEIPT")
        receipt.append("=" * 66)
        receipt.append(f"Date: {datetime.today().strftime('%Y-%m-%d %H:%M')}")
        receipt.append(f"Patient ID: {patient_id}")
        receipt.append(f"Patient Name: {patient[0]}")
        receipt.append(f"Phone: {patient[1]}")
        receipt.append(f"Payment Method: {method}")
        receipt.append("-" * 66)

        if not lines:
            receipt.append("No billable items found.")
        else:
            for category, description, cost in lines:
                safe_desc = str(description)[:37]
                receipt.append(f"{category:<13} {safe_desc:<37} {cost:>9.2f} EGP")

        receipt.append("-" * 66)
        receipt.append(f"TOTAL CHARGES:      {charges_total:.2f} EGP")
        receipt.append(f"ALREADY PAID:       {paid_total:.2f} EGP")
        receipt.append(f"CURRENT BALANCE:    {outstanding:.2f} EGP")
        if outstanding <= 0:
            receipt.append("Status: No current bills to pay.")
        receipt.append("=" * 66)
        return "\n".join(receipt), outstanding

    # ================= PDF EXPORT HELPER =================
    def export_text_to_pdf(self, text_content, default_filename="hospital_receipt.pdf"):
        """Export invoice/receipt text to a simple PDF without requiring extra libraries."""
        if not text_content.strip():
            messagebox.showerror("Error", "Load an invoice/receipt first before exporting.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_filename,
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF"
        )
        if not file_path:
            return

        try:
            lines = text_content.splitlines()
            max_lines_per_page = 48
            pages = [lines[i:i + max_lines_per_page] for i in range(0, len(lines), max_lines_per_page)] or [[""]]

            objects = []

            def pdf_escape(value):
                return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

            def add_object(content):
                objects.append(content)
                return len(objects)

            font_obj = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
            page_ids = []
            content_ids = []

            for page_lines in pages:
                stream_lines = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]
                for line in page_lines:
                    stream_lines.append(f"({pdf_escape(line)}) Tj")
                    stream_lines.append("T*")
                stream_lines.append("ET")
                stream = "\n".join(stream_lines)
                content_id = add_object(f"<< /Length {len(stream.encode('utf-8'))} >>\nstream\n{stream}\nendstream")
                content_ids.append(content_id)
                page_id = add_object("")
                page_ids.append(page_id)

            pages_obj = add_object("")

            for index, page_id in enumerate(page_ids):
                objects[page_id - 1] = (
                    f"<< /Type /Page /Parent {pages_obj} 0 R /MediaBox [0 0 595 842] "
                    f"/Resources << /Font << /F1 {font_obj} 0 R >> >> "
                    f"/Contents {content_ids[index]} 0 R >>"
                )

            kids = " ".join(f"{pid} 0 R" for pid in page_ids)
            objects[pages_obj - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>"
            catalog_obj = add_object(f"<< /Type /Catalog /Pages {pages_obj} 0 R >>")

            pdf = bytearray()
            pdf.extend(b"%PDF-1.4\n")
            offsets = []
            for obj_num, obj_content in enumerate(objects, start=1):
                offsets.append(len(pdf))
                pdf.extend(f"{obj_num} 0 obj\n".encode("utf-8"))
                pdf.extend(obj_content.encode("utf-8"))
                pdf.extend(b"\nendobj\n")

            xref_offset = len(pdf)
            pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("utf-8"))
            pdf.extend(b"0000000000 65535 f \n")
            for offset in offsets:
                pdf.extend(f"{offset:010d} 00000 n \n".encode("utf-8"))
            pdf.extend(
                f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_obj} 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("utf-8")
            )

            Path(file_path).write_bytes(pdf)
            messagebox.showinfo("PDF Saved", f"PDF saved successfully:\n{file_path}")
        except Exception as e:
            messagebox.showerror("PDF Error", str(e))

    # ================= LOGIN =================
    def login_screen(self):
        self.clear()

        wrapper = ttk.Frame(self.root, padding=30)
        wrapper.pack(fill="both", expand=True)

        panel = ttk.Frame(wrapper, style="Card.TFrame")
        panel.place(relx=0.5, rely=0.5, anchor="center", width=430, height=430)

        ttk.Label(
            panel,
            text="Hospital Management",
            background=self.colors["card"],
            foreground=self.colors["primary_dark"],
            font=("Segoe UI", 23, "bold")
        ).pack(pady=(42, 5))

        ttk.Label(
            panel,
            text="Professional admin dashboard",
            background=self.colors["card"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(pady=(0, 24))

        form = ttk.Frame(panel, style="Card.TFrame")
        form.pack(padx=45, fill="x")

        ttk.Label(form, text="Username", style="Card.TLabel").pack(anchor="w")
        user = ttk.Entry(form)
        user.pack(fill="x", pady=(4, 14))

        ttk.Label(form, text="Password", style="Card.TLabel").pack(anchor="w")
        pwd = ttk.Entry(form, show="*")
        pwd.pack(fill="x", pady=(4, 20))

        def login():
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (user.get(), pwd.get()))

            if cur.fetchone():
                conn.close()
                self.show_main_menu()
            else:
                conn.close()
                messagebox.showerror("Error", "Invalid login")

        ttk.Button(form, text="Login", command=login).pack(fill="x")

    # ================= MAIN MENU =================
    def show_main_menu(self):
        self.clear()

        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True)

        sidebar = ttk.Frame(main, style="Sidebar.TFrame", padding=24, width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ttk.Label(sidebar, text="HMS", style="SidebarTitle.TLabel").pack(anchor="w", pady=(0, 6))
        ttk.Label(sidebar, text="Hospital Management\nSystem", style="SidebarSubtitle.TLabel").pack(anchor="w", pady=(0, 30))

        content = ttk.Frame(main, padding=(26, 24, 26, 18))
        content.pack(side="right", fill="both", expand=True)

        ttk.Label(content, text="Dashboard", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            content,
            text="Manage patients, doctors, appointments, rooms, payments, invoices, and AI queries.",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(0, 16))

        # Canvas makes the dashboard responsive and prevents buttons from being clipped.
        canvas = tk.Canvas(content, bg=self.colors["bg"], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        grid = tk.Frame(canvas, bg=self.colors["bg"])
        canvas_window = canvas.create_window((0, 0), window=grid, anchor="nw")

        def on_grid_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfigure(canvas_window, width=event.width)

        grid.bind("<Configure>", on_grid_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        buttons = [
            ("Patients", "Register, update, delete, and view patients", self.register_screen),
            ("Book Appointment", "Smart doctor suggestion and availability", self.appointment_screen),
            ("Appointments", "Cancel, reschedule, and track status", self.view_appointments),
            ("Doctor Panel", "Add tests and medications", self.doctor_panel),
            ("Doctor Schedule", "Working days and days off", self.doctor_schedule_screen),
            ("Medical History", "Patient diagnosis, treatment, notes", self.patient_history_screen),
            ("Room Admission", "Admit and discharge patients", self.room_screen),
            ("Payments", "Calculate bills with test prices", self.payment_screen),
            ("Invoices / Receipts", "Preview and print-style receipt", self.invoice_screen),
            ("AI Hospital Assistant", "Groq AI converts English/Arabic questions to SQL", self.ai_chatbot_screen),
            ("Search", "Find doctors or appointments", self.search_screen),
        ]

        for col in range(2):
            grid.columnconfigure(col, weight=1, uniform="dashboard")

        for index, (title, subtitle, command) in enumerate(buttons):
            row = index // 2
            col = index % 2
            grid.rowconfigure(row, weight=0)

            tile = tk.Frame(
                grid,
                bg=self.colors["card"],
                highlightthickness=1,
                highlightbackground="#E5E7EB",
                height=126
            )
            tile.grid(row=row, column=col, sticky="nsew", padx=10, pady=9)
            tile.grid_propagate(False)

            tk.Label(
                tile,
                text=title,
                bg=self.colors["card"],
                fg=self.colors["primary_dark"],
                font=("Segoe UI", 14, "bold")
            ).place(x=20, y=18)

            tk.Label(
                tile,
                text=subtitle,
                bg=self.colors["card"],
                fg=self.colors["muted"],
                font=("Segoe UI", 9),
                wraplength=420,
                justify="left"
            ).place(x=20, y=50)

            open_button = tk.Button(
                tile,
                text="Open",
                command=command,
                bg=self.colors["primary"],
                fg="white",
                activebackground=self.colors["primary_dark"],
                activeforeground="white",
                font=("Segoe UI", 10, "bold"),
                relief="flat",
                cursor="hand2",
                bd=0
            )
            open_button.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-18, width=120, height=34)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ================= PATIENT REGISTRATION =================
    def register_screen(self):
        main = self.page("Patient Registration", "Add, update, or delete registered patients.")

        content = ttk.Frame(main)
        content.pack(fill="both", expand=True)

        form = ttk.LabelFrame(content, text="Patient Data", padding=15)
        form.pack(side="left", fill="y", padx=(0, 12))

        selected_patient_id = {"id": None}
        entries = {}
        fields = ["Name", "DOB", "Blood", "Phone", "Gender", "Address"]
        blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        genders = ["female", "male"]

        for i, field in enumerate(fields):
            ttk.Label(form, text=field, style="Card.TLabel").grid(row=i, column=0, sticky="w", pady=6)
            if field == "Blood":
                entry = ttk.Combobox(form, values=blood_types, state="readonly", width=31)
            elif field == "Gender":
                entry = ttk.Combobox(form, values=genders, state="readonly", width=31)
            else:
                entry = ttk.Entry(form, width=34)
            entry.grid(row=i, column=1, pady=6, padx=6)
            entries[field] = entry

        table_frame = ttk.LabelFrame(content, text="Registered Patients", padding=10)
        table_frame.pack(side="right", fill="both", expand=True)

        tree = ttk.Treeview(table_frame, columns=("ID", "Name", "DOB", "Blood", "Phone", "Gender", "Address"), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        def set_field(field, value):
            widget = entries[field]
            if isinstance(widget, ttk.Combobox):
                widget.set(str(value) if value is not None else "")
            else:
                widget.delete(0, tk.END)
                widget.insert(0, str(value) if value is not None else "")

        def get_field(field):
            return entries[field].get().strip()

        def clear_form():
            selected_patient_id["id"] = None
            for widget in entries.values():
                if isinstance(widget, ttk.Combobox):
                    widget.set("")
                else:
                    widget.delete(0, tk.END)

        def load_patients():
            tree.delete(*tree.get_children())
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT patient_id, name, date_of_birth, blood_type, phone_num, gender, address
                FROM patient
                ORDER BY patient_id
            """)
            for row in cur.fetchall():
                tree.insert("", "end", values=row)
            conn.close()

        def on_select(event=None):
            selected = tree.selection()
            if not selected:
                return
            values = tree.item(selected[0])["values"]
            clear_form()
            selected_patient_id["id"] = values[0]
            for key, value in zip(fields, values[1:]):
                set_field(key, value)

        tree.bind("<<TreeviewSelect>>", on_select)

        def validate_patient_form():
            if not get_field("Name"):
                messagebox.showerror("Error", "Patient name is required")
                return None

            dob = self.normalize_date(get_field("DOB"))
            if not dob:
                messagebox.showerror("Error", "DOB must be like 2026/5/4 or 2026-05-04")
                return None

            if get_field("Blood") not in blood_types:
                messagebox.showerror("Error", "Choose a valid blood type")
                return None

            if get_field("Gender") not in genders:
                messagebox.showerror("Error", "Choose a valid gender")
                return None

            return dob

        def add_patient():
            dob = validate_patient_form()
            if not dob:
                return

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("SELECT COALESCE(MAX(patient_id), 200) + 1 FROM patient")
                new_id = cur.fetchone()[0]
                cur.execute("""
                    INSERT INTO patient(patient_id, name, date_of_birth, blood_type, phone_num, gender, address)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (
                    new_id,
                    get_field("Name"),
                    dob,
                    get_field("Blood"),
                    get_field("Phone"),
                    get_field("Gender"),
                    get_field("Address")
                ))
                conn.commit()
                messagebox.showinfo("Success", f"Patient added successfully. ID: {new_id}")
                clear_form()
                load_patients()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        def update_patient():
            if not selected_patient_id["id"]:
                messagebox.showerror("Error", "Select a patient first")
                return

            dob = validate_patient_form()
            if not dob:
                return

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("""
                    UPDATE patient
                    SET name=%s, date_of_birth=%s, blood_type=%s, phone_num=%s, gender=%s, address=%s
                    WHERE patient_id=%s
                """, (
                    get_field("Name"),
                    dob,
                    get_field("Blood"),
                    get_field("Phone"),
                    get_field("Gender"),
                    get_field("Address"),
                    selected_patient_id["id"]
                ))
                conn.commit()
                messagebox.showinfo("Success", "Patient updated successfully")
                clear_form()
                load_patients()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        def delete_patient():
            if not selected_patient_id["id"]:
                messagebox.showerror("Error", "Select a patient first")
                return
            if not messagebox.askyesno("Confirm Delete", "This will delete the patient and related records. Continue?"):
                return

            conn = get_connection()
            cur = conn.cursor()
            try:
                pid = selected_patient_id["id"]
                cur.execute("DELETE FROM patient_history WHERE patient_id=%s", (pid,))
                cur.execute("DELETE FROM test WHERE appointment_id IN (SELECT appointment_id FROM appointment WHERE patient_id=%s)", (pid,))
                cur.execute("DELETE FROM prescribed WHERE patient_id=%s", (pid,))
                cur.execute("DELETE FROM payment WHERE patient_id=%s", (pid,))
                cur.execute("DELETE FROM admission WHERE patient_id=%s", (pid,))
                cur.execute("DELETE FROM nurse_patient WHERE patient_id=%s", (pid,))
                cur.execute("DELETE FROM appointment WHERE patient_id=%s", (pid,))
                cur.execute("DELETE FROM patient WHERE patient_id=%s", (pid,))
                conn.commit()
                messagebox.showinfo("Deleted", "Patient deleted successfully")
                clear_form()
                load_patients()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        btn_frame = ttk.Frame(form, style="Card.TFrame")
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="Add", command=add_patient, width=12, style="Success.TButton").grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Update", command=update_patient, width=12).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Delete", command=delete_patient, width=12, style="Danger.TButton").grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="Clear", command=clear_form, width=12).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(form, text="Back", command=self.show_main_menu).grid(row=len(fields) + 1, column=0, columnspan=2, sticky="ew")

        load_patients()

    # ================= APPOINTMENT BOOKING =================
    def appointment_screen(self):
        main = self.page("Book Appointment", "The system suggests the least-loaded doctor, while still letting the patient choose any available doctor.")

        frame = ttk.Frame(main, padding=18, style="Card.TFrame")
        frame.pack(fill="both", expand=True)

        self.doc = None
        doctors_by_name = {}
        available_doctors = []

        left = ttk.Frame(frame, style="Card.TFrame")
        left.pack(side="left", fill="y", padx=(0, 18))

        right = ttk.Frame(frame, style="Card.TFrame")
        right.pack(side="right", fill="both", expand=True)

        ttk.Label(left, text="Patient ID", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        pid = ttk.Entry(left, width=32)
        pid.grid(row=0, column=1, pady=6)

        ttk.Label(left, text="Specialization", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT specialization FROM doctor ORDER BY specialization")
        specializations = [row[0] for row in cur.fetchall()]
        conn.close()
        spec_combo = ttk.Combobox(left, values=specializations, state="readonly", width=29)
        spec_combo.grid(row=1, column=1, pady=6)

        ttk.Label(left, text="Date", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        date_combo = ttk.Combobox(left, values=self.get_available_dates(30), state="readonly", width=29)
        date_combo.grid(row=2, column=1, pady=6)

        ttk.Label(left, text="Available Doctor", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=6)
        doctor_combo = ttk.Combobox(left, state="readonly", width=50)
        doctor_combo.grid(row=3, column=1, pady=6)

        ttk.Label(left, text="Available Time", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=6)
        time_combo = ttk.Combobox(left, state="readonly", width=29)
        time_combo.grid(row=4, column=1, pady=6)

        doc_label = ttk.Label(left, text="", style="Card.TLabel", foreground=self.colors["primary_dark"], font=("Segoe UI", 10, "bold"), wraplength=500)
        doc_label.grid(row=5, column=0, columnspan=2, pady=10, sticky="w")

        suggestion_label = ttk.Label(left, text="", style="Card.TLabel", foreground=self.colors["success"], font=("Segoe UI", 10, "bold"), wraplength=500)
        suggestion_label.grid(row=6, column=0, columnspan=2, pady=8, sticky="w")

        availability_label = ttk.Label(right, text="Available doctors will appear after choosing specialization and date.", style="Card.TLabel", foreground=self.colors["muted"])
        availability_label.pack(anchor="w", pady=(0, 6))

        available_tree = ttk.Treeview(right, columns=("Doctor", "Shift", "FreeSlots", "BookedToday", "TotalLoad"), show="headings", height=7)
        for col in available_tree["columns"]:
            available_tree.heading(col, text=col)
            available_tree.column(col, width=115)
        available_tree.column("Doctor", width=210)
        available_tree.pack(fill="x", pady=(0, 12))

        patient_tree = ttk.Treeview(right, columns=("ID", "Name"), show="headings", height=13)
        patient_tree.heading("ID", text="Patient ID")
        patient_tree.heading("Name", text="Name")
        patient_tree.column("ID", width=120)
        patient_tree.column("Name", width=260)
        patient_tree.pack(fill="both", expand=True)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT patient_id, name FROM patient ORDER BY patient_id")
        for row in cur.fetchall():
            patient_tree.insert("", "end", values=row)
        conn.close()

        def reset_doctor_fields():
            nonlocal doctors_by_name, available_doctors
            doctors_by_name = {}
            available_doctors = []
            doctor_combo.set("")
            doctor_combo["values"] = []
            time_combo.set("")
            time_combo["values"] = []
            doc_label.config(text="")
            suggestion_label.config(text="")
            available_tree.delete(*available_tree.get_children())
            self.doc = None

        def doctor_display_name(doctor, index=0):
            prefix = "⭐ Suggested - " if index == 0 else "Available - "
            return (
                f"{prefix}{doctor['name']} | {doctor['shift']} | "
                f"{len(doctor['free_slots'])} slots | load {doctor['booked_today']}/{doctor['total_load']}"
            )

        def select_doctor(event=None):
            selected = doctor_combo.get()
            if not selected or selected not in doctors_by_name:
                return
            self.doc = doctors_by_name[selected]
            time_combo["values"] = self.doc["free_slots"]
            time_combo.set(self.doc["free_slots"][0] if self.doc["free_slots"] else "")
            doc_label.config(
                text=(
                    f"Selected Doctor: {self.doc['name']} | Shift: {self.doc['shift']} | "
                    f"Email: {self.doc['email']} | Free slots: {', '.join(self.doc['free_slots'])}"
                )
            )

        def load_available_doctors(event=None):
            nonlocal doctors_by_name, available_doctors
            spec = spec_combo.get()
            date_value = date_combo.get()
            reset_doctor_fields()
            if not spec or not date_value:
                return

            available_doctors = self.get_doctors_with_availability(spec, date_value)
            if not available_doctors:
                messagebox.showwarning("No Availability", "No doctors are working with free slots for this specialization on this date.")
                return

            display_values = []
            for index, doctor in enumerate(available_doctors):
                display = doctor_display_name(doctor, index)
                display_values.append(display)
                doctors_by_name[display] = doctor
                available_tree.insert(
                    "",
                    "end",
                    values=(doctor["name"], doctor["shift"], len(doctor["free_slots"]), doctor["booked_today"], doctor["total_load"])
                )

            doctor_combo["values"] = display_values
            doctor_combo.set(display_values[0])
            select_doctor()

            suggested = available_doctors[0]
            suggestion_label.config(
                text=(
                    f"Suggested: {suggested['name']} because they have the lowest load "
                    f"({suggested['booked_today']} booked on this date, {suggested['total_load']} total). "
                    f"You can still choose another available doctor from the dropdown."
                )
            )
            availability_label.config(text=f"Available doctors for {spec} on {date_value}: {len(available_doctors)}")

        def on_available_tree_select(event=None):
            selected = available_tree.selection()
            if not selected:
                return
            index = available_tree.index(selected[0])
            values = list(doctor_combo["values"])
            if 0 <= index < len(values):
                doctor_combo.set(values[index])
                select_doctor()

        spec_combo.bind("<<ComboboxSelected>>", load_available_doctors)
        date_combo.bind("<<ComboboxSelected>>", load_available_doctors)
        doctor_combo.bind("<<ComboboxSelected>>", select_doctor)
        available_tree.bind("<<TreeviewSelect>>", on_available_tree_select)

        def on_patient_select(event=None):
            selected = patient_tree.selection()
            if selected:
                values = patient_tree.item(selected[0])["values"]
                pid.delete(0, tk.END)
                pid.insert(0, values[0])

        patient_tree.bind("<<TreeviewSelect>>", on_patient_select)

        def book():
            if not pid.get().isdigit():
                messagebox.showerror("Error", "Invalid patient ID")
                return
            if not spec_combo.get() or not date_combo.get() or not self.doc or not time_combo.get():
                messagebox.showerror("Error", "Complete specialization, date, doctor, and time")
                return

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("SELECT COUNT(*) FROM patient WHERE patient_id=%s", (int(pid.get()),))
                if cur.fetchone()[0] == 0:
                    messagebox.showerror("Error", "Patient ID does not exist")
                    return

                cur.execute("""
                    SELECT COUNT(*)
                    FROM appointment
                    WHERE doctor_id=%s AND appointment_date=%s AND appointment_time=%s AND status <> 'Cancelled'
                """, (self.doc["id"], date_combo.get(), time_combo.get()))

                if cur.fetchone()[0] > 0:
                    messagebox.showerror("Error", "This slot was just booked. Choose another time.")
                    load_available_doctors()
                    return

                cur.execute("""
                    INSERT INTO appointment(patient_id, doctor_id, appointment_date, appointment_time, status)
                    VALUES (%s,%s,%s,%s,'Scheduled')
                """, (int(pid.get()), self.doc["id"], date_combo.get(), time_combo.get()))
                conn.commit()
                messagebox.showinfo("Success", f"Appointment booked with Dr. {self.doc['name']} at {time_combo.get()}.")
                load_available_doctors()
            except Exception as e:
                if "Duplicate entry" in str(e):
                    messagebox.showerror(
                        "Slot Conflict",
                        "This slot is blocked by the database unique constraint. Run the SQL fix for cancelled slots, then try again."
                    )
                else:
                    messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        button_row = ttk.Frame(left, style="Card.TFrame")
        button_row.grid(row=7, column=0, columnspan=2, sticky="ew", pady=18)
        ttk.Button(button_row, text="Book Appointment", command=book, style="Success.TButton").pack(side="left", padx=5)
        ttk.Button(button_row, text="Back", command=self.show_main_menu).pack(side="left", padx=5)

    # ================= APPOINTMENTS / CANCEL / RESCHEDULE =================
    def view_appointments(self):
        main = self.page("Appointments", "View, cancel, reschedule, and color-track appointment statuses.")

        body = ttk.Frame(main)
        body.pack(fill="both", expand=True)

        table_frame = ttk.LabelFrame(body, text="Appointment List", padding=10)
        table_frame.pack(fill="both", expand=True, pady=(0, 12))

        columns = ("ID", "Patient", "Doctor", "DoctorID", "Spec", "Date", "Time", "Status")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=125)
        tree.column("DoctorID", width=80)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        self.status_color_tag(tree)

        control = ttk.LabelFrame(body, text="Cancel / Reschedule", padding=12)
        control.pack(fill="x")

        selected_appt = {"id": None, "doctor_id": None}

        ttk.Label(control, text="New Date", style="Card.TLabel").grid(row=0, column=0, padx=6, pady=5)
        new_date = ttk.Combobox(control, values=self.get_available_dates(30), state="readonly", width=18)
        new_date.grid(row=0, column=1, padx=6, pady=5)

        ttk.Label(control, text="New Time", style="Card.TLabel").grid(row=0, column=2, padx=6, pady=5)
        new_time = ttk.Combobox(control, state="readonly", width=18)
        new_time.grid(row=0, column=3, padx=6, pady=5)

        def load_appointments():
            tree.delete(*tree.get_children())
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT a.appointment_id, p.name, s.name, d.essn, d.specialization,
                       a.appointment_date, TIME_FORMAT(a.appointment_time, '%H:%i'), a.status
                FROM appointment a
                JOIN patient p ON a.patient_id = p.patient_id
                JOIN doctor d ON a.doctor_id = d.essn
                JOIN staff s ON d.essn = s.ssn
                ORDER BY a.appointment_date, a.appointment_time
            """)
            for row in cur.fetchall():
                tree.insert("", "end", values=row, tags=(row[-1],))
            conn.close()

        def on_select(event=None):
            selected = tree.selection()
            if not selected:
                return
            values = tree.item(selected[0])["values"]
            selected_appt["id"] = values[0]
            selected_appt["doctor_id"] = values[3]
            new_date.set(values[5])
            load_reschedule_times()

        tree.bind("<<TreeviewSelect>>", on_select)

        def load_reschedule_times(event=None):
            if not selected_appt["id"] or not new_date.get():
                return
            slots = self.get_available_slots(selected_appt["doctor_id"], new_date.get(), exclude_appointment_id=selected_appt["id"])
            new_time["values"] = slots
            new_time.set(slots[0] if slots else "")

        new_date.bind("<<ComboboxSelected>>", load_reschedule_times)

        def cancel_appointment():
            if not selected_appt["id"]:
                messagebox.showerror("Error", "Select an appointment first")
                return
            if not messagebox.askyesno("Confirm", "Cancel this appointment?"):
                return
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE appointment SET status='Cancelled' WHERE appointment_id=%s", (selected_appt["id"],))
            conn.commit()
            conn.close()
            messagebox.showinfo("Done", "Appointment cancelled")
            load_appointments()

        def reschedule_appointment():
            if not selected_appt["id"]:
                messagebox.showerror("Error", "Select an appointment first")
                return
            if not new_date.get() or not new_time.get():
                messagebox.showerror("Error", "Choose a new date and time")
                return

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("""
                    UPDATE appointment
                    SET appointment_date=%s, appointment_time=%s, status='Scheduled'
                    WHERE appointment_id=%s
                """, (new_date.get(), new_time.get(), selected_appt["id"]))
                conn.commit()
                messagebox.showinfo("Done", "Appointment rescheduled")
                load_appointments()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        ttk.Button(control, text="Load Times", command=load_reschedule_times).grid(row=0, column=4, padx=6)
        ttk.Button(control, text="Reschedule", command=reschedule_appointment, style="Warning.TButton").grid(row=0, column=5, padx=6)
        ttk.Button(control, text="Cancel", command=cancel_appointment, style="Danger.TButton").grid(row=0, column=6, padx=6)
        ttk.Button(control, text="Back", command=self.show_main_menu).grid(row=0, column=7, padx=6)

        load_appointments()

    # ================= DOCTOR SCHEDULE =================
    def doctor_schedule_screen(self):
        main = self.page("Doctor Schedule", "Set working days and days off. Adding a day off cancels that doctor's active appointments on that date.")

        body = ttk.Frame(main)
        body.pack(fill="both", expand=True)

        left = ttk.LabelFrame(body, text="Working Days", padding=14)
        left.pack(side="left", fill="y", padx=(0, 12))

        right = ttk.LabelFrame(body, text="Days Off", padding=14)
        right.pack(side="right", fill="both", expand=True)

        # Load doctors once for the dropdown.
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT d.essn, s.name, d.specialization
                FROM doctor d
                JOIN staff s ON d.essn = s.ssn
                ORDER BY s.name
            """)
            doctors = cur.fetchall()
        except Exception as e:
            conn.close()
            messagebox.showerror("Database Error", "Could not load doctors.\n" + str(e))
            return
        conn.close()

        doctor_map = {f"{name} - {spec} ({doc_id})": doc_id for doc_id, name, spec in doctors}
        doctor_name_map = {doc_id: name for doc_id, name, spec in doctors}

        ttk.Label(left, text="Doctor", style="Card.TLabel").pack(anchor="w")
        doctor_combo = ttk.Combobox(left, values=list(doctor_map.keys()), state="readonly", width=42)
        doctor_combo.pack(pady=(4, 12), fill="x")

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_vars = {day: tk.BooleanVar(value=False) for day in days}

        for day in days:
            ttk.Checkbutton(left, text=day, variable=day_vars[day]).pack(anchor="w", pady=3)

        status_label = ttk.Label(left, text="", style="Card.TLabel", foreground=self.colors["muted"], wraplength=290)
        status_label.pack(anchor="w", pady=(4, 8))

        def selected_doctor_id():
            selected = doctor_combo.get()
            return doctor_map.get(selected)

        def load_working_days(event=None):
            for var in day_vars.values():
                var.set(False)

            doctor_id = selected_doctor_id()
            if not doctor_id:
                status_label.config(text="Select a doctor first.")
                return

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT day_name
                    FROM doctor_working_day
                    WHERE doctor_id=%s
                    ORDER BY FIELD(day_name, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')
                """, (doctor_id,))
                for (day_name,) in cur.fetchall():
                    if day_name in day_vars:
                        day_vars[day_name].set(True)
                status_label.config(text=f"Loaded schedule for Dr. {doctor_name_map.get(doctor_id, doctor_id)}.")
            except Exception as e:
                messagebox.showerror(
                    "Missing SQL Table",
                    "Could not load working days. Make sure doctor_working_day exists.\n" + str(e)
                )
            finally:
                conn.close()

            load_days_off()
            load_doctor_appointments()

        doctor_combo.bind("<<ComboboxSelected>>", load_working_days)

        def save_working_days():
            doctor_id = selected_doctor_id()
            if not doctor_id:
                messagebox.showerror("Error", "Select a doctor first")
                return

            chosen_days = [day for day, var in day_vars.items() if var.get()]
            if not chosen_days:
                if not messagebox.askyesno("No Working Days", "You selected no working days. Continue?"):
                    return

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM doctor_working_day WHERE doctor_id=%s", (doctor_id,))
                for day in chosen_days:
                    cur.execute("""
                        INSERT INTO doctor_working_day(doctor_id, day_name)
                        VALUES (%s,%s)
                    """, (doctor_id, day))
                conn.commit()
                status_label.config(text="Working days saved successfully.")
                messagebox.showinfo("Saved", "Working days saved")
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        ttk.Button(left, text="Save Working Days", command=save_working_days, style="Success.TButton").pack(fill="x", pady=12)
        ttk.Button(left, text="Back", command=self.show_main_menu).pack(fill="x")

        off_form = ttk.Frame(right, style="Card.TFrame")
        off_form.pack(fill="x", pady=(0, 10))

        ttk.Label(off_form, text="Off Date", style="Card.TLabel").grid(row=0, column=0, padx=5, pady=4, sticky="w")
        off_date = ttk.Entry(off_form, width=18)
        off_date.grid(row=0, column=1, padx=5, pady=4, sticky="w")
        off_date.insert(0, datetime.today().strftime("%Y-%m-%d"))

        ttk.Label(off_form, text="Reason", style="Card.TLabel").grid(row=0, column=2, padx=5, pady=4, sticky="w")
        reason_entry = ttk.Entry(off_form, width=32)
        reason_entry.grid(row=0, column=3, padx=5, pady=4, sticky="w")

        off_buttons = ttk.Frame(right, style="Card.TFrame")
        off_buttons.pack(fill="x", pady=(0, 10))

        off_tree = ttk.Treeview(right, columns=("ID", "Doctor", "Date", "Reason"), show="headings", height=7)
        for col in off_tree["columns"]:
            off_tree.heading(col, text=col)
            off_tree.column(col, width=140)
        off_tree.column("Reason", width=260)
        off_tree.pack(fill="x", pady=(0, 12))

        appt_label = ttk.Label(right, text="Appointments for selected doctor/day", style="Card.TLabel", foreground=self.colors["muted"])
        appt_label.pack(anchor="w", pady=(0, 4))

        appt_tree = ttk.Treeview(right, columns=("ID", "Patient", "Date", "Time", "Status"), show="headings", height=10)
        for col in appt_tree["columns"]:
            appt_tree.heading(col, text=col)
            appt_tree.column(col, width=120)
        appt_tree.column("Patient", width=210)
        appt_tree.pack(fill="both", expand=True)
        self.status_color_tag(appt_tree)

        def load_days_off():
            off_tree.delete(*off_tree.get_children())
            doctor_id = selected_doctor_id()
            if not doctor_id:
                return

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT off_id, doctor_id, off_date, reason
                    FROM doctor_day_off
                    WHERE doctor_id=%s
                    ORDER BY off_date
                """, (doctor_id,))
                for off_id, doc_id, date_value, reason in cur.fetchall():
                    off_tree.insert("", "end", values=(off_id, doctor_name_map.get(doc_id, doc_id), date_value, reason))
            except Exception as e:
                messagebox.showerror(
                    "Missing SQL Table",
                    "Could not load days off. Make sure doctor_day_off exists.\n" + str(e)
                )
            finally:
                conn.close()

        def load_doctor_appointments():
            appt_tree.delete(*appt_tree.get_children())
            doctor_id = selected_doctor_id()
            date_value = self.normalize_date(off_date.get())
            if not doctor_id or not date_value:
                return

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT a.appointment_id, p.name, a.appointment_date,
                           TIME_FORMAT(a.appointment_time, '%H:%i'), a.status
                    FROM appointment a
                    JOIN patient p ON a.patient_id = p.patient_id
                    WHERE a.doctor_id=%s
                      AND a.appointment_date=%s
                    ORDER BY a.appointment_time
                """, (doctor_id, date_value))
                rows = cur.fetchall()
                for row in rows:
                    appt_tree.insert("", "end", values=row, tags=(row[-1],))
                appt_label.config(text=f"Appointments on {date_value}: {len(rows)}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        def add_day_off():
            doctor_id = selected_doctor_id()
            if not doctor_id:
                messagebox.showerror("Error", "Select a doctor first")
                return

            date_value = self.normalize_date(off_date.get())
            if not date_value:
                messagebox.showerror("Error", "Date must be like 2026-05-04")
                return

            reason = reason_entry.get().strip() or "Day off"

            conn = get_connection()
            cur = conn.cursor()
            try:
                # IMPORTANT:
                # Some databases have a trigger that blocks appointment changes AFTER a doctor is marked off.
                # So we cancel the doctor's appointments FIRST, then save the day-off record.
                cur.execute("""
                    UPDATE appointment
                    SET status='Cancelled'
                    WHERE doctor_id=%s
                      AND appointment_date=%s
                      AND status <> 'Cancelled'
                """, (doctor_id, date_value))
                cancelled_count = cur.rowcount

                # Save or update the doctor's day off after appointments are already cancelled.
                # This avoids the trigger error: Invalid update: doctor is on day off.
                cur.execute("""
                    SELECT off_id
                    FROM doctor_day_off
                    WHERE doctor_id=%s AND off_date=%s
                    LIMIT 1
                """, (doctor_id, date_value))
                existing = cur.fetchone()

                if existing:
                    cur.execute("""
                        UPDATE doctor_day_off
                        SET reason=%s
                        WHERE off_id=%s
                    """, (reason, existing[0]))
                else:
                    cur.execute("""
                        INSERT INTO doctor_day_off(doctor_id, off_date, reason)
                        VALUES (%s,%s,%s)
                    """, (doctor_id, date_value, reason))

                conn.commit()
                reason_entry.delete(0, tk.END)
                load_days_off()
                load_doctor_appointments()
                status_label.config(text=f"Day off saved. Cancelled appointments: {cancelled_count}.")
                messagebox.showinfo(
                    "Saved",
                    f"Day off saved successfully.\n{cancelled_count} appointment(s) on {date_value} were cancelled."
                )
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        def delete_day_off():
            selected = off_tree.selection()
            if not selected:
                messagebox.showerror("Error", "Select a day off record")
                return

            off_id = off_tree.item(selected[0])["values"][0]
            if not messagebox.askyesno("Confirm", "Delete this day off record?\nCancelled appointments will stay cancelled unless you reschedule them manually."):
                return

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM doctor_day_off WHERE off_id=%s", (off_id,))
                conn.commit()
                load_days_off()
                load_doctor_appointments()
                messagebox.showinfo("Deleted", "Day off record deleted")
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        ttk.Button(off_buttons, text="Add Day Off + Cancel Appointments", command=add_day_off, style="Warning.TButton").pack(side="left", padx=5)
        ttk.Button(off_buttons, text="Delete Selected Day Off", command=delete_day_off, style="Danger.TButton").pack(side="left", padx=5)
        ttk.Button(off_buttons, text="Refresh", command=lambda: (load_days_off(), load_doctor_appointments())).pack(side="left", padx=5)

        off_date.bind("<FocusOut>", lambda event: load_doctor_appointments())
        off_date.bind("<Return>", lambda event: load_doctor_appointments())

        if doctors:
            doctor_combo.current(0)
            load_working_days()


    # ================= PATIENT HISTORY =================
    def patient_history_screen(self):
        main = self.page("Patient Medical History", "View every patient medical record regardless of which doctor handled it.")

        body = ttk.Frame(main)
        body.pack(fill="both", expand=True)

        patient_frame = ttk.LabelFrame(body, text="Patients", padding=10)
        patient_frame.pack(side="left", fill="y", padx=(0, 12))

        history_frame = ttk.LabelFrame(body, text="Complete Medical Record", padding=10)
        history_frame.pack(side="right", fill="both", expand=True)

        patient_tree = ttk.Treeview(patient_frame, columns=("ID", "Name"), show="headings", height=22)
        patient_tree.heading("ID", text="ID")
        patient_tree.heading("Name", text="Name")
        patient_tree.column("ID", width=80)
        patient_tree.column("Name", width=190)
        patient_tree.pack(fill="y")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT patient_id, name FROM patient ORDER BY patient_id")
        for row in cur.fetchall():
            patient_tree.insert("", "end", values=row)

        cur.execute("""
            SELECT d.essn, s.name
            FROM doctor d
            JOIN staff s ON d.essn = s.ssn
            ORDER BY s.name
        """)
        doctors = cur.fetchall()
        conn.close()
        doctor_map = {name: doc_id for doc_id, name in doctors}

        selected_patient = {"id": None}

        form = ttk.Frame(history_frame, style="Card.TFrame")
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Date", style="Card.TLabel").grid(row=0, column=0, padx=5, pady=4)
        record_date = ttk.Entry(form, width=16)
        record_date.grid(row=0, column=1, padx=5, pady=4)
        record_date.insert(0, datetime.today().strftime("%Y-%m-%d"))

        ttk.Label(form, text="Doctor", style="Card.TLabel").grid(row=0, column=2, padx=5, pady=4)
        doctor_combo = ttk.Combobox(form, values=list(doctor_map.keys()), state="readonly", width=24)
        doctor_combo.grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(form, text="Diagnosis", style="Card.TLabel").grid(row=1, column=0, padx=5, pady=4)
        diagnosis = ttk.Entry(form, width=34)
        diagnosis.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=4)

        ttk.Label(form, text="Treatment", style="Card.TLabel").grid(row=2, column=0, padx=5, pady=4)
        treatment = ttk.Entry(form, width=34)
        treatment.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=4)

        ttk.Label(form, text="Notes", style="Card.TLabel").grid(row=3, column=0, padx=5, pady=4)
        notes = ttk.Entry(form, width=34)
        notes.grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=4)

        columns = ("Type", "Date", "Doctor", "Details", "Treatment / Result", "Notes")
        history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        for col in columns:
            history_tree.heading(col, text=col)
            history_tree.column(col, width=145)
        history_tree.column("Details", width=210)
        history_tree.column("Treatment / Result", width=190)
        history_tree.column("Notes", width=240)
        history_tree.pack(fill="both", expand=True)

        def load_history():
            history_tree.delete(*history_tree.get_children())
            if not selected_patient["id"]:
                return

            pid = selected_patient["id"]
            conn = get_connection()
            cur = conn.cursor()

            try:
                cur.execute("""
                    SELECT h.record_date, COALESCE(s.name, 'N/A'), h.diagnosis, h.treatment, h.notes
                    FROM patient_history h
                    LEFT JOIN staff s ON h.doctor_id = s.ssn
                    WHERE h.patient_id=%s
                    ORDER BY h.record_date DESC, h.history_id DESC
                """, (pid,))
                for record_date_value, doctor_name, diag, treat, note in cur.fetchall():
                    history_tree.insert("", "end", values=("Manual History", record_date_value, doctor_name, diag, treat, note))
            except Exception:
                pass

            cur.execute("""
                SELECT a.appointment_date, COALESCE(TIME_FORMAT(a.appointment_time, '%H:%i'), 'N/A'),
                       s.name, d.specialization, a.status
                FROM appointment a
                JOIN doctor d ON a.doctor_id = d.essn
                JOIN staff s ON d.essn = s.ssn
                WHERE a.patient_id=%s
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """, (pid,))
            for date_value, time_value, doctor_name, spec, status in cur.fetchall():
                history_tree.insert("", "end", values=("Appointment", date_value, doctor_name, spec, status, f"Time: {time_value}"))

            cur.execute("""
                SELECT t.test_date, s.name, t.test_type, t.result
                FROM test t
                JOIN appointment a ON t.appointment_id = a.appointment_id
                JOIN doctor d ON a.doctor_id = d.essn
                JOIN staff s ON d.essn = s.ssn
                WHERE a.patient_id=%s
                ORDER BY t.test_date DESC, t.test_id DESC
            """, (pid,))
            for date_value, doctor_name, test_type, result in cur.fetchall():
                history_tree.insert("", "end", values=("Test", date_value, doctor_name, test_type, result, ""))

            cur.execute("""
                SELECT m.name, m.description, pr.amount
                FROM prescribed pr
                JOIN medication m ON pr.med_id = m.med_id
                WHERE pr.patient_id=%s
                ORDER BY m.name
            """, (pid,))
            for med_name, description, amount in cur.fetchall():
                history_tree.insert("", "end", values=("Medication", "N/A", "Any Doctor", med_name, f"Amount: {amount}", description))

            try:
                cur.execute("""
                    SELECT ad.admit_date, COALESCE(ad.discharged_date, 'Not discharged'), r.room_num, ad.notes
                    FROM admission ad
                    JOIN room r ON ad.room_id = r.room_id
                    WHERE ad.patient_id=%s
                    ORDER BY ad.admit_date DESC
                """, (pid,))
            except Exception:
                cur.execute("""
                    SELECT ad.admit_date, 'N/A', r.room_num, ad.notes
                    FROM admission ad
                    JOIN room r ON ad.room_id = r.room_id
                    WHERE ad.patient_id=%s
                    ORDER BY ad.admit_date DESC
                """, (pid,))

            for admit_date, discharge_date, room_num, note in cur.fetchall():
                history_tree.insert("", "end", values=("Admission", admit_date, "N/A", f"Room {room_num}", f"Discharged: {discharge_date}", note))

            conn.close()

        def on_patient_select(event=None):
            selected = patient_tree.selection()
            if not selected:
                return
            selected_patient["id"] = patient_tree.item(selected[0])["values"][0]
            load_history()

        patient_tree.bind("<<TreeviewSelect>>", on_patient_select)

        def add_history():
            if not selected_patient["id"]:
                messagebox.showerror("Error", "Select a patient first")
                return
            date_value = self.normalize_date(record_date.get())
            if not date_value:
                messagebox.showerror("Error", "Invalid date")
                return
            doctor_id = doctor_map.get(doctor_combo.get())
            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO patient_history(patient_id, doctor_id, record_date, diagnosis, treatment, notes)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (selected_patient["id"], doctor_id, date_value, diagnosis.get(), treatment.get(), notes.get()))
                conn.commit()
                diagnosis.delete(0, tk.END)
                treatment.delete(0, tk.END)
                notes.delete(0, tk.END)
                load_history()
                messagebox.showinfo("Saved", "History record added")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        button_row = ttk.Frame(history_frame, style="Card.TFrame")
        button_row.pack(fill="x", pady=10)
        ttk.Button(button_row, text="Add Manual History", command=add_history, style="Success.TButton").pack(side="left", padx=5)
        ttk.Button(button_row, text="Refresh", command=load_history).pack(side="left", padx=5)
        ttk.Button(button_row, text="Back", command=self.show_main_menu).pack(side="right", padx=5)

    # ================= DOCTOR PANEL =================
    def doctor_panel(self):
        main = self.page(
            "Doctor Panel",
            "Doctors can order tests and prescribe medications only for patients with Pending appointments."
        )

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT d.essn, s.name
            FROM doctor d
            JOIN staff s ON d.essn = s.ssn
            ORDER BY s.name
        """)
        doctors = cur.fetchall()
        conn.close()

        top = ttk.Frame(main)
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(top, text="Select Doctor:").pack(side="left")
        doctor_combo = ttk.Combobox(top, state="readonly", width=35, values=[d[1] for d in doctors])
        doctor_combo.pack(side="left", padx=10)

        info_label = ttk.Label(
            top,
            text="Only Pending appointments appear here.",
            foreground=self.colors["muted"]
        )
        info_label.pack(side="left", padx=10)

        table_frame = ttk.LabelFrame(main, text="Pending Appointments Only", padding=10)
        table_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(table_frame, columns=("ApptID", "PatientID", "Name", "Date", "Time", "Status"), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=140)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        self.status_color_tag(tree)

        selected_appt = {"id": None, "patient": None, "status": None}

        def get_selected_doctor_id():
            selected_name = doctor_combo.get()
            for doc_id, name in doctors:
                if name == selected_name:
                    return doc_id
            return None

        def clear_selection():
            selected_appt["id"] = None
            selected_appt["patient"] = None
            selected_appt["status"] = None

        def load_patients(event=None):
            clear_selection()
            tree.delete(*tree.get_children())
            doc_id = get_selected_doctor_id()
            if not doc_id:
                return

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT a.appointment_id, p.patient_id, p.name, a.appointment_date,
                       TIME_FORMAT(a.appointment_time, '%H:%i'), a.status
                FROM appointment a
                JOIN patient p ON a.patient_id = p.patient_id
                WHERE a.doctor_id = %s
                  AND a.status = 'Pending'
                ORDER BY a.appointment_date, a.appointment_time
            """, (doc_id,))
            rows = cur.fetchall()
            for row in rows:
                tree.insert("", "end", values=row, tags=(row[-1],))
            conn.close()

            if not rows:
                info_label.config(text="No Pending appointments for this doctor right now.")
            else:
                info_label.config(text=f"{len(rows)} Pending appointment(s) available for medical actions.")

        doctor_combo.bind("<<ComboboxSelected>>", load_patients)

        def on_select(event=None):
            selected = tree.selection()
            if selected:
                values = tree.item(selected[0])["values"]
                selected_appt["id"] = values[0]
                selected_appt["patient"] = values[1]
                selected_appt["status"] = values[5]

        tree.bind("<<TreeviewSelect>>", on_select)

        form_frame = ttk.LabelFrame(main, text="Order Test / Prescribe Medication", padding=14)
        form_frame.pack(fill="x", pady=12)

        ttk.Label(form_frame, text="Test Type", style="Card.TLabel").grid(row=0, column=0, padx=8, pady=6)
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT test_type, price
                FROM test_price
                ORDER BY test_type ASC
            """)
            tests = cur.fetchall()
        except Exception:
            tests = [("Blood Test", 200), ("Blood Sugar", 120), ("CT Scan", 1200), ("ECG", 400), ("MRI", 1500), ("Urine Test", 150), ("X-Ray", 350)]
        conn.close()
        test_labels = [f"{name} - {float(price):.0f} EGP" for name, price in tests]
        test_map = {f"{name} - {float(price):.0f} EGP": name for name, price in tests}
        test_combo = ttk.Combobox(form_frame, state="readonly", width=30, values=test_labels)
        test_combo.grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(form_frame, text="Medication", style="Card.TLabel").grid(row=0, column=2, padx=8, pady=6)
        med_combo = ttk.Combobox(form_frame, state="readonly", width=30)
        med_combo.grid(row=0, column=3, padx=8, pady=6)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT med_id, name
            FROM medication
            ORDER BY name ASC
        """)
        meds = cur.fetchall()
        conn.close()
        med_map = {m[1]: m[0] for m in meds}
        med_combo["values"] = list(med_map.keys())

        ttk.Label(form_frame, text="Amount", style="Card.TLabel").grid(row=1, column=0, padx=8, pady=6)
        amt = ttk.Entry(form_frame, width=15)
        amt.grid(row=1, column=1, padx=8, pady=6, sticky="w")

        def submit():
            if not selected_appt["id"]:
                messagebox.showerror("Error", "Select a Pending appointment first")
                return

            if not test_combo.get() and not med_combo.get():
                messagebox.showerror("Error", "Choose a test, a medication, or both")
                return

            conn = get_connection()
            cur = conn.cursor()
            try:
                # Re-check in the database, not only in the GUI, to prevent actions on old/completed/cancelled appointments.
                cur.execute("""
                    SELECT patient_id, status
                    FROM appointment
                    WHERE appointment_id=%s
                """, (selected_appt["id"],))
                appointment_row = cur.fetchone()

                if not appointment_row:
                    messagebox.showerror("Error", "Appointment no longer exists")
                    return

                patient_id, current_status = appointment_row
                if current_status != "Pending":
                    messagebox.showerror(
                        "Not Allowed",
                        "Tests and medications can only be added for Pending appointments."
                    )
                    load_patients()
                    return

                if test_combo.get():
                    test_type = test_map[test_combo.get()]
                    cur.execute("""
                        INSERT INTO test(test_type, test_date, result, appointment_id)
                        VALUES (%s, CURDATE(), 'Ordered', %s)
                    """, (test_type, selected_appt["id"]))

                if med_combo.get():
                    amount_value = int(amt.get()) if amt.get().isdigit() and int(amt.get()) > 0 else 1
                    med_id = med_map[med_combo.get()]
                    cur.execute("""
                        INSERT INTO prescribed(patient_id, med_id, amount)
                        VALUES (%s,%s,%s)
                        ON DUPLICATE KEY UPDATE amount = amount + VALUES(amount)
                    """, (patient_id, med_id, amount_value))

                conn.commit()
                messagebox.showinfo("Done", "Medical actions saved for the Pending appointment")
                test_combo.set("")
                med_combo.set("")
                amt.delete(0, tk.END)
                load_patients()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        ttk.Button(form_frame, text="Submit", command=submit, style="Success.TButton").grid(row=1, column=2, padx=8)
        ttk.Button(form_frame, text="Refresh Pending", command=load_patients).grid(row=1, column=3, padx=8, sticky="w")
        ttk.Button(form_frame, text="Back", command=self.show_main_menu).grid(row=1, column=4, padx=8, sticky="w")

    # ================= ROOM ADMISSION / DISCHARGE =================
    def room_screen(self):
        main = self.page("Room Admission", "Admit patients based on room capacity and discharge current admissions.")

        body = ttk.Frame(main)
        body.pack(fill="both", expand=True)

        available_frame = ttk.LabelFrame(body, text="Rooms With Free Beds", padding=12)
        available_frame.pack(side="left", fill="both", expand=True, padx=(0, 12))

        occupied_frame = ttk.LabelFrame(body, text="Current Admissions", padding=12)
        occupied_frame.pack(side="right", fill="both", expand=True)

        ttk.Label(available_frame, text="Patient ID", style="Card.TLabel").pack(anchor="w")
        pid = ttk.Entry(available_frame)
        pid.pack(fill="x", pady=(4, 10))

        room_columns = ("RoomID", "RoomNo", "Cost", "Capacity", "Occupied", "FreeBeds")
        room_tree = ttk.Treeview(available_frame, columns=room_columns, show="headings")
        for col in room_columns:
            room_tree.heading(col, text=col)
            room_tree.column(col, width=95)
        room_tree.pack(fill="both", expand=True)

        admission_columns = ("AdmissionID", "PatientID", "Patient", "RoomID", "RoomNo", "AdmitDate", "Notes")
        admission_tree = ttk.Treeview(occupied_frame, columns=admission_columns, show="headings")
        for col in admission_columns:
            admission_tree.heading(col, text=col)
            admission_tree.column(col, width=110)
        admission_tree.pack(fill="both", expand=True)

        def sync_room_status(cur, room_id):
            """Keep room.status realistic after admit/discharge, while still allowing partial capacity.
            This uses the same cursor/transaction as admit/discharge so it sees the latest change.
            """
            cur.execute("""
                SELECT r.capacity, COUNT(ad.admission_id)
                FROM room r
                LEFT JOIN admission ad
                    ON r.room_id = ad.room_id
                   AND ad.discharged_date IS NULL
                WHERE r.room_id=%s
                GROUP BY r.room_id, r.capacity
            """, (room_id,))

            row = cur.fetchone()
            if not row:
                return

            capacity, occupied = int(row[0]), int(row[1])

            if occupied >= capacity:
                new_status = "Occupied"
            else:
                # Empty rooms and partially filled rooms should stay Available
                # so another patient can still be admitted if there are free beds.
                new_status = "Available"

            cur.execute("UPDATE room SET status=%s WHERE room_id=%s", (new_status, room_id))

        def load_rooms():
            room_tree.delete(*room_tree.get_children())
            admission_tree.delete(*admission_tree.get_children())
            conn = get_connection()
            cur = conn.cursor()
            try:
                # Show every room that still has at least one free bed, even if one patient is already admitted.
                cur.execute("""
                    SELECT
                        r.room_id,
                        r.room_num,
                        r.room_cost,
                        r.capacity,
                        COUNT(ad.admission_id) AS occupied_beds,
                        r.capacity - COUNT(ad.admission_id) AS free_beds
                    FROM room r
                    LEFT JOIN admission ad
                        ON r.room_id = ad.room_id
                       AND ad.discharged_date IS NULL
                    WHERE r.status <> 'Under Maintenance'
                    GROUP BY r.room_id, r.room_num, r.room_cost, r.capacity
                    HAVING free_beds > 0
                    ORDER BY r.room_num
                """)
                for row in cur.fetchall():
                    room_tree.insert("", "end", values=row)

                cur.execute("""
                    SELECT ad.admission_id, p.patient_id, p.name, r.room_id, r.room_num, ad.admit_date, ad.notes
                    FROM admission ad
                    JOIN patient p ON ad.patient_id = p.patient_id
                    JOIN room r ON ad.room_id = r.room_id
                    WHERE ad.discharged_date IS NULL
                    ORDER BY ad.admit_date DESC, ad.admission_id DESC
                """)
                for row in cur.fetchall():
                    admission_tree.insert("", "end", values=row)
            except Exception as e:
                messagebox.showerror("Room Load Error", str(e))
            finally:
                conn.close()

        def admit():
            selected = room_tree.selection()
            if not selected:
                messagebox.showerror("Error", "Select a room first")
                return
            if not pid.get().isdigit():
                messagebox.showerror("Error", "Enter valid patient ID")
                return

            room_id = room_tree.item(selected[0])["values"][0]
            patient_id = int(pid.get())

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("SELECT COUNT(*) FROM patient WHERE patient_id=%s", (patient_id,))
                if cur.fetchone()[0] == 0:
                    messagebox.showerror("Error", "Patient ID does not exist")
                    return

                cur.execute("""
                    SELECT COUNT(*)
                    FROM admission
                    WHERE patient_id=%s
                      AND discharged_date IS NULL
                """, (patient_id,))
                if cur.fetchone()[0] > 0:
                    messagebox.showerror("Error", "This patient is already admitted and has not been discharged yet.")
                    return

                cur.execute("""
                    SELECT r.capacity, COUNT(ad.admission_id)
                    FROM room r
                    LEFT JOIN admission ad
                        ON r.room_id = ad.room_id
                       AND ad.discharged_date IS NULL
                    WHERE r.room_id=%s
                    GROUP BY r.capacity
                """, (room_id,))
                capacity_row = cur.fetchone()
                if not capacity_row:
                    messagebox.showerror("Error", "Room not found")
                    return

                capacity, occupied = int(capacity_row[0]), int(capacity_row[1])
                if occupied >= capacity:
                    messagebox.showerror("Room Full", "This room is already full. Choose another room.")
                    load_rooms()
                    return

                cur.execute("SELECT COALESCE(MAX(admission_id), 500) + 1 FROM admission")
                new_admission_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO admission(admission_id, admit_date, notes, patient_id, room_id)
                    VALUES (%s, CURDATE(), 'Admitted', %s, %s)
                """, (new_admission_id, patient_id, room_id))

                sync_room_status(cur, room_id)
                conn.commit()

                free_after = capacity - (occupied + 1)
                messagebox.showinfo("Done", f"Patient admitted. Free beds remaining in this room: {free_after}")
                pid.delete(0, tk.END)
                load_rooms()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        def discharge():
            selected = admission_tree.selection()
            if not selected:
                messagebox.showerror("Error", "Select an admission first")
                return

            values = admission_tree.item(selected[0])["values"]
            admission_id = values[0]
            room_id = values[3]

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute("""
                    UPDATE admission
                    SET discharged_date=CURDATE()
                    WHERE admission_id=%s
                """, (admission_id,))

                sync_room_status(cur, room_id)
                conn.commit()
                messagebox.showinfo("Done", "Patient discharged and room capacity updated")
                load_rooms()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=12)
        ttk.Button(buttons, text="Admit", command=admit, style="Success.TButton").pack(side="left", padx=5)
        ttk.Button(buttons, text="Discharge Selected", command=discharge, style="Warning.TButton").pack(side="left", padx=5)
        ttk.Button(buttons, text="Back", command=self.show_main_menu).pack(side="right", padx=5)

        load_rooms()

    # ================= PAYMENTS =================
    def payment_screen(self):
        main = self.page("Payment System", "Calculate only the current unpaid balance. Paid bills cannot be paid again.")

        frame = ttk.Frame(main, padding=18, style="Card.TFrame")
        frame.pack(fill="both", expand=True)

        top = ttk.Frame(frame, style="Card.TFrame")
        top.pack(fill="x")

        ttk.Label(top, text="Patient ID", style="Card.TLabel").pack(side="left", padx=(0, 6))
        pid = ttk.Entry(top, width=18)
        pid.pack(side="left", padx=6)

        ttk.Label(top, text="Payment Method", style="Card.TLabel").pack(side="left", padx=(20, 6))
        method = ttk.Combobox(top, state="readonly", values=["Cash", "Card", "Insurance", "Online"], width=18)
        method.pack(side="left", padx=6)

        receipt_text = tk.Text(frame, height=24, width=100, bg="#F8FAFC", fg=self.colors["text"], font=("Consolas", 10))
        receipt_text.pack(fill="both", expand=True, pady=12)

        total_label = ttk.Label(frame, text="Current Balance: 0.00 EGP", style="Card.TLabel", foreground=self.colors["primary_dark"], font=("Segoe UI", 14, "bold"))
        total_label.pack(anchor="e", pady=5)

        def load_details():
            if not pid.get().isdigit():
                messagebox.showerror("Error", "Enter valid patient ID")
                return
            receipt, outstanding = self.build_receipt_text(pid.get(), method.get() or "Not paid yet")
            if receipt is None:
                messagebox.showerror("Error", "Patient not found")
                return
            receipt_text.delete(1.0, tk.END)
            receipt_text.insert(tk.END, receipt)
            total_label.config(text=f"Current Balance: {outstanding:.2f} EGP")
            frame.total_amount = outstanding

            if outstanding <= 0:
                messagebox.showinfo("No Current Bills", "This patient has no current bills to pay. You can view the receipt/invoice only.")

        def pay():
            if not hasattr(frame, "total_amount"):
                messagebox.showerror("Error", "Load patient bill first")
                return
            if frame.total_amount <= 0:
                messagebox.showinfo("No Current Bills", "This patient has no current bills to pay.")
                return
            if not method.get():
                messagebox.showerror("Error", "Choose payment method")
                return
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO payment(patient_id, payment_date, status, amount, method)
                VALUES (%s, CURDATE(), 'Paid', %s, %s)
            """, (pid.get(), round(frame.total_amount, 2), method.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Done", "Payment recorded. This bill will not appear as payable again.")
            load_details()

        btns = ttk.Frame(frame, style="Card.TFrame")
        btns.pack(fill="x")
        ttk.Button(btns, text="Load Current Bill", command=load_details).pack(side="left", padx=5)
        ttk.Button(btns, text="Pay Current Balance", command=pay, style="Success.TButton").pack(side="left", padx=5)
        ttk.Button(btns, text="Back", command=self.show_main_menu).pack(side="right", padx=5)

    # ================= INVOICE SCREEN =================
    def invoice_screen(self):
        main = self.page("Invoices / Receipts", "Preview a print-style invoice and review previous payments.")

        body = ttk.Frame(main)
        body.pack(fill="both", expand=True)

        left = ttk.LabelFrame(body, text="Invoice Preview", padding=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        right = ttk.LabelFrame(body, text="Payment History", padding=12)
        right.pack(side="right", fill="both", expand=True)

        top = ttk.Frame(left, style="Card.TFrame")
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(top, text="Patient ID", style="Card.TLabel").pack(side="left")
        pid = ttk.Entry(top, width=18)
        pid.pack(side="left", padx=8)

        receipt_text = tk.Text(left, bg="#F8FAFC", fg=self.colors["text"], font=("Consolas", 10))
        receipt_text.pack(fill="both", expand=True)

        payment_tree = ttk.Treeview(right, columns=("PaymentID", "Date", "Status", "Amount", "Method"), show="headings")
        for col in payment_tree["columns"]:
            payment_tree.heading(col, text=col)
            payment_tree.column(col, width=110)
        payment_tree.pack(fill="both", expand=True)
        self.status_color_tag(payment_tree)

        def load_invoice():
            if not pid.get().isdigit():
                messagebox.showerror("Error", "Enter valid patient ID")
                return
            receipt, total = self.build_receipt_text(pid.get())
            if receipt is None:
                messagebox.showerror("Error", "Patient not found")
                return
            receipt_text.delete(1.0, tk.END)
            receipt_text.insert(tk.END, receipt)
            left.current_receipt = receipt
            left.current_patient_id = pid.get()

            payment_tree.delete(*payment_tree.get_children())
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT payment_id, payment_date, status, amount, method
                FROM payment
                WHERE patient_id=%s
                ORDER BY payment_date DESC, payment_id DESC
            """, (pid.get(),))
            for row in cur.fetchall():
                payment_tree.insert("", "end", values=row, tags=(row[2],))
            conn.close()

        def export_invoice_pdf():
            text = getattr(left, "current_receipt", receipt_text.get(1.0, tk.END))
            patient_id = getattr(left, "current_patient_id", pid.get().strip() or "patient")
            self.export_text_to_pdf(text, f"invoice_patient_{patient_id}.pdf")

        ttk.Button(top, text="Load Invoice", command=load_invoice).pack(side="left", padx=5)
        ttk.Button(top, text="Export PDF", command=export_invoice_pdf, style="Warning.TButton").pack(side="left", padx=5)
        ttk.Button(top, text="Back", command=self.show_main_menu).pack(side="right", padx=5)


    # ================= AI SQL CHATBOT =================
    # ================= GROQ AI SQL ASSISTANT =================
    def ai_read_groq_key(self):
        """Read the Groq API key from groq_key.txt placed beside this Python file."""
        possible_paths = [
            os.path.join(os.getcwd(), "groq_key.txt"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "groq_key.txt"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as file:
                    key = file.read().strip()
                if key:
                    return key
        return ""

    def ai_groq_chat(self, messages, temperature=0.05, max_tokens=900):
        """Send messages to Groq using free/common models."""
        api_key = self.ai_read_groq_key()
        if not api_key:
            return False, "Groq API key not found. Create groq_key.txt beside this Python file and paste your Groq key inside it."

        try:
            from groq import Groq
        except Exception:
            return False, "Groq library is not installed. Run: py -m pip install groq"

        client = Groq(api_key=api_key)
        models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "gemma2-9b-it",
            "qwen/qwen3-32b",
        ]

        last_error = ""
        for model_name in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return True, response.choices[0].message.content.strip()
            except Exception as e:
                last_error = str(e)

        return False, "Groq error: " + last_error

    def ai_get_mysql_schema(self):
        """Read the real MySQL schema so the AI does not invent names."""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                ORDER BY table_name, ordinal_position
            """)
            rows = cur.fetchall()
        finally:
            conn.close()

        tables = {}
        for table, column, dtype in rows:
            tables.setdefault(table, []).append(f"{column} {dtype}")

        return "\n".join([f"Table {table}: " + ", ".join(cols) for table, cols in tables.items()])

    def ai_get_database_value_hints(self):
        """Give the AI actual English values from important columns so Arabic questions map correctly."""
        hints = []
        queries = [
            ("Medication names", "SELECT DISTINCT name FROM medication ORDER BY name LIMIT 80"),
            ("Medication descriptions", "SELECT DISTINCT description FROM medication WHERE description IS NOT NULL ORDER BY description LIMIT 40"),
            ("Doctor specializations", "SELECT DISTINCT specialization FROM doctor ORDER BY specialization LIMIT 80"),
            ("Doctor shifts", "SELECT DISTINCT shift FROM doctor ORDER BY shift LIMIT 20"),
            ("Patient blood types", "SELECT DISTINCT blood_type FROM patient ORDER BY blood_type LIMIT 20"),
            ("Patient genders", "SELECT DISTINCT gender FROM patient ORDER BY gender LIMIT 20"),
            ("Appointment statuses", "SELECT DISTINCT status FROM appointment ORDER BY status LIMIT 20"),
            ("Room statuses", "SELECT DISTINCT status FROM room ORDER BY status LIMIT 20"),
            ("Payment statuses", "SELECT DISTINCT status FROM payment ORDER BY status LIMIT 20"),
            ("Payment methods", "SELECT DISTINCT method FROM payment ORDER BY method LIMIT 20"),
        ]

        conn = get_connection()
        cur = conn.cursor()
        try:
            for label, sql in queries:
                try:
                    cur.execute(sql)
                    values = [str(row[0]) for row in cur.fetchall() if row and row[0] is not None]
                    if values:
                        hints.append(f"{label}: " + ", ".join(values))
                except Exception:
                    pass
        finally:
            conn.close()
        return "\n".join(hints)

    def ai_expand_arabic_terms(self, user_question):
        """Add hidden English hints for common Arabic medical/admin words without changing the visible question."""
        q = user_question.lower()
        mapping = {
            "باراسيتامول": "Paracetamol", "الباراسيتامول": "Paracetamol", "براسيتامول": "Paracetamol",
            "اسبرين": "Aspirin", "أسبرين": "Aspirin", "الاسبرين": "Aspirin", "الأسبرين": "Aspirin",
            "انسولين": "Insulin", "أنسولين": "Insulin", "الانسولين": "Insulin", "الأنسولين": "Insulin",
            "مريض": "patient", "مرضى": "patients", "المريض": "patient", "المرضى": "patients",
            "دكتور": "doctor", "طبيب": "doctor", "دكاترة": "doctors", "الدكتور": "doctor",
            "موعد": "appointment", "حجز": "appointment", "مواعيد": "appointments", "الحجوزات": "appointments",
            "غرفة": "room", "اوضة": "room", "أوضة": "room", "غرف": "rooms",
            "دواء": "medication", "ادوية": "medications", "أدوية": "medications", "علاج": "medication",
            "تحاليل": "tests", "تحليل": "test", "اشعة": "X-Ray", "أشعة": "X-Ray",
            "مدفوع": "Paid", "اتدفع": "Paid", "غير مدفوع": "Unpaid", "مش مدفوع": "Unpaid",
            "ملغي": "Cancelled", "اتلغى": "Cancelled", "مجدول": "Scheduled", "مكتمل": "Completed",
            "النهاردة": datetime.today().strftime("%Y-%m-%d"),
            "اليوم": datetime.today().strftime("%Y-%m-%d"),
            "بكرة": (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "غدا": (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
        }
        hits = []
        for arabic, english in mapping.items():
            if arabic in q:
                hits.append(f"{arabic} = {english}")
        if not hits:
            return user_question
        return user_question + "\n\nHidden translation hints for SQL generation: " + "; ".join(sorted(set(hits)))

    def ai_is_safe_select(self, sql):
        """Allow only one safe SELECT statement."""
        if not sql:
            return False
        cleaned = sql.strip().strip("`").strip()
        lowered = cleaned.lower()
        if not lowered.startswith("select"):
            return False
        if ";" in cleaned:
            return False
        blocked_words = [
            " insert ", " update ", " delete ", " drop ", " alter ", " create ", " truncate ",
            " replace ", " grant ", " revoke ", " commit ", " rollback ", " set ", " call ",
        ]
        padded = " " + lowered + " "
        return not any(word in padded for word in blocked_words)

    def ai_json_from_text(self, text):
        """Extract JSON even if the model wraps it in markdown."""
        text = text.strip()
        text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
        return json.loads(text)

    def ai_value_to_text(self, value):
        if value is None:
            return "NULL"
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        try:
            if hasattr(value, "isoformat"):
                return value.isoformat()
        except Exception:
            pass
        return str(value)

    def ai_rows_preview(self, columns, rows, max_rows=30):
        preview_rows = []
        for row in rows[:max_rows]:
            preview_rows.append({str(col): self.ai_value_to_text(val) for col, val in zip(columns, row)})
        return json.dumps(preview_rows, ensure_ascii=False, indent=2)

    def ai_decide_answer_or_sql(self, user_question):
        schema = self.ai_get_mysql_schema()
        value_hints = self.ai_get_database_value_hints()
        today = datetime.today().strftime("%Y-%m-%d")

        system_prompt = f"""
You are an advanced AI assistant inside a Hospital Management System desktop app.

You can answer normal questions conversationally, or generate ONE safe MySQL SELECT query when the user asks about hospital database records.

CRITICAL SQL RULES:
- Use ONLY the real schema below.
- Never invent table names or column names.
- Generate exactly ONE MySQL SELECT query only.
- Never write INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, SET, CALL, or multiple statements.
- Do not include semicolons.
- Return JSON only. No markdown. No explanation outside JSON.

LANGUAGE AND VALUE TRANSLATION RULES:
- The database values are stored mostly in English.
- If the user asks in Arabic, translate Arabic medical/admin terms into the English values stored in the database BEFORE writing SQL.
- Never search for Arabic medication names unless the sample database values show Arabic values.
- Example: Arabic "باراسيتامول" or "الباراسيتامول" must be searched as "Paracetamol".
- Example: Arabic "انسولين" must be searched as "Insulin".
- Example: Arabic "اسبرين" must be searched as "Aspirin".
- For fuzzy names, use LOWER(column) LIKE LOWER('%EnglishValue%') when useful.

INTENT RULES:
- If the user asks about records, counts, statistics, patients, doctors, appointments, rooms, payments, invoices, medications, prescriptions, tests, or medical history: choose mode "sql".
- If the user asks a general explanation/presentation question not needing database rows: choose mode "answer".
- If the user asks "how many times was X used", use SUM(amount) from prescribed joined with medication when the schema supports it.

JSON FORMAT:
For normal answers:
{{"mode":"answer","answer":"your answer"}}

For database questions:
{{"mode":"sql","sql":"SELECT ...","answer":"short explanation of what you are checking"}}

Today is {today}.

REAL MYSQL SCHEMA:
{schema}

REAL DATABASE SAMPLE VALUES / VALUE HINTS:
{value_hints}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": self.ai_expand_arabic_terms(user_question)},
        ]
        ok, raw = self.ai_groq_chat(messages, temperature=0.02, max_tokens=900)
        if not ok:
            return {"mode": "answer", "answer": raw}

        try:
            data = self.ai_json_from_text(raw)
            if data.get("mode") not in ["answer", "sql"]:
                return {"mode": "answer", "answer": raw}
            if data.get("mode") == "sql" and not self.ai_is_safe_select(data.get("sql", "")):
                return {"mode": "answer", "answer": "I could not create a safe SELECT query for that request."}
            return data
        except Exception:
            return {"mode": "answer", "answer": raw}

    def ai_repair_failed_sql(self, user_question, failed_sql, error_message):
        """Ask Groq once to repair a SELECT query if MySQL rejects it."""
        schema = self.ai_get_mysql_schema()
        value_hints = self.ai_get_database_value_hints()
        messages = [
            {
                "role": "system",
                "content": f"""
Repair this MySQL SELECT query for the Hospital Management System.
Use only the schema and sample values below.
Return JSON only: {{"sql":"SELECT ..."}}
No markdown. No semicolon. Only one SELECT.
Translate Arabic terms to English database values when needed.

SCHEMA:
{schema}

SAMPLE VALUES:
{value_hints}
"""
            },
            {
                "role": "user",
                "content": f"User question: {self.ai_expand_arabic_terms(user_question)}\nFailed SQL: {failed_sql}\nMySQL error: {error_message}"
            }
        ]
        ok, raw = self.ai_groq_chat(messages, temperature=0.02, max_tokens=500)
        if not ok:
            return ""
        try:
            data = self.ai_json_from_text(raw)
            sql = data.get("sql", "").strip()
            return sql if self.ai_is_safe_select(sql) else ""
        except Exception:
            return ""

    def ai_summarize_database_result_with_groq(self, user_question, columns, rows):
        if not rows:
            return "I checked the database, but I did not find matching records."
        preview = self.ai_rows_preview(columns, rows, max_rows=25)
        messages = [
            {
                "role": "system",
                "content": "You are a friendly hospital system assistant. Summarize database results clearly and briefly. Reply in the same language as the user when possible. Do not mention SQL unless needed."
            },
            {
                "role": "user",
                "content": f"User question: {user_question}\nColumns: {columns}\nRows preview: {preview}\nTotal rows: {len(rows)}"
            }
        ]
        ok, answer = self.ai_groq_chat(messages, temperature=0.2, max_tokens=500)
        if ok:
            return answer
        return f"I found {len(rows)} matching record(s)."

    def ai_chatbot_screen(self):
        main = self.page("AI Hospital Assistant", "Groq converts your English/Arabic question into SQL, runs it, and shows the database results.")

        layout = ttk.Frame(main)
        layout.pack(fill="both", expand=True)

        left = ttk.LabelFrame(layout, text="AI Chat", padding=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = ttk.LabelFrame(layout, text="Database Results", padding=12)
        right.pack(side="right", fill="both", expand=True)

        chat_box = tk.Text(left, height=25, bg="#F8FAFC", fg=self.colors["text"], font=("Segoe UI", 10), wrap="word")
        chat_box.pack(fill="both", expand=True, pady=(0, 10))
        chat_box.insert(tk.END, "AI: Hi! I use Groq AI with your real MySQL schema.\n")
        chat_box.insert(tk.END, "AI: Ask in English or Arabic. Example: كم مرة تم استخدام الباراسيتامول؟ / how many times was paracetamol used?\n\n")
        chat_box.configure(state="disabled")

        input_row = ttk.Frame(left)
        input_row.pack(fill="x")
        question = ttk.Entry(input_row)
        question.pack(side="left", fill="x", expand=True, padx=(0, 8))

        examples = [
            "كم مرة تم استخدام الباراسيتامول؟",
            "how many times was paracetamol used?",
            "في حجز النهاردة؟",
            "مين أكتر دكتور مشغول؟",
            "show available rooms",
            "show patients with A+ blood type",
            "who paid more than 1000?",
            "show scheduled appointments today",
            "show medical history for patient 201",
            "explain what this hospital system does",
        ]
        example_combo = ttk.Combobox(left, values=examples, state="readonly")
        example_combo.pack(fill="x", pady=(8, 0))

        table_frame = ttk.Frame(right)
        table_frame.pack(fill="both", expand=True)
        result_tree = ttk.Treeview(table_frame, show="headings")
        result_tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, command=result_tree.yview)
        scrollbar.pack(side="right", fill="y")
        result_tree.configure(yscrollcommand=scrollbar.set)

        sql_frame = ttk.LabelFrame(right, text="Generated SQL Statement", padding=10)
        sql_frame.pack(fill="x", pady=(10, 0))

        sql_box = tk.Text(
            sql_frame,
            height=5,
            bg="#0F172A",
            fg="#22C55E",
            insertbackground="#22C55E",
            font=("Consolas", 10),
            wrap="word"
        )
        sql_box.pack(fill="x")
        sql_box.insert(tk.END, "No SQL generated yet.")
        sql_box.configure(state="disabled")

        status_label = ttk.Label(right, text="AI mode: ready", style="Card.TLabel", foreground=self.colors["muted"])
        status_label.pack(anchor="w", pady=(8, 0))

        def append_chat(sender, text):
            chat_box.configure(state="normal")
            chat_box.insert(tk.END, f"{sender}: {text}\n\n")
            chat_box.see(tk.END)
            chat_box.configure(state="disabled")

        def set_columns(columns):
            result_tree.delete(*result_tree.get_children())
            result_tree["columns"] = columns
            for col in columns:
                result_tree.heading(col, text=col)
                result_tree.column(col, width=max(110, min(280, len(str(col)) * 12)))

        def clear_results():
            result_tree.delete(*result_tree.get_children())
            result_tree["columns"] = []

        def set_sql_statement(sql_text):
            sql_box.configure(state="normal")
            sql_box.delete("1.0", tk.END)
            sql_box.insert(tk.END, sql_text if sql_text else "No SQL generated yet.")
            sql_box.configure(state="disabled")

        def execute_sql_and_show(sql):
            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute(sql)
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                set_columns(columns)
                self.status_color_tag(result_tree)
                for row in rows:
                    tag = ""
                    for value in row:
                        if str(value) in ["Scheduled", "Pending", "Completed", "Cancelled", "Paid", "Unpaid"]:
                            tag = str(value)
                            break
                    display_row = [self.ai_value_to_text(v) for v in row]
                    result_tree.insert("", "end", values=display_row, tags=(tag,) if tag else ())
                return rows, columns, None
            except Exception as err:
                return None, None, err
            finally:
                conn.close()

        def run_question():
            user_text = question.get().strip()
            if not user_text:
                messagebox.showerror("Error", "Type a question first")
                return

            question.delete(0, tk.END)
            append_chat("You", user_text)
            status_label.config(text="AI mode: thinking...")
            self.root.update_idletasks()

            decision = self.ai_decide_answer_or_sql(user_text)

            if decision.get("mode") == "answer":
                clear_results()
                set_sql_statement("No SQL generated. This was a normal AI answer, not a database query.")
                append_chat("AI", decision.get("answer", "I could not answer that."))
                status_label.config(text="AI mode: normal answer")
                return

            sql = decision.get("sql", "").strip()
            set_sql_statement(sql)
            if not self.ai_is_safe_select(sql):
                clear_results()
                set_sql_statement("Blocked unsafe or invalid SQL:\n" + (sql or "No SQL generated."))
                append_chat("AI", "I blocked that request because I only allow safe SELECT database questions.")
                status_label.config(text="AI mode: blocked unsafe SQL")
                return

            rows, columns, error = execute_sql_and_show(sql)

            if error is not None:
                repaired_sql = self.ai_repair_failed_sql(user_text, sql, str(error))
                if repaired_sql:
                    sql = repaired_sql
                    set_sql_statement("Original SQL failed, so Groq repaired it:\n\n" + repaired_sql)
                    rows, columns, error = execute_sql_and_show(repaired_sql)

            if error is not None:
                clear_results()
                append_chat("AI", "The AI tried to read the database, but the query failed. Error: " + str(error))
                status_label.config(text="AI mode: SQL error")
                return

            ai_summary = self.ai_summarize_database_result_with_groq(user_text, columns, rows)
            append_chat("AI", ai_summary)
            status_label.config(text=f"AI mode: database query | rows: {len(rows)}")

        def use_example(event=None):
            if example_combo.get():
                question.delete(0, tk.END)
                question.insert(0, example_combo.get())

        example_combo.bind("<<ComboboxSelected>>", use_example)
        question.bind("<Return>", lambda event: run_question())
        ttk.Button(input_row, text="Ask", command=run_question, style="Success.TButton").pack(side="left")
        ttk.Button(left, text="Back", command=self.show_main_menu).pack(fill="x", pady=(10, 0))

    # ================= SEARCH =================
    def search_screen(self):
        main = self.page("Search", "Search doctors by specialization or patients by appointment date.")

        search_frame = ttk.Frame(main)
        search_frame.pack(fill="x", pady=(0, 12))

        doctor_box = ttk.LabelFrame(search_frame, text="Doctor by Specialization", padding=12)
        doctor_box.pack(side="left", fill="x", expand=True, padx=(0, 8))

        date_box = ttk.LabelFrame(search_frame, text="Patients by Appointment Date", padding=12)
        date_box.pack(side="right", fill="x", expand=True, padx=(8, 0))

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT specialization FROM doctor ORDER BY specialization")
        specs = [row[0] for row in cur.fetchall()]
        conn.close()

        spec_combo = ttk.Combobox(doctor_box, values=specs, state="readonly", width=30)
        spec_combo.pack(side="left", padx=5)
        ttk.Button(doctor_box, text="Search Doctor", command=lambda: search_doctor()).pack(side="left", padx=5)

        date_entry = ttk.Entry(date_box, width=28)
        date_entry.pack(side="left", padx=5)
        date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        ttk.Button(date_box, text="Search Date", command=lambda: search_by_date()).pack(side="left", padx=5)

        tree = ttk.Treeview(main, show="headings")
        tree.pack(fill="both", expand=True)

        def set_columns(cols):
            tree.delete(*tree.get_children())
            tree["columns"] = cols
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=140)

        def search_doctor():
            if not spec_combo.get():
                messagebox.showerror("Error", "Choose specialization")
                return
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT d.essn, s.name, d.specialization, d.shift, d.email,
                       COUNT(a.appointment_id) AS total_appointments
                FROM doctor d
                JOIN staff s ON d.essn = s.ssn
                LEFT JOIN appointment a ON d.essn = a.doctor_id AND a.status <> 'Cancelled'
                WHERE d.specialization = %s
                GROUP BY d.essn, s.name, d.specialization, d.shift, d.email
                ORDER BY total_appointments ASC, s.name
            """, (spec_combo.get(),))
            rows = cur.fetchall()
            conn.close()
            set_columns(("Doctor ID", "Name", "Specialization", "Shift", "Email", "Load"))
            for row in rows:
                tree.insert("", "end", values=row)

        def search_by_date():
            date_value = self.normalize_date(date_entry.get())
            if not date_value:
                messagebox.showerror("Error", "Enter date like 2026/5/4 or 2026-05-04")
                return
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.patient_id, p.name, a.appointment_date, TIME_FORMAT(a.appointment_time, '%H:%i'),
                       s.name, d.specialization, a.status
                FROM appointment a
                JOIN patient p ON a.patient_id = p.patient_id
                JOIN doctor d ON a.doctor_id = d.essn
                JOIN staff s ON d.essn = s.ssn
                WHERE a.appointment_date = %s
                ORDER BY a.appointment_time
            """, (date_value,))
            rows = cur.fetchall()
            conn.close()
            set_columns(("Patient ID", "Patient", "Date", "Time", "Doctor", "Specialization", "Status"))
            self.status_color_tag(tree)
            for row in rows:
                tree.insert("", "end", values=row, tags=(row[-1],))

        ttk.Button(main, text="Back", command=self.show_main_menu).pack(pady=12)


# ================= RUN =================
root = tk.Tk()
app = HospitalApp(root)
root.mainloop()