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
        self.root.geometry("1024x600")

            # Adjust the frame weights to allocate more space to the left frame
        self.root.columnconfigure(0, weight=3)  # Give more weight to the left frame
        self.root.columnconfigure(1, weight=2)  # Right frame

        # Left frame for client details and navigation
        left_frame = ttk.Frame(self.root, padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew")

            # Scrollable area in the left frame
        canvas = tk.Canvas(left_frame)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


        # Right frame for scheduling and submission
        right_frame = ttk.Frame(self.root, padding="10")
        right_frame.grid(row=0, column=1, sticky="nsew")

        # Client Details in Scrollable Frame
        self.name_label = ttk.Label(scrollable_frame, text="")
        self.name_label.grid(row=0, column=0, sticky="w", pady=2)
        self.phone_label = ttk.Label(scrollable_frame, text="")
        self.phone_label.grid(row=1, column=0, sticky="w", pady=2)
        self.phone2_label = ttk.Label(scrollable_frame, text="")
        self.phone2_label.grid(row=2, column=0, sticky="w", pady=2)
        self.email_label = ttk.Label(scrollable_frame, text="")
        self.email_label.grid(row=3, column=0, sticky="w", pady=2)
        self.bauschritt_label = ttk.Label(scrollable_frame, text="", width=50)  # Adjust width as needed
        self.bauschritt_label.grid(row=4, column=0, sticky="w", pady=2)
        self.strasse_label = ttk.Label(scrollable_frame, text="")
        self.strasse_label.grid(row=3, column=0, sticky="w", pady=2)


        # Copy Buttons in Scrollable Frame
        self.copy_button = ttk.Button(scrollable_frame, text="Copy Phone Number 1", command=lambda: self.copy_phone_number('Telefonnummer 1'))
        self.copy_button.grid(row=5, column=0, pady=5)
        self.copy_button2 = ttk.Button(scrollable_frame, text="Copy Phone Number 2", command=lambda: self.copy_phone_number('Telefonnummer 2'))
        self.copy_button2.grid(row=6, column=0, pady=5)

        # Navigation Buttons in Scrollable Frame
        self.prev_button = ttk.Button(scrollable_frame, text="Previous", command=self.show_previous_client)
        self.prev_button.grid(row=7, column=0, padx=5, pady=10, sticky="w")
        self.next_button = ttk.Button(scrollable_frame, text="Next", command=self.show_next_client)
        self.next_button.grid(row=7, column=1, padx=5, pady=10, sticky="e")

        # Calendar and Timeslot Section in Right Frame
        self.calendar = Calendar(right_frame, selectmode='day')
        self.calendar.grid(row=0, column=0, pady=10)
        self.calendar.bind("<<CalendarSelected>>", self.view_timeslots)

        self.timeslot_selector = ttk.Combobox(right_frame, state="readonly")
        self.timeslot_selector.grid(row=1, column=0, pady=10)
        self.timeslot_selector.bind("<<ComboboxSelected>>", self.on_timeslot_selected)


        # Outcome Selection and Comment Section in Right Frame
        self.outcome_var = tk.StringVar()
        outcome_options = ["Not Reached", "Successfully Terminated", "Clarify", "Cancellation", "Other"]
        outcome_label = ttk.Label(right_frame, text="Select Call Outcome:")
        outcome_label.grid(row=3, column=0, pady=5)
        outcome_menu = ttk.OptionMenu(right_frame, self.outcome_var, outcome_options[0], *outcome_options)
        outcome_menu.grid(row=4, column=0, pady=5)

        self.comment_entry = tk.Text(right_frame, height=4, width=50)
        self.comment_entry.grid(row=5, column=0, pady=5)

        # Submit Button in Right Frame
        submit_button = ttk.Button(right_frame, text="Submit Outcome", command=self.submit_outcome)
        submit_button.grid(row=6, column=0, pady=10)

        # Configure grid behavior
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(7, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(7, weight=1)

        # Initialize with the first client
        self.show_client(0)




    def view_timeslots(self, event=None):
        selected_date = self.calendar.get_date()

        # Convert 'MM/DD/YY' to 'YYYY-MM-DD'
        try:
            formatted_date = datetime.strptime(selected_date, '%m/%d/%y').strftime('%Y-%m-%d')
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format: {e}")
            return

        try:
            events = get_events_on_date(formatted_date)
            booked_slots = [event['start']['dateTime'][11:16] for event in events if 'dateTime' in event['start']]

            # Generate 20-minute timeslots
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
        self.phone2_label.config(text=f"Telefon 2: {client.get('Telefonnummer 2', '')}")
        bauschritt_key = 'N\x8achste Bauschritt'
        self.bauschritt_label.config(text=f"Nächster Bauschritt: {client.get(bauschritt_key, '')}")
        self.strasse_label.config(text=f"Adresse: {client.get('Stra§e', '')}, {client.get('Hausnummer', '')}, {client.get('Teilpolygon', '')}")

       





        print(f"Showing client: {client}")

    def copy_phone_number(self, phone_key):
        current_client = self.csv_data[self.current_index]
        phone_number = current_client.get(phone_key, '')
        pyperclip.copy(phone_number)
        print(f"{phone_key} copied:", phone_number)


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
        client_address = f"{current_client.get('Stra§e', '')}, {current_client.get('Hausnummer', '')}"  # Combine street and house number

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

      