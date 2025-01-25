import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Sample data
categories = {"Food": 250, "Gas": 150, "Entertainment": 100, "Rent": 1200, "Other": 200}

def show_pie_chart():
    # Create a figure for the pie chart
    figure, ax = plt.subplots()
    labels = categories.keys()
    values = categories.values()
    
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio for a perfect circle
    ax.set_title("Spending by Category")
    
    # Display the chart in the Tkinter window
    canvas = FigureCanvasTkAgg(figure, root)
    canvas.get_tk_widget().pack()
    canvas.draw()

# Create the GUI window
root = tk.Tk()
root.title("Spending Analysis")

# Add a button to generate the pie chart
button = ttk.Button(root, text="Show Pie Chart", command=show_pie_chart)
button.pack(pady=20)

# Run the application
root.mainloop()
