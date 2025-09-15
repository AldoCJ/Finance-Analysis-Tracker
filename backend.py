from objects import *
from tkinter import filedialog
import pdfplumber 
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

def clean_label(label):
    """Clean the purchase label to extract only the company name."""

    # Remove non-alphanumeric characters (except spaces)
    cleaned_label = re.sub(r'[^a-zA-Z0-9\s]', '', label)

    # Remove location information (e.g., "Starbucks 123 Main St")
    cleaned_label = re.sub(r'\b\d{1,5}\b.*', '', cleaned_label)

    # Remove extra spaces
    cleaned_label = re.sub(r'\s+', ' ', cleaned_label).strip()

    return cleaned_label

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
        
    label = clean_label(label)    
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

def upload_file(user_data, ask_user_callback):
    print("Starting the upload process...")

    # Step 1: File selection
    file_path = filedialog.askopenfilename(
        title="Select a PDF File",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
    )
    if not file_path:
        print("No file selected.")
        return

    print(f"File selected: {file_path}")

    # Step 2: Check for duplicates
    if is_duplicate(file_path):
        print("File already uploaded. Duplicate detected.")
        return
    print("File is not a duplicate. Proceeding with processing...")

    try:
        # Step 3: Extract text from the PDF
        text = extract_text_from_pdf(file_path)

        purchases = []
        deposits = []
        year = 0

        # Step 4: Process extracted text
        for i, line in enumerate(text):
            if "Purchase" in line or "Zelle to" in line or "Money Transfer" in line or "Withdraw" in line:
                purchase = extract_purchase(line)
                purchases.append(purchase)
            elif "Fee period" in line:
                year = extract_year(line)
            else:
                deposit = extract_deposit(line)
                deposits.append(deposit)

        # Step 5: Add data to user_data
        user_data.add_data(purchases, deposits, year, ask_user_callback)

        # Step 6: Save data to database.json
        with open("database.json", "w") as file:
            json.dump(user_data.save_data(), file, indent=4)

        # Step 7: Copy the uploaded file to the storage directory
        filename = os.path.basename(file_path)
        shutil.copy(file_path, os.path.join("uploaded_files", filename))

        # Final confirmation
        if text:
            print("Data found and uploaded successfully.")
        else:
            print("No lines with dates found in the uploaded file.")

    except Exception as e:
        print(f"An error occurred during the upload process: {e}")


