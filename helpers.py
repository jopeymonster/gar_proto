import time
import csv
from pathlib import Path
import os
import sys
import re
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse

# 3p imports
from tabulate import tabulate

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
default_file_name = f"gads_report_{timestamp}.csv"

# exceptions wrapper
def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            print_error(func.__name__, e)
        except ValueError as e:
            print_error(func.__name__, e)
        except KeyboardInterrupt as e:
            print_error(func.__name__, e)
        except FileNotFoundError as e:
            print_error(func.__name__, e)
        except AttributeError as e:
            print_error(func.__name__, )
        except Exception as e:
            print_error(func.__name__, e)
    def print_error(func_name, error):
        print(f"\nError in function '{func_name}': {repr(error)} - Exiting...\n")
    return wrapper

# user error logging
def user_error(err_type):
    if err_type == 1:
        sys.exit("Problem with MAIN loop.")
    if err_type == 2:
        sys.exit("Invalid input.")
    elif err_type in [3,4]:
        sys.exit("Problem with output data.")

# exit menu, 'exit'
def custom_input(prompt=''):
    user_input = original_input(prompt)
    if user_input.lower() == 'exit':
        print("Exiting the program.")
        sys.exit()
    return user_input

# set __builtins__ module or a dictionary
if isinstance(__builtins__, dict):
    original_input = __builtins__['input']
    __builtins__['input'] = custom_input
else:
    original_input = __builtins__.input
    __builtins__.input = custom_input

# data handling
def save_to_csv(table_data, filename=default_file_name):
    headers = [
        "date",
        "property",
        "campaign name",
        "campaign group",
        "campaign labels",
        "ad_group name",
        "ad_group labels",
        "campaign channel_type",
        "cost",
        "impressions",
        "clicks",
        "interactions",
        "conversions",
        "conversions value",
        "property id",
        "campaign id",
        "ad_group id"
    ]
    home_dir = Path.home()
    file_path = home_dir / filename
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(table_data)
    print(f"Data saved to {file_path}")

def display_prop_list(prop_dict):
    print("\nAvailable Properties:")
    for i, (prop_name, values) in enumerate(prop_dict.items(), start=1):
        prop_id, prop_url = values
        print(f"{i}. {prop_name} / ID: {prop_id}, URL: {prop_url}")
    while True:
        selection = custom_input("\nSelect a property by number (1, 2, 3, etc) or enter 'exit' to exit: ").strip()
        if selection.isdigit():
            selection = int(selection)
            if 1 <= selection <= len(prop_dict):
                prop_name = list(prop_dict.keys())[selection - 1]
                prop_id, prop_url = prop_dict[prop_name]
                print(f"\nProp Info: {prop_name}, {prop_id}, {prop_url}")
                choice = custom_input("Is this correct? (Y/N): ").strip().lower()
                if choice == "y":
                    prop_info = prop_name, prop_id, prop_url
                    return prop_info
                elif choice == "n":
                    continue
                else:
                    print("Invalid input. Please enter 'Y' or 'N'.")
                    continue
        print("Invalid selection. Please try again.")

def get_timerange():
    while True:
        print("Search for:\n"
              "1. Specific date\n"
              "2. Range of dates\n")
        date_opt_input = input("Enter 1 or 2: ")
        if date_opt_input == '1':
            date_opt = 'Specific date'
            spec_date = input("What day would you like to retrieve data for (YYYY-MM-DD): ")
            start_date = spec_date
            end_date = spec_date
            time_seg = 'date'  # time_reg day options as below
            return date_opt, start_date, end_date, time_seg
        elif date_opt_input == '2':
            date_opt = 'Date range'
            start_date_input = input("Start Date (YYYY-MM-DD): ")
            end_date_input = input("End Date (YYYY-MM-DD): ")
            # placeholders if needing to convert input
            start_date = start_date_input
            end_date = end_date_input
            time_seg = 'date'
            return date_opt, start_date, end_date, time_seg
            """ # needs work        
            while True:
                print("Select a time segmentation for your requested date range: \n"
                      "1. Day\n"
                      "2. Week\n"
                      "3. Month\n"
                      "4. Quarter\n"
                      "5. Year")
                time_seg_input = input("Select one of the options (1-5) from above: ")
                if time_seg_input not in ['1', '2', '3', '4', '5']:
                    print("Invalid option, please choose from one of the provided options.")
                else:
                    # transform time_seg
                    time_seg_options = {'1': 'day', '2': 'week', '3': 'month', '4': 'quarter', '5': 'year'}
                    time_seg = time_seg_options.get(time_seg_input)
                    if time_seg is None:
                        raise ValueError("Invalid time segmentation option provided.")
                    return date_opt, start_date, end_date, time_seg
                    """
        else:
            print("Invalid option")