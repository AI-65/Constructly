import tkinter as tk
from gui import ClientManagementSystem
from csv_loader import load_csv_data

def main():
    root = tk.Tk()
    csv_data = load_csv_data("C:/Users/iljag/client_management_system/data/dieblich.csv")  # Load the CSV data
    app = ClientManagementSystem(root, csv_data)  # Instantiate the client management system
    root.mainloop()

if __name__ == "__main__":
    main()
