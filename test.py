import unittest
from unittest.mock import patch
import datetime
import os
import csv
import tkinter as tk
from tkinter import messagebox

# Importing classes from the provided script
from grocery_tracker import GroceryItem, Day, Month, GroceryExpenseTrackerApp

class TestGroceryExpenseTracker(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()  # Creating a Tkinter root window
        self.app = GroceryExpenseTrackerApp(self.root)

    def tearDown(self):
        self.root.update()
        self.root.destroy()  # Destroying the Tkinter root window
        # Clean up any created files
        if os.path.exists("test_import.csv"):
            os.remove("test_import.csv")

    # Test methods...
    def test_add_grocery_item_valid(self):
        item = GroceryItem("Milk", 2, 3.5)
        self.assertEqual(item.name, "Milk")
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price_per_unit, 3.5)

    @patch('grocery_tracker.messagebox.showerror')
    def test_add_grocery_item_invalid_values(self, mock_showerror):
        # Set up invalid input values
        invalid_values = [
            ("", "10", "5.99"),        # Missing item name
            ("Apple", "", "5.99"),     # Missing quantity
            ("Orange", "10", ""),      # Missing price per unit
            ("Banana", "0", "5.99"),   # Zero quantity
            ("Grapes", "10", "-5.99"), # Negative price per unit
            ("Watermelon", "-10", "5.99") # Negative quantity
        ]

        # Iterate through invalid input values and try to add them
        for item_name, quantity, price_per_unit in invalid_values:
            # Set values in entry fields
            self.app.item_name_entry.insert(0, item_name)
            self.app.quantity_entry.insert(0, quantity)
            self.app.price_entry.insert(0, price_per_unit)

            # Call add_item method
            self.app.add_item()

            # Check if messagebox.showerror was called
            self.assertTrue(mock_showerror.called)

            # Clear entry fields for next iteration
            self.app.item_name_entry.delete(0, 'end')
            self.app.quantity_entry.delete(0, 'end')
            self.app.price_entry.delete(0, 'end')

            # Reset mock call status
            mock_showerror.reset_mock()

    def test_generate_daily_report(self):
        day = Day(datetime.date(2024, 4, 30))
        item1 = GroceryItem("Apples", 3, 2)
        item2 = GroceryItem("Bananas", 2, 1.5)
        day.add_grocery_item(item1)
        day.add_grocery_item(item2)
        expected_report = "Grocery Expenses for April 2024:\nApples: $6.00\nBananas: $3.00\nTotal Expenses: $9.00"
        self.assertEqual(day.generate_daily_report(), expected_report)

    def test_generate_monthly_report(self):
        month = Month(4, 2024)
        day1 = Day(datetime.date(2024, 4, 1))
        item1 = GroceryItem("Milk", 2, 3)
        day1.add_grocery_item(item1)
        month.add_day(day1)
        day2 = Day(datetime.date(2024, 4, 2))
        item2 = GroceryItem("Bread", 1, 2.5)
        day2.add_grocery_item(item2)
        month.add_day(day2)
        expected_report = "Grocery Expenses for 4-2024:\n\nMilk: $6.00\nBread: $2.50\n\nTotal Expenses for 4-2024: $8.50\n"
        self.assertEqual(month.generate_monthly_report(), expected_report)

    @patch('grocery_tracker.messagebox.showinfo')
    def test_generate_daily_report_no_data(self, mock_showinfo):
        self.app.generate_daily_report()
        _, messagebox_text = mock_showinfo.call_args[0]
        self.assertTrue(messagebox_text.startswith("No data available"))

    @patch('grocery_tracker.messagebox.showinfo')
    def test_generate_monthly_report_no_data(self, mock_showinfo):
        self.app.generate_monthly_report()
        _, messagebox_text = mock_showinfo.call_args[0]
        self.assertTrue(messagebox_text.startswith("No data available"))

    def test_import_groceries(self):
        # Creating a test CSV file
        with open("test_import.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["2024-04-30", "Eggs", 1, 2])
            writer.writerow(["2024-04-30", "Cheese", 2, 4.5])

        month = Month(4, 2024)
        self.app.months = [month]
        self.app.file_path_entry.insert(0, "test_import.csv")
        self.app.import_groceries()
        self.assertEqual(len(month.days), 1)
        self.assertEqual(len(month.days[0].items), 2)
        self.assertEqual(month.days[0].items[0].name, "Eggs")
        self.assertEqual(month.days[0].items[1].name, "Cheese")

    def test_import_groceries_nonexistent_file(self):
        self.app.file_path_entry.insert(0, "nonexistent_file.csv")
        with self.assertRaises(FileNotFoundError):
            self.app.import_groceries()

    def test_import_groceries_invalid_csv_format(self):
        # Creating a test CSV file with invalid format
        with open("test_invalid_format.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["2024-04-30", "Eggs", 1])  # Missing fields

        self.app.file_path_entry.insert(0, "test_invalid_format.csv")
        with self.assertRaises(ValueError):
            self.app.import_groceries()


if __name__ == '__main__':
    unittest.main()
