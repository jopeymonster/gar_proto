# -*- coding: utf-8 -*-
import csv
import pydoc
import re
import sys
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from tabulate import tabulate


# user error logging
def user_error(err_type):
    if err_type == 1:
        sys.exit("Problem with MAIN loop.")
    if err_type == 2:
        sys.exit("Invalid input.")
    elif err_type in [3, 4]:
        sys.exit("Problem with output data.")


# exit menu, 'exit'
def custom_input(prompt=""):
    user_input = original_input(prompt)
    if user_input.lower() == "exit":
        print("Exiting the program.")
        sys.exit()
    return user_input


# set __builtins__ module or a dictionary
if isinstance(__builtins__, dict):
    original_input = __builtins__["input"]
    __builtins__["input"] = custom_input
else:
    original_input = __builtins__.input
    __builtins__.input = custom_input

MICROS_PER_UNIT = Decimal("1000000")


def micros_to_decimal(micros, quantize=None, rounding=ROUND_HALF_UP):
    """Convert a micro-amount value to a Decimal without float precision loss."""
    if micros in (None, ""):
        value = Decimal("0")
    else:
        value = Decimal(str(micros)) / MICROS_PER_UNIT
    if quantize is not None:
        return value.quantize(quantize, rounding=rounding)
    return value


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
    print(
        f"Selected prop info:\naccount_name: {account_name}\naccount_id: {account_id}\n"
    )
    input("If correct, press ENTER to continue or input 'exit' to exit: ")
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
        account_table.append([i, account_name, account_id])
    account_headers = ["#", "Account Name", "Customer ID"]
    if len(accounts_info) == 1:
        account_id, account_name = next(iter(accounts_info.items()))
        print(f"\nOne account to process: {account_name} / {account_id}")
        return str(account_id), account_name
    while True:
        data_handling_options(
            table_data=account_table, headers=account_headers, auto_view=True
        )
        selection = input(
            "\nSelect an account by number (1, 2, 3, etc.) or enter 'exit' to quit: "
        ).strip()
        if selection.isdigit():
            selection = int(selection)
            if 1 <= selection <= len(accounts_info):
                account_id = list(accounts_info.keys())[selection - 1]
                account_name = accounts_info[account_id]
                print(f"\nSelected Account: {account_name} / {account_id} ")
                choice = input("Is this correct? (Y/N): ").strip().lower()
                if choice in ("y", "yes"):
                    return str(account_id), account_name
                elif choice in ("n", "no"):
                    continue
                else:
                    print("Invalid input. Please enter 'Y' or 'N'.")
                    continue
        print("Invalid selection. Please try again.")


# data handling/display
def data_handling_options(table_data, headers, auto_view=False):
    if auto_view:
        if not table_data or not headers:
            print("No data to display.")
            return
        # display info automatically
        display_table(table_data, headers, auto_view=True)
        return
    print(
        "How would you like to view the report?\n1. CSV\n2. Display table on screen\n"
    )
    report_view = input("Choose 1 or 2 ('exit' to exit): ")
    if report_view == "1":
        # save to csv
        save_csv(table_data, headers)
    elif report_view == "2":
        # display table
        display_table(table_data, headers)
    else:
        print("Invalid input, please select one of the indicated options.")
        sys.exit(1)


def sanitize_filename(name):
    """
    Removes invalid filename characters for cross-platform safety.
    """
    return re.sub(r'[<>:"/\\|?*]', "", name)


def save_csv(table_data, headers):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    default_file_name = f"gads_report_{timestamp}.csv"
    print(f"Default file name: {default_file_name}")
    file_name_input = input("Enter a file name (or leave blank for default): ").strip()
    if file_name_input:
        base_name = file_name_input.replace(".csv", "").strip()
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
        with open(file_path, mode="w", newline="") as file:
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
        input(
            "Report ready for viewing. Press ENTER to display results and 'Q' to exit output when done..."
        )
        pydoc.pager(tabulate(table_data, headers=headers, tablefmt="simple_grid"))


# data transforming/selecting
def extract_arc(campaign_name):
    """
    Extracts the ARC designation from a campaign name.
    The ARC is defined as the text after the last colon ':'.
    Args:
        campaign_name (str): The full campaign name.
    Returns:
        str: The extracted ARC value, or 'UNDEFINED' if not found.
    """
    if not campaign_name or ":" not in campaign_name:
        return "UNDEFINED"
    arc = campaign_name.rsplit(":", 1)[-1].strip()
    return arc if arc else "UNDEFINED"


def aggregate_channels():
    while True:
        print(
            "\nWould you like a detailed report that includes aggregates channel types? (Y)es or (N)o"
        )
        aggregate_channels_opt = input("Please select Y or N: ").strip().lower()
        if aggregate_channels_opt in ("y", "yes"):
            aggregate_channels = True
            print("Channel types will be aggregated in the report.")
            break
        elif aggregate_channels_opt in ("n", "no"):
            aggregate_channels = False
            print("Channel types will NOT be aggregated in the report.")
            break
        else:
            print("Invalid input, please select one of the indicated options (Y/N).")
    return aggregate_channels


def include_channel_types():
    while True:
        print(
            "\nWould you like a detailed report that includes channel types? (Y)es or (N)o"
        )
        include_channel_types_opt = input("Please select Y or N: ").strip().lower()
        if include_channel_types_opt in ("y", "yes"):
            include_channel_types = True
            print("Channel types will be included in the report.")
            break
        elif include_channel_types_opt in ("n", "no"):
            include_channel_types = False
            print("Channel types will NOT be included in the report.")
            break
        else:
            print("Invalid input, please select one of the indicated options (Y/N).")
    return include_channel_types


def include_campaign_info():
    while True:
        print(
            "\nWould you like a detailed report that includes campaign names and IDs? (Y)es or (N)o"
        )
        include_campaign_info_opt = input("Please select Y or N: ").strip().lower()
        if include_campaign_info_opt in ("y", "yes"):
            include_campaign_info = True
            print("Campaign names and IDs will be included in the report.")
            break
        elif include_campaign_info_opt in ("n", "no"):
            include_campaign_info = False
            print("Campaign names and IDs will NOT be included in the report.")
            break
        else:
            print("Invalid input, please select one of the indicated options (Y/N).")
    return include_campaign_info


def include_adgroup_info():
    while True:
        print(
            "\nWould you like a detailed report that includes ad group names and IDs? (Y)es or (N)o"
        )
        include_adgroup_info_opt = input("Please select Y or N: ").strip().lower()
        if include_adgroup_info_opt in ("y", "yes"):
            include_adgroup_info = True
            print("Ad group names and IDs will be included in the report.")
            break
        elif include_adgroup_info_opt in ("n", "no"):
            include_adgroup_info = False
            print("Ad group names and IDs will NOT be included in the report.")
            break
        else:
            print("Invalid input, please select one of the indicated options (Y/N).")
    return include_adgroup_info


def include_device_info():
    while True:
        print(
            "\nWould you like a detailed report that includes device types? (Y)es or (N)o"
        )
        include_device_info_opt = input("Please select Y or N: ").strip().lower()
        if include_device_info_opt in ("y", "yes"):
            include_device_info = True
            print("Device types will be included in the report.")
            break
        elif include_device_info_opt in ("n", "no"):
            include_device_info = False
            print("Device types will NOT be included in the report.")
            break
        else:
            print("Invalid input, please select one of the indicated options (Y/N).")
    return include_device_info


# timedate handling
SUPPORTED_DATE_FORMATS = ("%Y-%m-%d", "%Y%m%d")


def parse_supported_date(date_str):
    """Return a 'date' object if 'date_str' matches a supported format."""
    for fmt in SUPPORTED_DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt).date()
        except (TypeError, ValueError):
            continue
    raise ValueError(f"Unsupported date format: {date_str}")


def get_timerange(force_single=False):
    """
    Prompt the user to select either a single date or a date range,
    with validation for supported formats (YYYY-MM-DD or YYYYMMDD) and logical order.
    Defaults to today's date if user presses ENTER without input.
    """
    if force_single:
        date_opt = "Specific date"
        print("The report you selected only accepts a single date for reporting.")
        spec_date_input = input(
            "Enter the date (YYYY-MM-DD or YYYYMMDD) or press ENTER for today: "
        ).strip()
        spec_date = validate_date_input(spec_date_input, default_today=True)
        if spec_date:
            start_date = end_date = spec_date
            time_seg = "date"
            return date_opt, start_date, end_date, time_seg
    while True:
        print("Reporting time range:\n1. Specific date\n2. Range of dates\n")
        date_opt_input = input("Enter 1 or 2: ").strip()
        # --- specific date ---
        if date_opt_input == "1":
            date_opt = "Specific date"
            while True:
                spec_date_input = input(
                    "Enter the date (YYYY-MM-DD or YYYYMMDD) or press ENTER for today: "
                ).strip()
                spec_date = validate_date_input(spec_date_input, default_today=True)
                if spec_date:
                    start_date = end_date = spec_date
                    time_seg = "date"
                    print(
                        "Single date option selected, defaulting time segmentation to 'date'."
                    )
                    return date_opt, start_date, end_date, time_seg
        # --- date range ---
        elif date_opt_input == "2":
            date_opt = "Date range"
            while True:
                start_input = input("Start Date (YYYY-MM-DD or YYYYMMDD): ").strip()
                end_input = input("End Date (YYYY-MM-DD or YYYYMMDD): ").strip()
                start_val = validate_date_input(start_input, default_today=True)
                end_val = validate_date_input(end_input, default_today=True)
                if not (start_val and end_val):
                    continue  # invalid input, re-prompt
                start_dt = parse_supported_date(start_val)
                end_dt = parse_supported_date(end_val)
                if start_dt > end_dt:
                    print("Start date cannot be later than end date. Please re-enter.")
                    continue
                start_date = start_val
                end_date = end_val
                while True:
                    print(
                        "\nDate range segmentation:\n"
                        "1. Day\n"
                        "2. Week\n"
                        "3. Month\n"
                        "4. Quarter\n"
                        "5. Year\n"
                    )
                    time_seg_input = input(
                        "Select from one of the above numbered options (1-5): "
                    ).strip()
                    time_seg_options = {
                        "1": "date",
                        "2": "week",
                        "3": "month",
                        "4": "quarter",
                        "5": "year",
                    }
                    time_seg = time_seg_options.get(time_seg_input)
                    if time_seg:
                        return date_opt, start_date, end_date, time_seg
                    else:
                        print("Invalid segmentation option, please choose 1-5.")
        else:
            print("Invalid option, please enter 1 or 2.")


def validate_date_input(date_str, default_today=False):
    """Validate a date string and return it in the format provided by the user."""
    if not date_str:
        if default_today:
            today = date.today()
            today_str = today.strftime("%Y-%m-%d")
            print(f"No date entered. Defaulting to today's date: {today_str}")
            return today_str
        print(
            "Invalid date format. Please use YYYY-MM-DD or YYYYMMDD (e.g., 2025-03-14 or 20250314)."
        )
        return None
    try:
        parse_supported_date(date_str)
        return date_str
    except ValueError:
        print(
            "Invalid date format. Please use YYYY-MM-DD or YYYYMMDD (e.g., 2025-02-06 or 20250206)."
        )
        return None


def get_last30days():
    today_actual = date.today()
    start_date = today_actual - timedelta(days=30)
    end_date = today_actual - timedelta(days=1)
    time_seg = "date"
    date_opt = "Date range"
    return date_opt, start_date, end_date, time_seg


def get_last_calendar_month():
    today_actual = date.today()
    first_of_this_month = today_actual.replace(day=1)
    last_day_prev_month = first_of_this_month - timedelta(days=1)  # end_date
    first_day_prev_month = last_day_prev_month.replace(day=1)  # start_date
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
