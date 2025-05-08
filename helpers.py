import time
import csv
from pathlib import Path
import os
import sys
import re
import pydoc
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse

# 3p imports
from tabulate import tabulate
from authfiles import account_constants

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
def data_handling_options(table_data, headers):
    print("How would you like to view the report?\n"
            "1. CSV\n"
            "2. Display table on screen\n")
    report_view = input("Choose 1 or 2 ('exit' to exit): ")
    if report_view == '1':
        # save to csv
        save_csv(table_data, headers)
    elif report_view == '2':
        # display table
        display_table(table_data, headers)
    else:
        print("Invalid input, please select one of the indicated options.")
        # exit
        sys.exit(1)

def save_csv(table_data, headers):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    default_file_name = f"gads_report_{timestamp}.csv"
    print("Enter a file name  or leave blank for default...")
    file_name_input = input(f"(default: {default_file_name}): ").strip()
    if file_name_input is None:
        file_name = default_file_name
    else:
        file_name = f"{file_name_input}.csv"
    home_dir = Path.home()
    file_path = home_dir / file_name
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(table_data)
    print(f"Data saved to {file_path}")

def display_table(table_data, headers):
    """
    Displays a table using the tabulate library.
    Args:
        table_data (list): The data to display in the table.
        headers (list): The headers for the table.
    """
    input("Report ready for viewing. Press ENTER to display results and 'Q' to exit output when done...")
    pydoc.pager(tabulate(table_data, headers=headers, tablefmt="simple_grid"))

# account/property selection
def get_account_properties():
    prop_dict = account_constants.PROP_INFO
    print("Select a property to report on:\n")
    prop_info = display_prop_list(prop_dict)
    prop_name, prop_id, prop_url = prop_info
    # debug constants info
    print(f"\nSelected prop info:\n"
          f"prop_name: {prop_name}\n"
          f"prop_id: {prop_id}\n"
          f"prop_url: {prop_url}")
    input("Pause for debug...")
    return prop_info

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

def extract_arc(campaign_name):
    """
    Extracts the ARC designation from a campaign name.
    The ARC is defined as the text after the last colon ':'.
    Args:
        campaign_name (str): The full campaign name.
    Returns:
        str: The extracted ARC value, or 'UNDEFINED' if not found.
    """
    if not campaign_name or ':' not in campaign_name:
        return 'UNDEFINED'
    arc = campaign_name.rsplit(':', 1)[-1].strip()
    return arc if arc else 'UNDEFINED'

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

""" needs testing
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
        elif date_opt_input == '2':
            date_opt = 'Date range'
            start_date_input = input("Start Date (YYYY-MM-DD): ")
            end_date_input = input("End Date (YYYY-MM-DD): ")
            # placeholders if needing to convert input
            start_date = start_date_input
            end_date = end_date_input
            time_seg = 'date'
        else:
            print("Invalid option")
        date_vars = {}
        start_string_value = "start"
        end_string_value = "end"
        date_vars[start_string_value] = f"'{start_date}'"
        date_vars[end_string_value] = f"'{end_date}'"
        start_date_string = str(date_vars[start_string_value])
        end_date_string = str(date_vars[end_string_value])
        
        # testing - timeframe transformations, date_opt scope      
        # if date_opt == 'EQUALS': # AD_GROUP_SINGLE
        #     time_condition = '='
        #     start_date = date_vars["start"]
        # elif date_opt == 'BETWEEN': # AD_GROUP_RANGE
        #     time_condition = date_opt
        #     start_date = date_vars["start"]
        #     end_date = date_vars["end"]
        # elif date_opt == 'DURING': # AD_GROUP_SINGLE
        #     start_date = time_seg
        #     time_condition = date_opt
        #     time_seg = 'date'
        # else:
        #     raise ValueError("Improper input or incorrect report date details")
        
        # query testing
        print("\nServices params passback after get_timerange:\n"
            f"date_opt: {date_opt}\n"
            f"time_seg: {time_seg}\n"
            f"start_date: {start_date}\n"
            f"start_date_string: {start_date_string}\n"
            f"end_date: {end_date}\n"
            f"end_date_string: {end_date_string}\n")
            # f"time_condition: {time_condition}")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit")

        # time_detail = _query.TIME_DETAIL_STRINGS.get(date_opt)

        # debug
        # print(time_detail)
        # input("Pause for debug, enter 'exit' to exit or ENTER to continue.")
        timerange_opts = (date_opt, start_date_string, end_date_string, time_seg)
        return date_opt, start_date_string, end_date_string, time_seg
"""