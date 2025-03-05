import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Color scheme
COLORS = {
    "primary": "#3498db",      # Blue
    "secondary": "#2ecc71",    # Green
    "background": "#f5f5f5",   # Light grey
    "text": "#2c3e50",         # Dark blue/grey
    "accent": "#e74c3c",       # Red
    "button": "#ecf0f1",       # Light greyish
    "button_text": "#2c3e50",  # Dark blue/grey
    "frame": "#ffffff",        # White
}

# Function to check available balance
def check_available_balance(expense_amount=0):
    cursor.execute("SELECT SUM(amount) FROM Transactions WHERE type='Earning'")
    total_earnings = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM Transactions WHERE type='Expense'")
    total_expenses = cursor.fetchone()[0] or 0
    available_balance = total_earnings - total_expenses
    return available_balance >= expense_amount

# Function to add a transaction with sufficient funds check
def add_transaction():
    try:
        amount = float(amount_var.get())
        desc = desc_var.get().strip()
        trans_type = type_var.get()
        method = method_var.get()
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if not desc:
            raise ValueError("Description is required")
            
        # Check if there are sufficient funds for an expense
        if trans_type == "Expense" and not check_available_balance(amount):
            messagebox.showerror("Error", "Insufficient funds, please add funds")
            return
            
        cursor.execute("SELECT id FROM PaymentMethods WHERE method_name = %s", (method,))
        method_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO Transactions (type, amount, description, payment_method_id)
            VALUES (%s, %s, %s, %s)
        """, (trans_type, amount, desc, method_id))
        db.commit()
        amount_entry.delete(0, tk.END)
        desc_entry.delete(0, tk.END)
        show_transactions()
        messagebox.showinfo("Success", "Transaction added!")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", "An error occurred: " + str(e))

# Pie chart function to show detailed breakdown by description
def show_pie_chart():
    chart_window = tk.Toplevel(root)
    chart_window.title("Transaction Visual Representation")
    chart_window.geometry("900x600")
    chart_window.configure(bg=COLORS["background"])
    
    fig = plt.figure(figsize=(12, 10))
    
    # First subplot for earnings
    ax1 = fig.add_subplot(121)
    cursor.execute("SELECT description, amount FROM Transactions WHERE type='Earning'")
    earnings_data = cursor.fetchall()
    
    if earnings_data:
        labels = [row[0] for row in earnings_data]
        sizes = [float(row[1]) for row in earnings_data]
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, shadow=True, 
                colors=plt.cm.Blues([i/len(labels) for i in range(len(labels))]))
        ax1.axis('equal')
        ax1.set_title("Earnings Breakdown")
    else:
        ax1.text(0.5, 0.5, "No earnings data available", ha='center', va='center')
        ax1.axis('off')
    
    # Second subplot for expenses
    ax2 = fig.add_subplot(122)
    cursor.execute("SELECT description, amount FROM Transactions WHERE type='Expense'")
    expenses_data = cursor.fetchall()
    
    if expenses_data:
        labels = [row[0] for row in expenses_data]
        sizes = [float(row[1]) for row in expenses_data]
        ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, shadow=True,
                colors=plt.cm.Reds([i/len(labels) for i in range(len(labels))]))
        ax2.axis('equal')
        ax2.set_title("Expenses Breakdown")
    else:
        ax2.text(0.5, 0.5, "No expense data available", ha='center', va='center')
        ax2.axis('off')
    
    plt.tight_layout()
    
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

# Database connection setup
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="BudgetApp"        #schema name
    )
    print("Connection successful!")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit(1)

cursor = db.cursor()

# Tkinter Window
root = tk.Tk()
root.title("Budgeting App")
root.geometry("800x650")
root.configure(bg=COLORS["background"])

# Variables
amount_var = tk.StringVar()
desc_var = tk.StringVar()
type_var = tk.StringVar(value="Earning")
method_var = tk.StringVar()
selected_transaction_id = None
high_contrast = False       #By-default high contrast mode is off

# Toggle high-contrast mode
def high_contrast():
    global high_contrast
    high_contrast = not high_contrast
    if high_contrast:
        # High-contrast mode: Black background, white text
        hc_colors = {
            "background": "#000000",
            "text": "#FFFFFF",
            "frame": "#000000",
            "button": "#FFFFFF",
            "button_text": "#000000",
            "accent": "#FFFF00",  # Yellow for high contrast
        }
        
        root.configure(bg=hc_colors["background"])
        
        for frame in [entry_frame, method_frame, tree_frame, button_frame]:
            frame.configure(bg=hc_colors["background"], fg=hc_colors["text"])
            
        for widget in entry_frame.winfo_children() + method_frame.winfo_children() + button_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=hc_colors["background"], fg=hc_colors["text"])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=hc_colors["button"], fg=hc_colors["button_text"])
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=hc_colors["button"], fg=hc_colors["button_text"])
                
        style.configure("Treeview", background=hc_colors["background"], foreground=hc_colors["text"], fieldbackground=hc_colors["background"])
        style.map("Treeview", background=[("selected", hc_colors["accent"])], foreground=[("selected", hc_colors["button_text"])])
        style.configure("Treeview.Heading", background=hc_colors["button"], foreground=hc_colors["button_text"])
    else:
        # Default mode with our color scheme
        root.configure(bg=COLORS["background"])
        
        for frame in [entry_frame, method_frame, tree_frame]:
            frame.configure(bg=COLORS["frame"], fg=COLORS["text"])
        
        button_frame.configure(bg=COLORS["frame"])
            
        for widget in entry_frame.winfo_children() + method_frame.winfo_children() + button_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=COLORS["frame"], fg=COLORS["text"])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=COLORS["button"], fg=COLORS["button_text"])
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=COLORS["frame"], fg=COLORS["text"])
                
        style.configure("Treeview", background=COLORS["frame"], foreground=COLORS["text"], fieldbackground=COLORS["frame"])
        style.map("Treeview", background=[("selected", COLORS["primary"])], foreground=[("selected", "#ffffff")])
        style.configure("Treeview.Heading", background=COLORS["button"], foreground=COLORS["text"])

# Fetch payment methods for dropdown
def load_payment_methods():
    cursor.execute("SELECT method_name FROM PaymentMethods")
    methods = [row[0] for row in cursor.fetchall()]
    if not methods:
        methods = ["Cash"]
        cursor.execute("INSERT INTO PaymentMethods (method_name) VALUES ('Cash')")
        db.commit()
    return methods

# Add new payment method
def add_payment_method():
    new_method = method_entry.get().strip()
    if new_method:
        cursor.execute("INSERT INTO PaymentMethods (method_name) VALUES (%s)", (new_method,))
        db.commit()
        update_method_dropdown()
        method_entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"Payment method '{new_method}' added!")
    else:
        messagebox.showwarning("Input Error", "Please enter a payment method name.")

# Update payment method dropdown
def update_method_dropdown():
    methods = load_payment_methods()
    method_dropdown['values'] = methods
    if methods:
        method_var.set(methods[0])

# Update transaction
def update_transaction():
    global selected_transaction_id
    if not selected_transaction_id:
        messagebox.showwarning("Selection Error", "Please select a transaction to update.")
        return
    try:
        amount = float(amount_var.get())
        desc = desc_var.get().strip()
        trans_type = type_var.get()
        method = method_var.get()
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if not desc:
            raise ValueError("Description is required")
        cursor.execute("SELECT id FROM PaymentMethods WHERE method_name = %s", (method,))
        method_id = cursor.fetchone()[0]
        cursor.execute("""
            UPDATE Transactions 
            SET type = %s, amount = %s, description = %s, payment_method_id = %s
            WHERE id = %s
        """, (trans_type, amount, desc, method_id, selected_transaction_id))
        db.commit()
        amount_entry.delete(0, tk.END)
        desc_entry.delete(0, tk.END)
        show_transactions()
        selected_transaction_id = None
        messagebox.showinfo("Success", "Transaction updated!")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", "An error occurred: " + str(e))

# Delete transaction
def delete_transaction():
    global selected_transaction_id
    if not selected_transaction_id:
        messagebox.showwarning("Selection Error", "Please select a transaction to delete.")
        return
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?"):
        cursor.execute("DELETE FROM Transactions WHERE id = %s", (selected_transaction_id,))
        db.commit()
        show_transactions()
        selected_transaction_id = None
        messagebox.showinfo("Success", "Transaction deleted!")

# Display transactions and handle selection
def show_transactions():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("""
        SELECT t.id, t.type, t.amount, t.description, pm.method_name, t.transaction_date
        FROM Transactions t
        JOIN PaymentMethods pm ON t.payment_method_id = pm.id
        ORDER BY t.transaction_date DESC
    """)
    # Preconfigure tags
    tree.tag_configure('earning', background=COLORS["primary"])
    tree.tag_configure('expense', background=COLORS["accent"])
    
    for row in cursor.fetchall():
        # Color rows differently based on transaction type
        tag = row[1].lower()
        tree.insert("", tk.END, values=row, tags=(tag,))

def select_transaction(event):
    global selected_transaction_id
    selected_item = tree.selection()
    if selected_item:
        selected_transaction_id = tree.item(selected_item, "values")[0]
        amount_var.set(tree.item(selected_item, "values")[2])
        desc_var.set(tree.item(selected_item, "values")[3])
        type_var.set(tree.item(selected_item, "values")[1])
        method_var.set(tree.item(selected_item, "values")[4])

# Show pie chart
def show_pie_chart():
    cursor.execute("SELECT type, SUM(amount) FROM Transactions GROUP BY type")
    data = cursor.fetchall()
    if not data:
        messagebox.showinfo("No Data", "No transactions available to display.")
        return
    labels = [row[0] for row in data]
    sizes = [row[1] for row in data]
    colors = [COLORS["primary"], COLORS["accent"]]
    explode = (0.1, 0)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, shadow=True)
    ax.axis('equal')
    ax.set_title("Earnings vs Expenses")
    chart_window = tk.Toplevel(root)
    chart_window.title("Clik to view transactions Visual Representation")
    chart_window.geometry("700x600")
    chart_window.configure(bg=COLORS["background"])
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

# GUI Layout
style = ttk.Style()
style.theme_use('default')

# Main container frame
main_container = tk.Frame(root, bg=COLORS["background"], padx=15, pady=10)
main_container.pack(fill="both", expand=True)

left_panel = tk.Frame(main_container, bg=COLORS["background"])
left_panel.pack(side=tk.LEFT, fill="y", padx=5, pady=5)

right_panel = tk.Frame(main_container, bg=COLORS["background"])
right_panel.pack(side=tk.RIGHT, fill="both", expand=True, padx=5, pady=5)

# Transaction Entry Frame
entry_frame = tk.LabelFrame(left_panel, text="Add/Update Transaction", padx=10, pady=10, 
                          bg=COLORS["frame"], fg=COLORS["text"], font=("Arial", 10, "bold"))
entry_frame.pack(pady=10, padx=5, fill="x")

tk.Label(entry_frame, text="Amount:", bg=COLORS["frame"], fg=COLORS["text"]).grid(row=0, column=0, padx=5, pady=5, sticky="w")
amount_entry = tk.Entry(entry_frame, textvariable=amount_var, bg=COLORS["frame"], fg=COLORS["text"], width=20)
amount_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(entry_frame, text="Description:", bg=COLORS["frame"], fg=COLORS["text"]).grid(row=1, column=0, padx=5, pady=5, sticky="w")
desc_entry = tk.Entry(entry_frame, textvariable=desc_var, bg=COLORS["frame"], fg=COLORS["text"], width=20)
desc_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(entry_frame, text="Type:", bg=COLORS["frame"], fg=COLORS["text"]).grid(row=2, column=0, padx=5, pady=5, sticky="w")
type_dropdown = ttk.Combobox(entry_frame, textvariable=type_var, values=["Earning", "Expense"], state="readonly", width=17)
type_dropdown.grid(row=2, column=1, padx=5, pady=5)

tk.Label(entry_frame, text="Payment Method:", bg=COLORS["frame"], fg=COLORS["text"]).grid(row=3, column=0, padx=5, pady=5, sticky="w")
method_dropdown = ttk.Combobox(entry_frame, textvariable=method_var, state="readonly", width=17)
method_dropdown.grid(row=3, column=1, padx=5, pady=5)
update_method_dropdown()

button_style = {"bg": COLORS["button"], "fg": COLORS["button_text"], "padx": 10, "pady": 5,
                "font": ("Arial", 9), "relief": tk.RAISED, "width": 15}

tk.Button(entry_frame, text="Add Transaction", command=add_transaction, **button_style).grid(row=4, column=0, pady=10, padx=5)
tk.Button(entry_frame, text="Update Transaction", command=update_transaction, **button_style).grid(row=4, column=1, pady=10, padx=5)

# Payment Method Frame
method_frame = tk.LabelFrame(left_panel, text="Add Payment Method", padx=10, pady=10, 
                           bg=COLORS["frame"], fg=COLORS["text"], font=("Arial", 10, "bold"))
method_frame.pack(pady=10, padx=5, fill="x")

tk.Label(method_frame, text="New Method:", bg=COLORS["frame"], fg=COLORS["text"]).grid(row=0, column=0, padx=5, pady=5, sticky="w")
method_entry = tk.Entry(method_frame, bg=COLORS["frame"], fg=COLORS["text"], width=20)
method_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(method_frame, text="Add Method", command=add_payment_method, **button_style).grid(row=1, column=0, columnspan=2, pady=10)

# Action Buttons
action_frame = tk.Frame(left_panel, bg=COLORS["background"], pady=10)
action_frame.pack(fill="x", pady=5)

tk.Button(action_frame, text="Visual Representation", command=show_pie_chart, 
        bg=COLORS["primary"], fg="white", padx=10, pady=8, font=("Arial", 10, "bold")).pack(fill="x", pady=5)

tk.Button(action_frame, text="Click for High Contrast", command=high_contrast,
        bg=COLORS["secondary"], fg="white", padx=10, pady=8, font=("Arial", 10, "bold")).pack(fill="x", pady=5)

# Transaction Display
tree_frame = tk.LabelFrame(right_panel, text="Transactions", padx=10, pady=10, 
                         bg=COLORS["frame"], fg=COLORS["text"], font=("Arial", 10, "bold"))
tree_frame.pack(fill="both", expand=True, pady=5)

style.configure("Treeview", background=COLORS["frame"], foreground=COLORS["text"], fieldbackground=COLORS["frame"], rowheight=25)
style.map("Treeview", background=[("selected", COLORS["primary"])], foreground=[("selected", "#ffffff")])
style.configure("Treeview.Heading", background=COLORS["button"], foreground=COLORS["text"], font=("Arial", 9, "bold"))

# Create a frame for the treeview and scrollbar
tree_container = tk.Frame(tree_frame, bg=COLORS["frame"])
tree_container.pack(fill="both", expand=True)

# Create scrollbar first
scrollbar = ttk.Scrollbar(tree_container)
scrollbar.pack(side=tk.RIGHT, fill="y")

tree = ttk.Treeview(tree_container, columns=("ID", "Type", "Amount", "Description", "Method", "Date"), 
                  show="headings", yscrollcommand=scrollbar.set)
tree.heading("ID", text="ID")
tree.heading("Type", text="Type")
tree.heading("Amount", text="Amount")
tree.heading("Description", text="Description")
tree.heading("Method", text="Payment Method")
tree.heading("Date", text="Date")
tree.column("ID", width=40, anchor="center")
tree.column("Type", width=80, anchor="center")
tree.column("Amount", width=80, anchor="e")
tree.column("Description", width=150)
tree.column("Method", width=100, anchor="center")
tree.column("Date", width=120, anchor="center")
tree.pack(fill="both", expand=True)

# Configure scrollbar
scrollbar.config(command=tree.yview)

tree.bind("<<TreeviewSelect>>", select_transaction)

# Buttons Frame
button_frame = tk.Frame(tree_frame, bg=COLORS["frame"], pady=10)
button_frame.pack(fill="x")
tk.Button(button_frame, text="Delete Transaction", command=delete_transaction, 
        bg=COLORS["accent"], fg="white", padx=10, pady=5, font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)

show_transactions()

# Start the app
root.mainloop()

# Close database connection when done
db.close()