from backend import *
from frontend import *
import sys

def on_closing(root, app):
    # Only close matplotlib figure if it exists
    if hasattr(app, "fig"):
        plt.close(app.fig)
    root.destroy()
    sys.exit()

# Load data if any exists

user_data = AllData()

if data_exists():
    with open('database.json', 'r') as file:
        data = json.load(file)
    user_data.load_data(data)
else:
    print("No existing data found.")
    user_data.add_year(2025)  # Initialize with a default year

# Display dashboard using existing data

root = tk.Tk()
app = FinanceTrackerGUI(root, user_data)
root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, app))
root.mainloop()
