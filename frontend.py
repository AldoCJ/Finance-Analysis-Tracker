import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from backend import upload_file


class FinanceTrackerGUI:
    def __init__(self, root, user_data):
        self.root = root
        self.root.title("Finance Analysis Tracker")
        self.root.geometry("1000x700")
        self.user_data = user_data

        # Container for screens
        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)

        # Define frames
        self.dashboard_frame = tk.Frame(self.container)
        self.categorization_frame = tk.Frame(self.container)

        for frame in (self.dashboard_frame, self.categorization_frame):
            frame.grid(row=0, column=0, sticky="nsew")

        # Build screens
        self.build_dashboard(self.dashboard_frame)
        self.build_categorization(self.categorization_frame)

        self.show_dashboard()

    # ---------------- Dashboard ----------------
    def build_dashboard(self, parent):
        top_frame = tk.Frame(parent)
        top_frame.pack(side="top", fill="x", pady=10, padx=10)

        # Year dropdown
        self.year_var = tk.StringVar()
        tk.Label(top_frame, text="Select Year:").pack(side="left", padx=5)
        self.year_dropdown = ttk.Combobox(top_frame, textvariable=self.year_var, state="readonly")
        self.year_dropdown['values'] = self.user_data.get_years()
        if self.year_dropdown['values']:
            self.year_dropdown.current(0)
        self.year_dropdown.pack(side="left", padx=5)
        self.year_dropdown.bind("<<ComboboxSelected>>", self.on_year_change)

        # Month dropdown
        self.month_var = tk.StringVar()
        tk.Label(top_frame, text="Select Month:").pack(side="left", padx=5)
        self.month_dropdown = ttk.Combobox(top_frame, textvariable=self.month_var, state="readonly")
        self.month_dropdown['values'] = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        if self.month_dropdown['values']:
            self.month_dropdown.current(0)
        self.month_dropdown.pack(side="left", padx=5)
        self.month_dropdown.bind("<<ComboboxSelected>>", self.on_month_change)

        # Main content
        content_frame = tk.Frame(parent)
        content_frame.pack(fill="both", expand=True)

        # Year data (left panel)
        self.yearly_frame = tk.Frame(content_frame, width=400)
        self.yearly_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.build_yearly_data(self.yearly_frame)

        # Month data (right panel)
        self.monthly_frame = tk.Frame(content_frame)
        self.monthly_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.build_monthly_data(self.monthly_frame)

        # Upload button
        bottom_frame = tk.Frame(parent)
        bottom_frame.pack(side="bottom", fill="x", pady=10)
        self.upload_button = tk.Button(bottom_frame, text="Upload New Data", command=self.upload_data)
        self.upload_button.pack()

    def build_yearly_data(self, frame):
        self.year_stats_label = tk.Label(frame, text="Yearly Data", font=("Helvetica", 14, "bold"))
        self.year_stats_label.pack(pady=5)

        self.year_total_spent_label = tk.Label(frame, text="Total Spent: $0.00")
        self.year_total_spent_label.pack(pady=5)

        self.year_total_earned_label = tk.Label(frame, text="Total Earned: $0.00")
        self.year_total_earned_label.pack(pady=5)

        self.year_avg_spending_label = tk.Label(frame, text="Average Spending: $0.00")
        self.year_avg_spending_label.pack(pady=5)

        self.year_avg_earning_label = tk.Label(frame, text="Average Earning: $0.00")
        self.year_avg_earning_label.pack(pady=5)

        self.year_pie_canvas = self.create_pie_chart(frame, "Yearly Spending Breakdown")

    def build_monthly_data(self, frame):
        self.month_stats_label = tk.Label(frame, text="Monthly Data", font=("Helvetica", 14, "bold"))
        self.month_stats_label.pack(pady=5)

        self.month_total_spent_label = tk.Label(frame, text="Total Spent: $0.00")
        self.month_total_spent_label.pack(pady=5)

        self.month_total_earned_label = tk.Label(frame, text="Total Earned: $0.00")
        self.month_total_earned_label.pack(pady=5)

        self.month_pie_canvas = self.create_pie_chart(frame, "Monthly Spending Breakdown")

    def create_pie_chart(self, frame, title):
        tk.Label(frame, text=title, font=("Helvetica", 12, "bold")).pack(pady=5)
        fig, ax = plt.subplots(figsize=(4, 4))
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return {"fig": fig, "ax": ax, "canvas": canvas}

    def update_yearly_data(self, year):
        year_data = next((y for y in self.user_data.years if y.year == int(year)), None)
        if not year_data:
            return

        self.year_stats_label.config(text=f"Year: {year}")
        self.year_total_spent_label.config(text=f"Total Spent: ${year_data.total_spent:.2f}")
        self.year_total_earned_label.config(text=f"Total Earned: ${year_data.total_earned:.2f}")
        self.year_avg_spending_label.config(text=f"Average Spending: ${year_data.average_spending:.2f}")
        self.year_avg_earning_label.config(text=f"Average Earning: ${year_data.average_earning:.2f}")

        self.update_pie_chart(self.year_pie_canvas, year_data.categories)

    def update_monthly_data(self, year, month):
        year_data = next((y for y in self.user_data.years if y.year == int(year)), None)
        if not year_data:
            return

        month_index = self.month_dropdown['values'].index(month)
        month_data = year_data.months[month_index]

        self.month_stats_label.config(text=f"Month: {month}")
        self.month_total_spent_label.config(text=f"Total Spent: ${month_data.total_spent:.2f}")
        self.month_total_earned_label.config(text=f"Total Earned: ${month_data.total_earned:.2f}")

        self.update_pie_chart(self.month_pie_canvas, month_data.categories)

    def update_pie_chart(self, pie_canvas, categories):
        pie_canvas["ax"].clear()
        if not categories or all(value == 0 for value in categories.values()):  # Check if categories are empty or all zeros
            pie_canvas["ax"].text(0.5, 0.5, "No Data", fontsize=14, ha='center', va='center')
        else:
            filtered_categories = {k: v for k, v in categories.items() if v > 0}
            labels = filtered_categories.keys()
            values = filtered_categories.values()

            custom_colors = [
                "#2c0be9",  # Food
                "#c1f507",  # Transportation
                "#f3bd0b",  # Entertainment
                "#08d6aa",  # Shopping
                "#af301f",  # Bills
                "#0BB8E4FF"  # Other
            ]

            def autopct_func(pct):
                return f'{pct:.1f}%' if pct >= 5 else ''  # Only show percentages >= 5%

            pie_canvas["ax"].pie(
            values,
            labels=labels,
            explode=[0.05] * len(labels),  
            shadow=True,
            autopct=autopct_func,
            colors=custom_colors,
            startangle=90, 
            labeldistance=1.2,  
            pctdistance=0.6,  
            wedgeprops={"linewidth": 1, "edgecolor": "black"}  
            )
        pie_canvas["fig"].tight_layout()
        pie_canvas["canvas"].draw()

    def on_year_change(self, event):
        selected_year = self.year_var.get()
        self.update_yearly_data(selected_year)
        self.update_monthly_data(selected_year, self.month_var.get())

    def on_month_change(self, event):
        selected_year = self.year_var.get()
        selected_month = self.month_var.get()
        self.update_monthly_data(selected_year, selected_month)

    def upload_data(self):
        try:
            print("Starting file upload...")
            upload_file(self.user_data, self.ask_user_category_gui)
            print("File uploaded successfully. Updating dashboard...")
            self.update_yearly_data(self.year_var.get())
            self.update_monthly_data(self.year_var.get(), self.month_var.get())
            self.show_dashboard()
            print("Dashboard updated successfully.")
        except FileNotFoundError:
            print("No file was selected for upload.")
        except Exception as e:
            print(f"An error occurred during file upload: {e}")

    # ---------------- Categorization ----------------
    def build_categorization(self, parent):
        tk.Label(parent, text="Categorize Transaction", font=("Helvetica", 16)).pack(pady=10)

        self.uncategorized_label = tk.Label(parent, text="")
        self.uncategorized_label.pack(pady=10)

        tk.Label(parent, text="Select Category:").pack()
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(parent, textvariable=self.category_var, state="readonly")
        self.category_dropdown.pack(pady=10)

        self.submit_button = tk.Button(parent, text="Submit")
        self.submit_button.pack(pady=20)

    def ask_user_category_gui(self, label, categories):
        self.uncategorized_label.config(text=f"Transaction: {label}")
        self.category_dropdown['values'] = categories
        self.category_var.set(categories[0])

        self.show_categorization()

        done = tk.BooleanVar(value=False)

        def submit():
            done.set(True)

        self.submit_button.config(command=submit)

        self.root.wait_variable(done)

        self.show_dashboard()

        return self.category_var.get()

    # ---------------- Screen Switching ----------------
    def show_dashboard(self):
        self.dashboard_frame.tkraise()

    def show_categorization(self):
        self.categorization_frame.tkraise()
