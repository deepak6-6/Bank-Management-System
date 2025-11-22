import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import re


# ---------------- DATABASE CONNECTION ----------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="deepak@12",  # change if needed
        database="bank_miniproject2"
    )


def run_query(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()


def fetch_query(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def validate_inputs(email, phone, dob):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("❌ Invalid Email Format")
    if not re.match(r"^\d{10}$", phone):
        raise ValueError("❌ Invalid Phone Number")
    try:
        d = datetime.strptime(dob, "%Y-%m-%d")
        if d > datetime.now():
            raise ValueError("❌ DOB cannot be a future date")
    except ValueError:
        raise ValueError("❌ DOB format should be YYYY-MM-DD")


# ---------------- MAIN DASHBOARD ----------------
def main_dashboard():
    root = tk.Tk()
    root.title("🏦 Banking Management System")
    root.geometry("1550x850")
    root.configure(bg="#e9f5f5")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    header = tk.Frame(root, bg="#005f73")
    header.pack(fill="x")
    tk.Label(header, text="🏦 BANK MANAGEMENT SYSTEM DASHBOARD",
             bg="#005f73", fg="white", font=("Segoe UI", 22, "bold"), pady=15).pack()

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=15, pady=15)

    # ====================================================================
    # 🏠 HOME DASHBOARD
    # ====================================================================
    home_tab = ttk.Frame(notebook)
    notebook.add(home_tab, text="🏠 Home Dashboard")

    tk.Label(home_tab, text="📊 BANK OVERVIEW", bg="#e9f5f5", fg="#005f73",
             font=("Segoe UI", 18, "bold")).pack(pady=20)

    frame_cards = tk.Frame(home_tab, bg="#e9f5f5")
    frame_cards.pack(pady=20)

    card_titles = ["Total Customers", "Total Accounts", "Total Balance", "Total Loans"]
    card_colors = ["#94d2bd", "#ee9b00", "#ca6702", "#0a9396"]
    values = []

    for i in range(4):
        f = tk.Frame(frame_cards, bg=card_colors[i], width=250, height=120)
        f.grid(row=0, column=i, padx=20)
        f.pack_propagate(False)
        tk.Label(f, text=card_titles[i], bg=card_colors[i], font=("Segoe UI", 11)).pack(pady=10)
        val = tk.Label(f, text="0", bg=card_colors[i], fg="white", font=("Segoe UI", 20, "bold"))
        val.pack()
        values.append(val)

    def refresh_dashboard():
        try:
            total_cust = fetch_query("SELECT COUNT(*) FROM Customer")[0][0]
            total_acc = fetch_query("SELECT COUNT(*) FROM Account")[0][0]
            total_bal = fetch_query("SELECT IFNULL(SUM(Balance),0) FROM Account")[0][0]
            total_loans = fetch_query("SELECT COUNT(*) FROM Loan")[0][0]
            values[0].config(text=total_cust)
            values[1].config(text=total_acc)
            values[2].config(text=f"₹{total_bal:,.2f}")
            values[3].config(text=total_loans)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(home_tab, text="🔁 Refresh Dashboard", command=refresh_dashboard).pack(pady=10)
    refresh_dashboard()

    # ====================================================================
    # 👥 CUSTOMERS TAB
    # ====================================================================
    tab_cust = ttk.Frame(notebook)
    notebook.add(tab_cust, text="👥 Customers")

    frame = tk.Frame(tab_cust, bg="#e9f5f5")
    frame.pack(pady=10)
    labels = ["Customer ID", "Name", "DOB (YYYY-MM-DD)", "Email", "Phone", "CompNo", "Branch_ID"]
    entries = {}
    for i, label in enumerate(labels):
        tk.Label(frame, text=label, bg="#e9f5f5").grid(row=i, column=0, pady=5, sticky="e")
        e = ttk.Entry(frame, width=30)
        e.grid(row=i, column=1, pady=5)
        entries[label] = e
    cus_id, name, dob, email, phone, comp, branch = entries.values()

    def show_customers():
        tree.delete(*tree.get_children())
        rows = fetch_query("SELECT CUS_ID, Name, Email, PhoneNo, Branch_ID FROM Customer")
        for r in rows:
            tree.insert("", "end", values=r)

    def add_customer():
        try:
            validate_inputs(email.get(), phone.get(), dob.get())
            run_query("INSERT INTO Customer VALUES (%s,%s,%s,%s,%s,%s,%s)",
                      (int(cus_id.get()), name.get(), dob.get(), email.get(),
                       phone.get(), comp.get(), int(branch.get())))
            messagebox.showinfo("Success", "Customer Added")
            show_customers(); refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_customer():
        try:
            run_query("DELETE FROM Customer WHERE CUS_ID=%s", (int(cus_id.get()),))
            show_customers(); refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_customer():
        try:
            validate_inputs(email.get(), phone.get(), dob.get())
            run_query("""UPDATE Customer 
                         SET Name=%s, DOB=%s, Email=%s, PhoneNo=%s, CompNo=%s, Branch_ID=%s 
                         WHERE CUS_ID=%s""",
                      (name.get(), dob.get(), email.get(), phone.get(),
                       comp.get(), int(branch.get()), int(cus_id.get())))
            messagebox.showinfo("Updated", "✅ Customer details updated successfully!")
            show_customers(); refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def check_age():
        try:
            cid = int(cus_id.get())
            age = fetch_query("SELECT GetCustomerAge(DOB) FROM Customer WHERE CUS_ID=%s", (cid,))
            if age and age[0][0] is not None:
                messagebox.showinfo("Age Info", f"Customer Age: {age[0][0]} years")
            else:
                messagebox.showwarning("Not Found", "Customer not found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_customers():
        show_customers()
        messagebox.showinfo("Refreshed", "🔄 Customer list updated!")

    btn_frame = tk.Frame(tab_cust, bg="#e9f5f5"); btn_frame.pack(pady=10)
    ttk.Button(btn_frame, text="Add", command=add_customer).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Delete", command=delete_customer).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Update", command=update_customer).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Check Age", command=check_age).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Refresh", command=refresh_customers).pack(side="left", padx=5)

    tree = ttk.Treeview(tab_cust, columns=("ID", "Name", "Email", "Phone", "Branch"), show="headings")
    for c in ("ID", "Name", "Email", "Phone", "Branch"):
        tree.heading(c, text=c)
        tree.column(c, width=200)
    tree.pack(fill="both", expand=True, padx=10, pady=10)
    show_customers()

    # ====================================================================
    # 💰 ACCOUNTS TAB
    # ====================================================================
    tab_acc = ttk.Frame(notebook)
    notebook.add(tab_acc, text="💰 Accounts")

    def show_accounts():
        tree_acc.delete(*tree_acc.get_children())
        for r in fetch_query("SELECT Account_ID, Acc_Type, Opened_Date, Status, Balance, CUS_ID FROM Account"):
            tree_acc.insert("", "end", values=r)

    def show_transactions(acc_id=None):  # for cross-tab updates
        tree_trans.delete(*tree_trans.get_children())
        if acc_id:
            rows = fetch_query("SELECT Trans_ID, Description, Date_of_Transaction, Type, Amount, Account_ID FROM Transactions WHERE Account_ID=%s", (acc_id,))
        else:
            rows = fetch_query("SELECT Trans_ID, Description, Date_of_Transaction, Type, Amount, Account_ID FROM Transactions")
        for r in rows:
            tree_trans.insert("", "end", values=r)

    def add_account():
        try:
            run_query("INSERT INTO Account (Account_ID, Acc_Type, Opened_Date, Status, Balance, CUS_ID) "
                      "VALUES (%s,%s,CURDATE(),'Active',%s,%s)",
                      (int(acc_id.get()), acc_type.get(), float(amount.get()), int(acc_cus.get())))
            messagebox.showinfo("Added", "✅ New Account Created")
            show_accounts(); refresh_dashboard(); show_transactions()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_account():
        try:
            run_query("DELETE FROM Account WHERE Account_ID=%s", (int(acc_id.get()),))
            messagebox.showinfo("Deleted", "❌ Account Deleted")
            show_accounts(); refresh_dashboard(); show_transactions()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def deposit():
        try:
            run_query("CALL DepositAmount(%s,%s)", (int(acc_id.get()), float(amount.get())))
            messagebox.showinfo("Deposited", "💰 Amount Deposited Successfully")
            show_accounts(); refresh_dashboard(); show_transactions()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def withdraw():
        try:
            run_query("CALL WithdrawAmount(%s,%s)", (int(acc_id.get()), float(amount.get())))
            messagebox.showinfo("Withdrawn", "💸 Amount Withdrawn Successfully")
            show_accounts(); refresh_dashboard(); show_transactions()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    acc_frame = tk.Frame(tab_acc, bg="#e9f5f5"); acc_frame.pack(pady=10)
    tk.Label(acc_frame, text="Account_ID").grid(row=0, column=0)
    acc_id = ttk.Entry(acc_frame, width=10); acc_id.grid(row=0, column=1)
    tk.Label(acc_frame, text="Type").grid(row=0, column=2)
    acc_type = ttk.Combobox(acc_frame, values=["Saving", "Current", "Fixed"], width=10); acc_type.grid(row=0, column=3)
    tk.Label(acc_frame, text="Amount").grid(row=0, column=4)
    amount = ttk.Entry(acc_frame, width=10); amount.grid(row=0, column=5)
    tk.Label(acc_frame, text="CUS_ID").grid(row=0, column=6)
    acc_cus = ttk.Entry(acc_frame, width=10); acc_cus.grid(row=0, column=7)

    ttk.Button(acc_frame, text="➕ Add Account", command=add_account).grid(row=0, column=8, padx=5)
    ttk.Button(acc_frame, text="❌ Delete Account", command=delete_account).grid(row=0, column=9, padx=5)
    ttk.Button(acc_frame, text="💰 Deposit", command=deposit).grid(row=0, column=10, padx=5)
    ttk.Button(acc_frame, text="💸 Withdraw", command=withdraw).grid(row=0, column=11, padx=5)

    tree_acc = ttk.Treeview(tab_acc, columns=("AccID", "Type", "Opened_Date", "Status", "Balance", "CUS_ID"),
                            show="headings")
    for c in ("AccID", "Type", "Opened_Date", "Status", "Balance", "CUS_ID"):
        tree_acc.heading(c, text=c)
        tree_acc.column(c, width=150)
    tree_acc.pack(fill="both", expand=True, padx=10, pady=10)
    show_accounts()
        # ====================================================================
    # 🏠 LOANS TAB WITH AUTO INTEREST RATE
    # ====================================================================
    tab_loan = ttk.Frame(notebook)
    notebook.add(tab_loan, text="🏠 Loans")

    form_loan = tk.Frame(tab_loan, bg="#e9f5f5"); form_loan.pack(pady=10)
    tk.Label(form_loan, text="Loan_ID").grid(row=0, column=0)
    l_id = ttk.Entry(form_loan, width=10); l_id.grid(row=0, column=1)
    tk.Label(form_loan, text="Loan_Type").grid(row=0, column=2)
    l_type = ttk.Combobox(form_loan, values=["Home", "Personal", "Car", "Education", "Gold"], width=15); l_type.grid(row=0, column=3)
    tk.Label(form_loan, text="Amount").grid(row=0, column=4)
    l_amt = ttk.Entry(form_loan, width=12); l_amt.grid(row=0, column=5)
    tk.Label(form_loan, text="Interest Rate (%)").grid(row=0, column=6)
    l_rate = ttk.Entry(form_loan, width=10, state="readonly"); l_rate.grid(row=0, column=7)
    tk.Label(form_loan, text="CUS_ID").grid(row=0, column=8)
    l_cus = ttk.Entry(form_loan, width=10); l_cus.grid(row=0, column=9)
    tk.Label(form_loan, text="Branch_ID").grid(row=0, column=10)
    l_branch = ttk.Entry(form_loan, width=10); l_branch.grid(row=0, column=11)

    # Auto-update interest rate based on selected loan type
    def update_interest_rate(event=None):
        try:
            loan_type = l_type.get()
            row = fetch_query("SELECT Default_Interest FROM LoanTypes WHERE Type_Name=%s", (loan_type,))
            if row:
                rate = row[0][0]
                l_rate.config(state="normal")
                l_rate.delete(0, tk.END)
                l_rate.insert(0, str(rate))
                l_rate.config(state="readonly")
            else:
                l_rate.config(state="normal")
                l_rate.delete(0, tk.END)
                l_rate.insert(0, "N/A")
                l_rate.config(state="readonly")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    l_type.bind("<<ComboboxSelected>>", update_interest_rate)

    def show_loans():
        tree_loan.delete(*tree_loan.get_children())
        for r in fetch_query("SELECT Loan_ID, Loan_Type, Loan_Amount, Interest_Rate, CUS_ID, Branch_ID, Status FROM Loan"):
            tree_loan.insert("", "end", values=r)

    def add_loan():
        try:
            if l_rate.get() == "" or l_rate.get() == "N/A":
                messagebox.showwarning("Warning", "Select a valid loan type first to get interest rate.")
                return
            run_query("""INSERT INTO Loan (Loan_ID, Interest_Rate, Status, Loan_Type, Loan_Amount, StartDate, CUS_ID, Branch_ID)
                         VALUES (%s,%s,'Approved',%s,%s,CURDATE(),%s,%s)""",
                      (int(l_id.get()), float(l_rate.get()), l_type.get(), float(l_amt.get()), int(l_cus.get()), int(l_branch.get())))
            messagebox.showinfo("Added", "Loan Added Successfully")
            show_loans(); refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_loan():
        try:
            run_query("UPDATE Loan SET Loan_Amount=%s, Loan_Type=%s, Interest_Rate=%s WHERE Loan_ID=%s",
                      (float(l_amt.get()), l_type.get(), float(l_rate.get()), int(l_id.get())))
            messagebox.showinfo("Updated", "Loan Updated")
            show_loans()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_loan():
        try:
            run_query("DELETE FROM Loan WHERE Loan_ID=%s", (int(l_id.get()),))
            messagebox.showinfo("Deleted", "Loan Deleted")
            show_loans(); refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn_loan = tk.Frame(tab_loan, bg="#e9f5f5"); btn_loan.pack(pady=6)
    ttk.Button(btn_loan, text="Add Loan", command=add_loan).pack(side="left", padx=5)
    ttk.Button(btn_loan, text="Update Loan", command=update_loan).pack(side="left", padx=5)
    ttk.Button(btn_loan, text="Delete Loan", command=delete_loan).pack(side="left", padx=5)
    ttk.Button(btn_loan, text="Refresh Loans", command=show_loans).pack(side="left", padx=5)

    tree_loan = ttk.Treeview(tab_loan, columns=("LoanID", "Type", "Amount", "Interest", "CUS_ID", "Branch_ID", "Status"), show="headings")
    for c in ("LoanID", "Type", "Amount", "Interest", "CUS_ID", "Branch_ID", "Status"):
        tree_loan.heading(c, text=c)
        tree_loan.column(c, width=140)
    tree_loan.pack(fill="both", expand=True, padx=10, pady=10)
    show_loans()


    # ====================================================================
    # 👨‍👩‍👧 BENEFICIARIES TAB WITH SEARCH + TRANSFER
    # ====================================================================
    tab_ben = ttk.Frame(notebook)
    notebook.add(tab_ben, text="👨‍👩‍👧 Beneficiaries")

    # Search area
    ben_search_frame = tk.Frame(tab_ben, bg="#e9f5f5")
    ben_search_frame.pack(fill="x", pady=6)
    tk.Label(ben_search_frame, text="Search by Customer ID:", bg="#e9f5f5").pack(side="left", padx=5)
    ben_search = ttk.Entry(ben_search_frame, width=12); ben_search.pack(side="left", padx=5)
    ttk.Button(ben_search_frame, text="Search", command=lambda: show_ben_filtered()).pack(side="left", padx=5)
    ttk.Button(ben_search_frame, text="Show All", command=lambda: show_ben()).pack(side="left", padx=5)

    # Beneficiary form
    ben_form = tk.Frame(tab_ben, bg="#e9f5f5"); ben_form.pack(pady=6)
    labels = ["Ben_ID", "Name", "Branch_AccNo", "Phone", "CUS_ID"]
    entries = [ttk.Entry(ben_form, width=20) for _ in labels]
    for i, lbl in enumerate(labels):
        tk.Label(ben_form, text=lbl, bg="#e9f5f5").grid(row=i, column=0, sticky="e", padx=5, pady=3)
        entries[i].grid(row=i, column=1, padx=5, pady=3)
    b_id, b_name, b_acc, b_phone, b_cus = entries

    def validate_beneficiary_phone(phone):
        if phone and not re.match(r"^\d{10}$", phone):
            raise ValueError("❌ Invalid phone number format (must be 10 digits)")

    def show_ben(cust_id=None):
        tree_ben.delete(*tree_ben.get_children())
        if cust_id:
            rows = fetch_query("SELECT ID, Name, Branch_AccNo, PhoneNo, CUS_ID FROM Beneficiary WHERE CUS_ID=%s", (cust_id,))
        else:
            rows = fetch_query("SELECT ID, Name, Branch_AccNo, PhoneNo, CUS_ID FROM Beneficiary")
        for r in rows:
            tree_ben.insert("", "end", values=r)

    def show_ben_filtered():
        txt = ben_search.get().strip()
        if not txt:
            show_ben()
            return
        try:
            cid = int(txt)
            show_ben(cid)
        except Exception:
            messagebox.showerror("Error", "Enter a valid Customer ID")

    def add_ben():
        try:
            validate_beneficiary_phone(b_phone.get())
            run_query("INSERT INTO Beneficiary (ID, Name, Branch_AccNo, PhoneNo, CUS_ID) VALUES (%s,%s,%s,%s,%s)",
                      (int(b_id.get()), b_name.get(), b_acc.get(), b_phone.get(), int(b_cus.get())))
            show_ben()
            for e in entries: e.delete(0, tk.END)
            messagebox.showinfo("Added", "✅ Beneficiary Added")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_ben():
        try:
            run_query("DELETE FROM Beneficiary WHERE ID=%s", (int(b_id.get()),))
            show_ben(); messagebox.showinfo("Deleted", "❌ Beneficiary Deleted")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn_ben = tk.Frame(ben_form, bg="#e9f5f5"); btn_ben.grid(row=0, column=2, rowspan=5, padx=10)
    ttk.Button(btn_ben, text="Add", command=add_ben).pack(pady=4)
    ttk.Button(btn_ben, text="Delete", command=delete_ben).pack(pady=4)
    ttk.Button(btn_ben, text="Refresh", command=show_ben).pack(pady=4)

    # Transfer section
    transfer_frame = tk.Frame(tab_ben, bg="#e9f5f5"); transfer_frame.pack(fill="x", pady=8)
    tk.Label(transfer_frame, text="From Account ID:", bg="#e9f5f5").grid(row=0, column=0, padx=5, pady=4)
    from_acc = ttk.Entry(transfer_frame, width=12); from_acc.grid(row=0, column=1, padx=5)
    tk.Label(transfer_frame, text="Beneficiary AccNo:", bg="#e9f5f5").grid(row=0, column=2, padx=5, pady=4)
    to_acc = ttk.Entry(transfer_frame, width=14); to_acc.grid(row=0, column=3, padx=5)
    tk.Label(transfer_frame, text="Amount:", bg="#e9f5f5").grid(row=0, column=4, padx=5, pady=4)
    trans_amt = ttk.Entry(transfer_frame, width=12); trans_amt.grid(row=0, column=5, padx=5)
    ttk.Button(transfer_frame, text="Transfer 💸", command=lambda: transfer_funds()).grid(row=0, column=6, padx=10)

    def transfer_funds():
        try:
            from_id = int(from_acc.get())
            to_acc_no = to_acc.get().strip()
            amount_val = float(trans_amt.get())

            if amount_val <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0")
                return

            ben_row = fetch_query("SELECT ID, Branch_AccNo, CUS_ID FROM Beneficiary WHERE Branch_AccNo=%s", (to_acc_no,))
            if not ben_row:
                messagebox.showerror("Error", "Beneficiary account not found!")
                return

            bal_row = fetch_query("SELECT Balance FROM Account WHERE Account_ID=%s", (from_id,))
            if not bal_row:
                messagebox.showerror("Error", "Sender account not found!")
                return

            if bal_row[0][0] < amount_val:
                messagebox.showerror("Error", "Insufficient Balance!")
                return

            # Debit sender
            run_query("UPDATE Account SET Balance=Balance-%s WHERE Account_ID=%s", (amount_val, from_id))

            # Try to credit beneficiary if Account exists (assumes Branch_AccNo contains digits)
            m = re.search(r"(\d+)", to_acc_no)
            if m:
                ben_acc_id = int(m.group(1))
                exist = fetch_query("SELECT COUNT(*) FROM Account WHERE Account_ID=%s", (ben_acc_id,))
                if exist and exist[0][0] > 0:
                    run_query("UPDATE Account SET Balance=Balance+%s WHERE Account_ID=%s", (amount_val, ben_acc_id))

            # Log transaction
            run_query("INSERT INTO Transactions (Description, Date_of_Transaction, Type, Amount, Account_ID) "
                      "VALUES (%s, CURDATE(), 'Transfer', %s, %s)",
                      (f'Transfer to {to_acc_no}', amount_val, from_id))

            messagebox.showinfo("Success", f"✅ Transferred ₹{amount_val:,.2f} to {to_acc_no}")
            show_ben(); refresh_dashboard(); show_accounts(); show_transactions()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Beneficiaries tree
    tree_ben = ttk.Treeview(tab_ben, columns=("ID", "Name", "AccNo", "Phone", "CusID"), show="headings")
    for c in ("ID", "Name", "AccNo", "Phone", "CusID"):
        tree_ben.heading(c, text=c)
        tree_ben.column(c, width=160)
    tree_ben.pack(fill="both", expand=True, padx=10, pady=8)
    show_ben()

    # ====================================================================
    # 🧾 TRANSACTIONS TAB
    # ====================================================================
    tab_trans = ttk.Frame(notebook)
    notebook.add(tab_trans, text="🧾 Transactions")

    trans_search_frame = tk.Frame(tab_trans, bg="#e9f5f5")
    trans_search_frame.pack(fill="x", pady=6)
    tk.Label(trans_search_frame, text="Search by Account ID:", bg="#e9f5f5").pack(side="left", padx=5)
    trans_search = ttk.Entry(trans_search_frame, width=12); trans_search.pack(side="left", padx=5)
    ttk.Button(trans_search_frame, text="Search", command=lambda: show_transactions_filtered()).pack(side="left", padx=5)
    ttk.Button(trans_search_frame, text="Refresh", command=lambda: show_transactions()).pack(side="left", padx=5)

    # Treeview for displaying transactions
    tree_trans = ttk.Treeview(tab_trans, columns=("TID", "Desc", "Date", "Type", "Amount", "AccID"), show="headings")
    for c in ("TID", "Desc", "Date", "Type", "Amount", "AccID"):
        tree_trans.heading(c, text=c)
        tree_trans.column(c, width=200)
    tree_trans.pack(fill="both", expand=True, padx=10, pady=10)

    # Function to show all or specific account transactions
    def show_transactions(acc_id=None):
        tree_trans.delete(*tree_trans.get_children())
        if acc_id:
            rows = fetch_query("""
                SELECT Transaction_ID, Description, Date_of_Transaction, Type, Amount, Account_ID
                FROM Transactions
                WHERE Account_ID=%s
                ORDER BY Transaction_ID DESC
            """, (acc_id,))
        else:
            rows = fetch_query("""
                SELECT Transaction_ID, Description, Date_of_Transaction, Type, Amount, Account_ID
                FROM Transactions
                ORDER BY Transaction_ID DESC
            """)
        for r in rows:
            tree_trans.insert("", "end", values=r)

    # Search filter by Account ID
    def show_transactions_filtered():
        txt = trans_search.get().strip()
        if not txt:
            show_transactions()
            return
        try:
            aid = int(txt)
            show_transactions(aid)
        except Exception:
            messagebox.showerror("Error", "Enter a valid Account ID")

    # Initialize table on tab load
    show_transactions()


    # ====================================================================
    # 📊 REPORTS TAB
    # ====================================================================
    tab_rep = ttk.Frame(notebook)
    notebook.add(tab_rep, text="📊 Reports")

    report_box = tk.Text(tab_rep, width=140, height=28, font=("Consolas", 10))
    report_box.pack(padx=10, pady=10)

    def show_branch_totals():
        rows = fetch_query("SELECT Branch_ID, Branch_Name, GetTotalBalance(Branch_ID) FROM Branch")
        report_box.delete("1.0", tk.END)
        report_box.insert(tk.END, "Branch_ID    Branch_Name           Total Balance\n")
        report_box.insert(tk.END, "-" * 60 + "\n")
        for r in rows:
            report_box.insert(tk.END, f"{r[0]:<10} {r[1]:<20} ₹{r[2]:,.2f}\n")

    def show_top_customers():
        rows = fetch_query("""
            SELECT c.CUS_ID, c.Name, IFNULL(SUM(a.Balance),0)
            FROM Customer c LEFT JOIN Account a ON c.CUS_ID=a.CUS_ID
            GROUP BY c.CUS_ID ORDER BY SUM(a.Balance) DESC LIMIT 5
        """)
        report_box.delete("1.0", tk.END)
        report_box.insert(tk.END, "Top 5 Customers\n" + "-" * 60 + "\n")
        for r in rows:
            report_box.insert(tk.END, f"{r[0]:<10}{r[1]:<20}₹{r[2]:,.2f}\n")

    def show_customer_loans():
        rows = fetch_query("SELECT * FROM CustomerLoanSummary")
        report_box.delete("1.0", tk.END)
        report_box.insert(tk.END, "Customer Loan Summary\n" + "-" * 60 + "\n")
        for r in rows:
            report_box.insert(tk.END, f"CUS_ID {r[0]:<5} {r[1]:<20} Total Loan: ₹{r[2]:,.2f}\n")

    def search_customer_report():
        try:
            cid_text = rep_search_box.get().strip()
            if not cid_text:
                messagebox.showwarning("Input", "Enter Customer ID to search")
                return
            cid = int(cid_text)
            loans = fetch_query("SELECT IFNULL(SUM(Loan_Amount),0) FROM Loan WHERE CUS_ID=%s", (cid,))
            bal = fetch_query("SELECT IFNULL(SUM(Balance),0) FROM Account WHERE CUS_ID=%s", (cid,))
            name = fetch_query("SELECT Name FROM Customer WHERE CUS_ID=%s", (cid,))
            report_box.delete("1.0", tk.END)
            if not name:
                report_box.insert(tk.END, "❌ Customer not found!")
                return
            report_box.insert(tk.END, f"Customer {cid} - {name[0][0]} Summary\n\n")
            report_box.insert(tk.END, f"Total Loan: ₹{loans[0][0]:,.2f}\n")
            report_box.insert(tk.END, f"Total Balance: ₹{bal[0][0]:,.2f}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    rpt_btn_frame = tk.Frame(tab_rep, bg="#e9f5f5"); rpt_btn_frame.pack(pady=6)
    ttk.Button(rpt_btn_frame, text="Show Branch Totals", command=show_branch_totals).pack(side="left", padx=6)
    ttk.Button(rpt_btn_frame, text="Top 5 Customers", command=show_top_customers).pack(side="left", padx=6)
    ttk.Button(rpt_btn_frame, text="Customer Loan Summary", command=show_customer_loans).pack(side="left", padx=6)

    rep_search_frame = tk.Frame(tab_rep, bg="#e9f5f5"); rep_search_frame.pack(pady=6)
    tk.Label(rep_search_frame, text="Enter Customer ID:").pack(side="left")
    rep_search_box = ttk.Entry(rep_search_frame, width=10); rep_search_box.pack(side="left", padx=5)
    ttk.Button(rep_search_frame, text="🔍 Search", command=search_customer_report).pack(side="left")

    # Final UI adjustments and start
    # Ensure initial population of tables in all tabs
    show_customers()
    show_accounts()
    show_loans()
    show_ben()
    show_transactions()
    show_branch_totals = lambda: None  # placeholder if called earlier (reports are button-driven)

    root.mainloop()


if __name__ == "__main__":
    main_dashboard()
