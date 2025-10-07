# -*- coding: utf-8 -*-
import csv
import sys
import re
import pydoc
from datetime import datetime, date, timedelta
from pathlib import Path
from tabulate import tabulate

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

# account/account selection
def get_account_properties(accounts_info):
    """
    Displays a list of available properties and prompts the user to select one.
    Returns the selected account name and ID.
    """
    print("\nSelect a account to report on:\n")
    account_info = display_account_list(accounts_info)
    account_id, account_name = account_info
    # debug constants info
    print(f"Selected prop info:\n"
          f"account_name: {account_name}\n"
          f"account_id: {account_id}\n")
    input("Pause for debug...")
    return account_info

def display_account_list(accounts_info):
    """
    Displays available accounts in a clean tabular format and prompts
    the user to select one by number.

    Args:
        accounts_info (dict): {account_id: account_name}

    Returns:
        tuple: (account_id, account_name)
    """
    account_table = []
    for i, (account_id, account_name) in enumerate(accounts_info.items(), start=1):
        account_table.append([i, account_id, account_name])
    account_headers = ["#", "Customer ID", "Account Name"]
    data_handling_options(
        table_data=account_table,
        headers=account_headers,
        auto_view=True
    )
    if len(accounts_info) == 1:
        account_id, account_name = next(iter(accounts_info.items()))
        print(f"\nOnly one account found: {account_name} / {account_id}")
        return str(account_id), account_name
    while True:
        selection = custom_input(
            "\nSelect an account by number (1, 2, 3, etc.) or enter 'exit' to quit: "
        ).strip()
        if selection.lower() == "exit":
            sys.exit("User exited the account selection.")
        if selection.isdigit():
            selection = int(selection)
            if 1 <= selection <= len(accounts_info):
                account_id = list(accounts_info.keys())[selection - 1]
                account_name = accounts_info[account_id]
                print(f"\nSelected Account: {account_id} ({account_name})")
                choice = custom_input("Is this correct? (Y/N): ").strip().lower()
                if choice in ("y", "yes"):
                    return str(account_id), account_name
                elif choice in ("n", "no"):
                    continue
                else:
                    print("Invalid input. Please enter 'Y' or 'N'.")
                    continue
        print("Invalid selection. Please try again.")

def include_channel_types():
    while True:
        print("\nWould you like a detailed report that includes channel types? (Y)es or (N)o")
        include_channel_types_opt = input("Please select Y or N: ").strip().lower()
        if include_channel_types_opt in ('y', 'yes'):
            include_channel_types = True
            print("Channel types will be included in the report.")
            break
        elif include_channel_types_opt in ('n', 'no'):
            include_channel_types = False
            print("Channel types will NOT be included in the report.")
            break
        else:
            print("Invalid input, please select one of the indicated options (Y/N).")
    return include_channel_types

# data handling
def data_handling_options(table_data, headers, auto_view=False):
    if auto_view:
        if not table_data or not headers:
            print("No data to display.")
            return
        # display info automatically
        display_table(table_data, headers, auto_view=True)
        return
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
        sys.exit(1)

def sanitize_filename(name):
    """
    Removes invalid filename characters for cross-platform safety.
    """
    return re.sub(r'[<>:"/\\|?*]', '', name)

def save_csv(table_data, headers):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    default_file_name = f"gads_report_{timestamp}.csv"
    print(f"Default file name: {default_file_name}")
    file_name_input = input("Enter a file name (or leave blank for default): ").strip()
    if file_name_input:
        base_name = file_name_input.replace('.csv', '').strip()
        safe_name = sanitize_filename(base_name)
        if not safe_name:
            print("Invalid file name entered. Using default instead.")
            file_name = default_file_name
        else:
            file_name = f"{safe_name}.csv"
    else:
        file_name = default_file_name
    home_dir = Path.home()
    file_path = home_dir / file_name
    try:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(table_data)
        print(f"\nData saved to: {file_path}\n")
    except Exception as e:
        print(f"\nFailed to save file: {e}\n")

def display_table(table_data, headers, auto_view=False):
    """
    Displays a table using the tabulate library.
    Args:
        table_data (list): The data to display in the table.
        headers (list): The headers for the table.
    """
    if auto_view:
        print(tabulate(table_data, headers, tablefmt="simple_grid"))
    else:
        input("Report ready for viewing. Press ENTER to display results and 'Q' to exit output when done...")
        pydoc.pager(tabulate(table_data, headers=headers, tablefmt="simple_grid"))

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
        print("Reporting time range:\n"
              "1. Specific date\n"
              "2. Range of dates\n")
        date_opt_input = input("Enter 1 or 2: ")
        if date_opt_input == '1':
            date_opt = 'Specific date'
            spec_date = input("What day would you like to retrieve data for (YYYY-MM-DD): ")
            start_date = spec_date
            end_date = spec_date
            time_seg = 'date'  # time_reg day options as below
            print("Single date option selected, default time segmentation to 'date'.")
            return date_opt, start_date, end_date, time_seg
        elif date_opt_input == '2':
            date_opt = 'Date range'
            start_date = input("Start Date (YYYY-MM-DD): ")
            end_date = input("End Date (YYYY-MM-DD): ")
            while True:
                print("Date range segmentation:\n"
                    "1. Day\n"
                    "2. Week\n"
                    "3. Month\n"
                    "4. Quarter\n"
                    "5. Year\n")
                time_seg_input = input("Select from one of the above numbered options (1, 2, 3, etc): ")
                # transform time_seg
                time_seg_options = {'1': 'date', '2': 'week', '3': 'month', '4': 'quarter', '5': 'year'}
                time_seg = time_seg_options.get(time_seg_input)
                if time_seg:
                    return date_opt, start_date, end_date, time_seg
                else:
                    print("Invalid time segmentation option provided.")
        else:
            print("Invalid option, please enter 1 or 2.")

def get_last30days():
    today_actual = date.today()
    start_date = today_actual-timedelta(days=30)
    end_date = today_actual-timedelta(days=1)
    time_seg = 'date'
    date_opt = 'Date range'
    return date_opt, start_date, end_date, time_seg

def get_last_calendar_month():
    today_actual = date.today()
    first_of_this_month = today_actual.replace(day=1)
    last_day_prev_month = first_of_this_month - timedelta(days=1) # end_date
    first_day_prev_month = last_day_prev_month.replace(day=1) # start_date
    date_opt = "Last calendar month"
    time_seg = "month"
    return date_opt, first_day_prev_month, last_day_prev_month, time_seg

def get_quarter_dates(year: int, quarter: int):
    """
    Return the start and end dates for a given year and quarter (1 - 4).
    The initial dates are static to allow quarter boundries to be altered in the future of needed.
    """
    if quarter not in (1, 2, 3, 4):
        raise ValueError("Quarter must be between 1 and 4")
    if quarter == 1:
        start_date = date(year, 1, 1)
        end_date = date(year, 3, 31)
    elif quarter == 2:
        start_date = date(year, 4, 1)
        end_date = date(year, 6, 30)
    elif quarter == 3:
        start_date = date(year, 7, 1)
        end_date = date(year, 9, 30)
    else:  # Q4
        start_date = date(year, 10, 1)
        end_date = date(year, 12, 31)
    return start_date, end_date

def get_current_quarter_to_date():
    today_actual = date.today()
    year = today_actual.year
    month = today_actual.month
    current_quarter = (month - 1) // 3 + 1
    q_start, _ = get_quarter_dates(year, current_quarter)
    # quarter-to-date runs through yesterday
    start_date = q_start
    end_date = today_actual - timedelta(days=1)
    date_opt = "Date range"
    time_seg = "quarter"
    return date_opt, start_date, end_date, time_seg

def get_previous_calendar_quarter():
    today_actual = date.today()
    year = today_actual.year
    month = today_actual.month
    current_quarter = (month - 1) // 3 + 1
    # determine year/quarter
    if current_quarter == 1:
        prev_quarter = 4
        year -= 1
    else:
        prev_quarter = current_quarter - 1
    start_date, end_date = get_quarter_dates(year, prev_quarter)
    date_opt = "Date range"
    time_seg = "quarter"
    return date_opt, start_date, end_date, time_seg
