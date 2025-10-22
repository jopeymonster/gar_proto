# -*- coding: utf-8 -*-
import helpers

# menu prompts
def report_menu():
    print("Main Menu - Select from the options below:\n"
          "1. Performance Reporting\n"
          "2. Account Auditing\n"
          "3. Budget Reporting\n")
    report_scope = input("Choose a numbered option (1, 2, etc or 'exit' to exit): ").strip()
    return str(report_scope)

def report_opt_prompt():
    report_opt_list = ['arc','account','ads','clickview','paid_organic_terms']
    while True:
        print("Reporting Options:\n"
            "1. ARC Report\n"
            "2. Account Report\n"
            "3. Ads Report\n"
            "4. GCLID/ClickView Report\n"
            "5. Paid and Organic Search Terms Report\n"
            # "X. Test Query\n"
            "Or type 'exit' at any prompt to quit immediately.\n")
        report_opt_input = input("Choose a numbered option (1, 2, etc or 'exit' to exit): ")
        if report_opt_input in ['1','2','3','4','5']:
            index_choice = int(report_opt_input)-1 # convert input to int and shift to 0-index
            return report_opt_list[index_choice]
        else:
            print("Invalid option. Please try again.")

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
    budget_opt_list = ['budget',]
    while True:
        print("Budget Report Options:\n"
            "1. Budget Report\n"
            # "2. Budget Report\n"
            "Or type 'exit' at any prompt to quit immediately.\n")
        budget_opt_input = input("Choose a numbered option (1, 2, etc or 'exit' to exit): ")
        if budget_opt_input in ['1','2','3','4','5']:
            index_choice = int(budget_opt_input)-1 # convert input to int and shift to 0-index
            return budget_opt_list[index_choice]
        else:
            print("Invalid option. Please try again.")

def report_details_prompt(report_opt):
    if report_opt == 'clickview':
        report_date_details = helpers.get_timerange(force_single=True)
    else:
        report_date_details = helpers.get_timerange(force_single=False)
    date_opt, start_date, end_date, time_seg = report_date_details
    account_scope = account_scope_prompt() # returns 'single' or 'all'
    report_details = (
        date_opt,
        start_date,
        end_date,
        time_seg,
        account_scope
        )
    return report_details

# timer
def execution_time(start_time, end_time):
    print(f"\nReport compiled - Execution time: {end_time - start_time:.2f} seconds\n")

# debugs
def data_review(report_details, **toggles):
        """
        Report prompt tuple positioning:
        0. date_opt
        1. start_date
        2. end_date
        3. time_seg
        4. account_scope
        toggles:
         - include_channel_types
         - include_campaign
         - include_adgroup
         - include_device
         - aggregate_channels
        """
        date_opt, start_date, end_date, time_seg, account_scope = report_details
        # all report options
        print("\nServices params passback after prompts:\n"
              f"account_scope: {account_scope}\n"
              f"date_opt: {date_opt}\n"
              f"time_seg: {time_seg}\n"
              f"start_date: {start_date}\n"
              f"end_date: {end_date}")
        # specified options
        for key, value in toggles.items():
            print(f"{key}: {value}")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit: ")
        return