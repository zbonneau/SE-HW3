import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
import datetime
from typing import List
import csv

# Define the GroceryItem, Day, and Month classes
class GroceryItem:
    def __init__(self, name, quantity, price_per_unit):
        self.name = name
        self.quantity = quantity
        self.price_per_unit = price_per_unit

    def get_total_price(self):
        return self.quantity * self.price_per_unit

class Day:
    def __init__(self, date):
        self.date = date
        self.items = []

    def add_grocery_item(self, item):
        for existing_item in self.items:
            if existing_item.name == item.name and existing_item.price_per_unit == item.price_per_unit:
                existing_item.quantity += item.quantity
                break
        else:
            self.items.append(item)

    def get_total_expenses(self):
        return sum(item.get_total_price() for item in self.items)
    
    def generate_daily_report(self) -> str:
        report = f"Grocery Expenses for {self.date.strftime('%B')} {self.date.year}:\n"
        for item in self.items:
            report += f"{item.name}: ${item.get_total_price():.2f}\n"
        report += f"Total Expenses: ${self.get_total_expenses():.2f}"
        return report

class Month:
    def __init__(self, month, year):
        self.month = month
        self.year = year
        self.days = []

    def add_day(self, day):
        self.days.append(day)

    def get_days(self):
        return self.days

    def get_total_expenses(self):
        return sum(day.get_total_expenses() for day in self.days)
    
    def generate_monthly_report(self):
        item_costs = {}
        for day in self.days:
            for item in day.items:
                if item.name in item_costs:
                    item_costs[item.name] += item.get_total_price()
                else:
                    item_costs[item.name] = item.get_total_price()

        report = f"Grocery Expenses for {self.month}-{self.year}:\n\n"
        for item, cost in item_costs.items():
            report += f"{item}: ${cost:.2f}\n"

        total_expenses = sum(item_costs.values())
        report += f"\nTotal Expenses for {self.month}-{self.year}: ${total_expenses:.2f}\n"
        return report or "No expenses recorded for this month."

    def import_monthly_groceries(self, file_path: str) -> None:
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                day, item_name, quantity, price_per_unit = row
                date = datetime.datetime.strptime(day, '%Y-%m-%d').date()
                item = GroceryItem(item_name, int(quantity), float(price_per_unit))
                for existing_day in self.days:
                    if existing_day.date == date:
                        existing_day.add_grocery_item(item)
                        break
                else:
                    new_day = Day(date)
                    new_day.add_grocery_item(item)
                    self.add_day(new_day)

# Define the UI
class GroceryExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grocery Expense Tracker")

        self.months = []

        self.create_widgets()

    def create_widgets(self):
        # Label for item name
        self.label = tk.Label(self.root, text="Enter Grocery Item:")
        self.label.pack()

        # Entry field for item name
        self.item_name_entry = tk.Entry(self.root)
        self.item_name_entry.pack()

        # Label for quantity
        self.label2 = tk.Label(self.root, text="Enter Quantity:")
        self.label2.pack()

        # Entry field for quantity
        self.quantity_entry = tk.Entry(self.root)
        self.quantity_entry.pack()

        # Label for price per unit
        self.label3 = tk.Label(self.root, text="Enter Price per Unit:")
        self.label3.pack()

        # Entry field for price per unit
        self.price_entry = tk.Entry(self.root)
        self.price_entry.pack()

        # Label for date selection
        self.label4 = ttk.Label(self.root, text="Select Date:")
        self.label4.pack()

        # DateEntry widget for date selection
        self.date_entry = DateEntry(self.root, width=12, date_pattern="yyyy-mm-dd")
        self.date_entry.pack()

        # Button to add item
        self.add_button = tk.Button(self.root, text="Add Item", command=self.add_item)
        self.add_button.pack()

        # Button to generate daily report
        self.daily_report_button = tk.Button(self.root, text="Generate Daily Report", command=self.generate_daily_report)
        self.daily_report_button.pack()

        # Button to generate monthly report
        self.monthly_report_button = tk.Button(self.root, text="Generate Monthly Report", command=self.generate_monthly_report)
        self.monthly_report_button.pack()

        # Entry field for file path
        self.file_path_entry = ttk.Entry(self.root)
        self.file_path_entry.pack()

        # Button to import groceries
        self.import_button = ttk.Button(self.root, text="Import Groceries", command=self.import_groceries)
        self.import_button.pack()

    def import_groceries(self):
        file_path = self.file_path_entry.get()
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            first_row = next(csv_reader)
            first_date = datetime.datetime.strptime(first_row[0], '%Y-%m-%d').date()
            month_obj = self.get_month_for_date(first_date)
            if month_obj is None:
                month_obj = Month(first_date.month, first_date.year)
                self.months.append(month_obj)
            month_obj.import_monthly_groceries(file_path)

    def get_month_for_date(self, date):
        for month in self.months:
            if month.month == date.month and month.year == date.year:
                return month
        return None

    def add_item(self):
        # Get input from UI elements
        item_name = self.item_name_entry.get()
        quantity_text = self.quantity_entry.get()
        price_text = self.price_entry.get()
        selected_date = self.date_entry.get_date()

        # Validate input
        if not (item_name and quantity_text and price_text):
            messagebox.showerror("Error", "Please fill all fields.")
            return

        try:
            quantity = int(quantity_text)
            price_per_unit = float(price_text)
        except ValueError:
            messagebox.showerror("Error", "Invalid input for quantity or price.")
            return

        if quantity <= 0 or price_per_unit <= 0:
            messagebox.showerror("Error", "Quantity and price per unit must be positive.")
            return

        # Extract year and month from the selected date
        selected_year = selected_date.year
        selected_month = selected_date.month

        # Find or create the selected month
        selected_month_obj = None
        for month in self.months:
            if month.month == selected_month and month.year == selected_year:
                selected_month_obj = month
                break
        if not selected_month_obj:
            selected_month_obj = Month(selected_month, selected_year)
            self.months.append(selected_month_obj)

        # Find or create the selected day
        selected_day = None
        for day in selected_month_obj.get_days():
            if day.date == selected_date:
                selected_day = day
                break
        if not selected_day:
            selected_day = Day(selected_date)
            selected_month_obj.add_day(selected_day)

        # Create a GroceryItem object
        item = GroceryItem(item_name, quantity, price_per_unit)

        # Add the item to the selected day
        selected_day.add_grocery_item(item)

        messagebox.showinfo("Item Added", f"Item '{item_name}' added successfully.")

    def generate_daily_report(self):
        selected_date = self.date_entry.get_date()

        selected_month_obj = None
        for month in self.months:
            if month.month == selected_date.month and month.year == selected_date.year:
                selected_month_obj = month
                break

        if selected_month_obj:
            for day in selected_month_obj.days:
                if day.date == selected_date:
                    report = day.generate_daily_report()
                    messagebox.showinfo("Daily Report", report)
                    break
            else:
                messagebox.showinfo("Daily Report", f"No data available for {selected_date}.")
        else:
            messagebox.showinfo("Daily Report", f"No data available for {selected_date}.")

    def generate_monthly_report(self):
        selected_date = self.date_entry.get_date()
        selected_month = selected_date.month
        selected_year = selected_date.year

        selected_month_obj = None
        for month in self.months:
            if month.month == selected_month and month.year == selected_year:
                selected_month_obj = month
                break

        if selected_month_obj:
            report = selected_month_obj.generate_monthly_report()
            messagebox.showinfo("Monthly Report", report)
        else:
            messagebox.showinfo("Monthly Report", f"No data available for {selected_month}-{selected_year}.")

    def run(self):
        self.root.mainloop()

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    app = GroceryExpenseTrackerApp(root)
    app.run()
