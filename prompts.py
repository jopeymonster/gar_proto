# -*- coding: utf-8 -*-

# menu prompts
def report_menu():
    print("Main Menu - Select from the options below:\n"
          "1. Performance Reporting\n"
          "2. Account Auditing\n"
          "3. Budget Reporting\n")
    report_scope = input("Choose a numbered option (1, 2, etc or 'exit' to exit): ").strip()
    return str(report_scope)

def report_opt_prompt():
    print("Reporting Options:\n"
        "1. ARC Report\n"
        "2. Account Report\n"
        "3. Ads Report\n"
        "4. GCLID/ClickView Report\n"
        # "X. Test Query\n"
        "Or type 'exit' at any prompt to quit immediately.\n")
    report_opt = input("Choose a numbered option (1, 2, etc or 'exit' to exit): ")
    return str(report_opt)

def audit_opt_prompt():
    print("Auditing Options:\n"
        "1. Account Labels List\n"
        "2. Campaign Group List\n"
        "3. Campaign and Ad Group Label Assignments\n"
        "Or type 'exit' at any prompt to quit immediately.\n")
    audit_opt = input("Choose 1, 2, 3, 4, etc ('exit' to exit): ")
    return audit_opt

def account_scope_prompt():
    while True:
        print("Generate a report for a single account or all accounts?\n"
              "1. Select a single account\n"
              "2. All accounts\n")
        account_scope_input = input("Choose a numbered option (1, 2, etc or 'exit' to exit): ").strip()
        if account_scope_input == '1':
            return 'single'
        elif account_scope_input == '2':
            return 'all'
        else:
            print("Invalid selection. Please enter 'Y' or 'N'.")

def budget_opt_prompt():
    print("Budget Options:\n"
          "1. Budget Report\n"
          # "2. Budget Report\n"
          "Or type 'exit' at any prompt to quit immediately.\n")
    budget_opt_input = input("Choose a numbered option (1, 2, etc or 'exit' to exit): ").strip()
    return str(budget_opt_input)

# timer
def execution_time(start_time, end_time):
    print(f"\nReport compiled - Execution time: {end_time - start_time:.2f} seconds\n")

# debugs
def datetime_debug(account_scope, date_opt, start_date, end_date, time_seg):
    print("\nServices params passback after prompts:\n"
        f"account_scope: {account_scope}\n"
        f"date_opt: {date_opt}\n"
        f"time_seg: {time_seg}\n"
        f"start_date: {start_date}\n"
        f"end_date: {end_date}\n")
        # f"time_condition: {time_condition}")
    input("\nPause for debug - press ENTER to continue or input 'exit' to exit: ")
    return

def arc_debug(account_scope, date_opt, start_date, end_date, time_seg, include_channel_types):
    print("\nServices params passback after prompts:\n"
        f"account_scope: {account_scope}\n"
        f"date_opt: {date_opt}\n"
        f"time_seg: {time_seg}\n"
        f"start_date: {start_date}\n"
        f"end_date: {end_date}\n"
        f"include_channel_types: {include_channel_types}")
        # f"time_condition: {time_condition}")
    input("\nPause for debug - press ENTER to continue or input 'exit' to exit: ")
    return