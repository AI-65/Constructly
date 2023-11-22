import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip  # Ensure pyperclip is installed for clipboard functionality
from calendar_integration import get_events_on_date, create_event
from tkcalendar import Calendar
from datetime import datetime

class ClientManagementSystem:
    def __init__(self, root, csv_data):
        self.root = root
        self.csv_data = csv_data
        self.current_index = 0
        self.selected_timeslot = None  # Initialize selected_timeslot here
        self.initialize_ui()

    def initialize_ui(self):
        self.root.title("Client Management System")
        self.root.geometry("600x400")

        # Client Details
        self.client_details_frame = ttk.Frame(self.root)
        self.client_details_frame.pack(side="top", fill="both", expand=True)

        self.name_label = ttk.Label(self.client_details_frame, text="")
        self.name_label.pack(side="top", pady=5)
        self.phone_label = ttk.Label(self.client_details_frame, text="")
        self.phone_label.pack(side="top", pady=5)
        self.email_label = ttk.Label(self.client_details_frame, text="")
        self.email_label.pack(side="top", pady=5)

        # Copy Button
        self.copy_button = ttk.Button(self.root, text="Copy Phone Number", command=self.copy_phone_number)
        self.copy_button.pack(side="top", pady=10)

        # Outcome Selection
        self.outcome_var = tk.StringVar()
        outcome_options = ["Not Reached", "Successfully Terminated", "Clarify", "Cancellation", "Other"]
        outcome_label = tk.Label(self.root, text="Select Call Outcome:")
        outcome_label.pack(side="top", pady=5)
        outcome_menu = ttk.OptionMenu(self.root, self.outcome_var, outcome_options[0], *outcome_options)
        outcome_menu.pack(side="top", pady=5)

        # Comment Section
        comment_label = tk.Label(self.root, text="Comments:")
        comment_label.pack(side="top", pady=5)
        self.comment_entry = tk.Text(self.root, height=4, width=50)
        self.comment_entry.pack(side="top", pady=5)

        # Navigation Buttons
        self.prev_button = ttk.Button(self.root, text="Previous", command=self.show_previous_client)
        self.prev_button.pack(side="left", padx=10)
        self.next_button = ttk.Button(self.root, text="Next", command=self.show_next_client)
        self.next_button.pack(side="right", padx=10)

        # Submit Button
        submit_button = ttk.Button(self.root, text="Submit Outcome", command=self.submit_outcome)
        submit_button.pack(side="bottom", pady=10)

        # Initialize with the first client
        self.show_client(0)

        # Calendar Widget for Selecting Date
        self.calendar = Calendar(self.root, selectmode='day')
        self.calendar.pack(side="top", pady=5)

        self.view_timeslots_button = ttk.Button(self.root, text="View Timeslots", command=self.view_timeslots)
        self.view_timeslots_button.pack(side="top", pady=5)

        # Timeslot Selector
        self.timeslot_selector = ttk.Combobox(self.root, state="readonly")
        self.timeslot_selector.pack(side="top", pady=5)
        self.timeslot_selector.bind("<<ComboboxSelected>>", self.on_timeslot_selected)



    def view_timeslots(self):
        selected_date = self.calendar.get_date()

        try:
            formatted_date = datetime.strptime(selected_date, '%m/%d/%y').strftime('%Y-%m-%d')
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format: {e}")
            return

        try:
            events = get_events_on_date(formatted_date)
            booked_slots = [event['start']['dateTime'][11:16] for event in events if 'dateTime' in event['start']]

            # Generate timeslots for every 20 minutes
            available_slots = []
            for hour in range(9, 18):
                for minute in (0, 20, 40):
                    slot = f"{hour:02d}:{minute:02d}"
                    if slot not in booked_slots:
                        available_slots.append(slot)

            self.timeslot_selector['values'] = available_slots
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching events: {e}")



    def show_client(self, index):
        client = self.csv_data[index]
        self.name_label.config(text=f"Name: {client.get('Kontaktperson', '')}")
        self.phone_label.config(text=f"Phone: {client.get('Telefonnummer 1', '')}")
        self.email_label.config(text=f"Email: {client.get('E-Mail', '')}")

    def copy_phone_number(self):
        current_client = self.csv_data[self.current_index]
        phone_number = current_client.get('Telefonnummer 1', '')
        pyperclip.copy(phone_number)
        print("Phone number copied:", phone_number)

    def show_next_client(self):
        self.current_index = min(self.current_index + 1, len(self.csv_data) - 1)
        self.show_client(self.current_index)

    def show_previous_client(self):
        self.current_index = max(self.current_index - 1, 0)
        self.show_client(self.current_index)

    def on_timeslot_selected(self, event=None):
        self.selected_timeslot = self.timeslot_selector.get()
        print(f"Timeslot selected: {self.selected_timeslot}")

    def submit_outcome(self):
        selected_outcome = self.outcome_var.get()
        comment_text = self.comment_entry.get("1.0", tk.END).strip()

        # Retrieve current client information
        current_client = self.csv_data[self.current_index]
        client_name = current_client.get('Kontaktperson', '')  # Adjust the key as per your CSV
        client_phone = current_client.get('Telefonnummer 1', '')
        client_email = current_client.get('E-Mail', '')
        client_address = f"{current_client.get('Straße', '')}, {current_client.get('Hausnummer', '')}"  # Combine street and house number

        # Prepare event description with client information
        event_description = f"Meeting with {client_name}\nPhone: {client_phone}\nEmail: {client_email}\nAddress: {client_address}\n\n{comment_text}"

        # Use the calendar widget to get the selected date
        selected_date = self.calendar.get_date()
        try:
            # Convert 'MM/DD/YY' to 'YYYY-MM-DD'
            formatted_date = datetime.strptime(selected_date, '%m/%d/%y').strftime('%Y-%m-%d')
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format: {e}")
            return

        if self.selected_timeslot:
            start_time_str = f"{formatted_date}T{self.selected_timeslot}:00"
            create_event(start_time_str, f"Hausbesuch/Montage bei {client_name}", 1, event_description)
            print(f"Created event at timeslot: {self.selected_timeslot}")
        else:
            print("No timeslot selected.")

        print(f"Outcome for {client_name}: {selected_outcome}, Comment: {comment_text}")
        self.show_next_client()  # Move to next client

      
