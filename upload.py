import tkinter as tk
from tkinter import filedialog

# Global variable to store the file path
pdf_path = ""

def upload_pdf():
    global pdf_path
    # Open file dialog to select a PDF file
    file_path = filedialog.askopenfilename(
        title="Select a PDF File",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
    )
    if file_path:
        # Store the file path in the variable
        pdf_path = file_path
        # Update the label to display the file path
        status_label.config(text=f"Selected: {file_path}")
        print(f"File path stored: {pdf_path}")

# Create the main Tkinter window
root = tk.Tk()
root.title("Upload PDF")

# Create the "Upload PDF" button
upload_button = tk.Button(root, text="Upload PDF", command=upload_pdf)
upload_button.pack(pady=20)

# Label to show the selected file path
status_label = tk.Label(root, text="No file selected.")
status_label.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()

# At this point, `pdf_path` contains the selected file path
