from objects import *
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pdfplumber # type: ignore
import re
import json
import os
import hashlib
import shutil


def generate_file_hash(file_path):
    hash_sha256 = hashlib.sha256()  
    with open(file_path, "rb") as file:
        while chunk := file.read(4096):  
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def is_duplicate(file_path, storage_dir="uploaded_files"):
    file_hash = generate_file_hash(file_path)
    
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)  
    for stored_file in os.listdir(storage_dir):
        stored_file_path = os.path.join(storage_dir, stored_file)
        if generate_file_hash(stored_file_path) == file_hash:
            return True 
    return False

def extract_text_from_pdf(pdf_path):
    lines_with_dates = []
    with pdfplumber.open(pdf_path) as pdf:
        date_pattern = r'^\d{1,2}/\d{1,2}'
        year_pattern = r'\d{2}/\d{2}/\d{4}'
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')
            lines_with_dates.extend([line for line in lines if re.match(date_pattern, line) or re.search(year_pattern, line)])
    return lines_with_dates

def extract_purchase(line):

    date_pattern = r'\d{1,2}/\d{1,2}'
    amount_pattern = r'\d+\.\d{2}'
    label_pattern = r'authorized on ' + date_pattern + r' (.*?) ' + amount_pattern

    date_match = re.match(date_pattern, line)
    amount_match = re.search(amount_pattern, line)
    label_match = re.search(label_pattern, line)

    if date_match:
        date = date_match.group(0)
    else:
        date = "00/00"
    if amount_match:
        amount = float(amount_match.group(0))
    else:
        amount = 0.0
    if label_match:
        label = label_match.group(1)
    else:
        label = "Zelle"
        
    purchase = Purchase(date, label, float(amount))
    return purchase

def extract_deposit(line):
    date_pattern = r'\d{1,2}/\d{1,2}'
    amount_pattern = r'\d+\.\d{2}'

    amount_match = re.search(amount_pattern, line)
    date_match = re.match(date_pattern, line)

    if amount_match:
        amount = float(amount_match.group(0))
    else:
        amount = 0.0

    if date_match:
        date = date_match.group(0)
    else:
        date = "00/00"

    deposit = Deposit(date, amount)
    return deposit

def extract_year(line):
    year_pattern = r'Fee period \d{2}/\d{2}/(\d{4})'
    match = re.search(year_pattern, line)
    if match:
        return int(match.group(1))
    return None
        
def data_exists():
    file_path = "database.json"
    
    if not os.path.exists(file_path):
        return False
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return bool(data)  
    except (json.JSONDecodeError, FileNotFoundError):
        return False

def upload_file():
    
    file_path = filedialog.askopenfilename(
        title="Select a PDF File",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
    )
    if file_path:
        
        if is_duplicate(file_path):
            result_label.config(text="File already exists!")
        else:
            text = extract_text_from_pdf(file_path)
            purchases = []
            deposits = []
            year = 0
            for i in text:
                if "Purchase" in i or "Zelle to" in i or "Money Transfer" in i or "Withdraw" in i:
                    purchases.append(extract_purchase(i))
                elif "Fee period" in i:
                    year = extract_year(i)
                else:
                    deposits.append(extract_deposit(i))

            user_data.add_data(purchases, deposits, year)

            with open("database.json", "w") as file:
                json.dump(user_data.save_data(), file, indent=4)

            filename = os.path.basename(file_path)
            shutil.copy(file_path, os.path.join("uploaded_files", filename))
            
            if text:
                result_label.config(text="Data found and uploaded")
                print("Data found and uploaded")
            else:
                result_label.config(text="No lines with dates found.")
                print("No lines with dates found.")     


def display_data(all_data):
    
    display_window = tk.Toplevel()
    display_window.title("Data Viewer")
    display_window.geometry("800x600")  

    # Create a treeview widget to display data hierarchically
    tree = ttk.Treeview(display_window)
    tree.pack(fill="both", expand=True)

    # Define the columns
    tree["columns"] = ("Year", "Total Spent", "Total Earned")
    tree.heading("#0", text="Category", anchor="w")  # Use this for hierarchical data
    tree.heading("Year", text="Year")
    tree.heading("Total Spent", text="Total Spent")
    tree.heading("Total Earned", text="Total Earned")

    # Set column widths
    tree.column("#0", width=150, anchor="w")
    tree.column("Year", width=100, anchor="center")
    tree.column("Total Spent", width=100, anchor="center")
    tree.column("Total Earned", width=100, anchor="center")

    # Populate the treeview with data from all_data
    for year_data in all_data.years:
        # Add a parent node for the year
        year_id = tree.insert(
            "", "end",
            text=f"Year: {year_data.year}",
            values=(year_data.year, year_data.total_spent, year_data.total_earned, year_data.average_spending,
                    year_data.average_earning)
        )

        # Add child nodes for each month
        for month_data in year_data.months:
            tree.insert(
                year_id, "end",
                text=f"{month_data.month}",
                values=("", month_data.total_spent, month_data.total_earned)
            )

    # Add a close button
    close_button = tk.Button(display_window, text="Close", command=display_window.destroy)
    close_button.pack(pady=10)

root = tk.Tk()
root.title("Data Loader")
root.geometry("600x400")

user_data = AllData()

if data_exists():
    print("Data exists in the file.")
    with open('database.json', 'r') as file:
        data = json.load(file)
    user_data.load_data(data)
else:
    print("The file doesn't exist or is empty.")

upload_button = tk.Button(root, text="Upload Data", command=upload_file)
upload_button.pack()

result_label = tk.Label(root, text="No data processed yet", justify=tk.LEFT)
result_label.pack()

display_data(user_data)

root.mainloop()
