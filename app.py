from objects import *
import tkinter as tk
from tkinter import filedialog
import pdfplumber # type: ignore
import re
import json


def extract_text_from_pdf(pdf_path):
    lines_with_dates = []
    with pdfplumber.open(pdf_path) as pdf:
        date_pattern = r'^\d{1,2}/\d{1,2}'
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')
            lines_with_dates.extend([line for line in lines if re.match(date_pattern, line)])
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

def upload_and_extract():
    
    file_path = filedialog.askopenfilename(
        title="Select a PDF File",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
    )
    if file_path:
        
        text = extract_text_from_pdf(file_path)
        purchases = []
        deposits = []
        year_data = YearData(2024)

        for i in text:
            if "Purchase" in i or "Zelle to" in i or "Money Transfer" in i or "Withdraw" in i:
                purchases.append(extract_purchase(i))
            else:
                deposits.append(extract_deposit(i))

        year_data.add_purchases(purchases)
        year_data.add_deposits(deposits)

        with open("database.json", "w") as file:
            json.dump(year_data.to_dict(), file, indent=4)
        
        if text:
            results_label.config(text="Data found and uploaded")
            print("Data found and uploaded")
        else:
            results_label.config(text="No lines with dates found.")
            print("No lines with dates found.")

# Create the main Tkinter window
root = tk.Tk()
root.title("Upload and Extract PDF")
root.geometry("600x400")

# Create the "Upload PDF" button
upload_button = tk.Button(root, text="Upload PDF and Extract", command=upload_and_extract)
upload_button.pack(pady=20)

# Label to display extraction results
results_label = tk.Label(root, text="No file selected or processed yet.")
results_label.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()

