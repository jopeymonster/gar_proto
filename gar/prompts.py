# -*- coding: utf-8 -*-
"""User-facing prompts for interacting with the Google Ads Reporter."""

from gar import common


# menu prompts
def report_menu():
    """Prompt the user to select the high-level report category.

    Returns:
        str: Raw string selection provided by the user.
    """

    print("Main Menu - Select from the options below:\n")
    for option, label, _ in common.REPORT_SCOPE_MENU_OPTIONS:
        print(f"{option}. {label}")
    report_scope = input(
        "Choose a numbered option (1, 2, etc or 'exit' to exit): "
    ).strip()
    return str(report_scope)


def report_opt_prompt():
    """Prompt the user to choose a performance reporting option.

    Returns:
        str: Keyword describing the selected report type.
    """

    while True:
        print("Reporting Options:\n")
        for option, label, _ in common.PERFORMANCE_REPORT_MENU_OPTIONS:
            print(f"{option}. {label}")
        print("Or type 'exit' at any prompt to quit immediately.\n")
        print(
            "NOTE: The 'Campaign Type' report summarizes spend by advertising "
            "channel and always includes channel segmentation. MAC values can "
            "be toggled for reports that contain campaign names.\n"
        )
        report_opt_input = input(
            "Choose a numbered option (1, 2, etc or 'exit' to exit): "
        ).strip()
        if report_opt_input in common.PERFORMANCE_REPORT_MENU_LOOKUP:
            return common.PERFORMANCE_REPORT_MENU_LOOKUP[report_opt_input]
        else:
            print("Invalid option. Please try again.")


def audit_opt_prompt():
    """Prompt the user to select an auditing workflow.

    Returns:
        str: Raw string selection from the auditing menu.
    """

    print("Auditing Options:\n")
    for option, label, _ in common.AUDIT_REPORT_MENU_OPTIONS:
        print(f"{option}. {label}")
    print("Or type 'exit' at any prompt to quit immediately.\n")
    audit_opt = input("Choose 1, 2, 3, 4, etc ('exit' to exit): ")
    return audit_opt


def account_scope_prompt():
    """Prompt the user to choose between single-account or all-account scope.

    Returns:
        str: "single" or "all" based on the selection.
    """

    while True:
        print(
            "Generate a report for a single account or all accounts?\n"
            "1. Select a single account\n"
            "2. All accounts\n"
        )
        account_scope_input = input(
            "Choose a numbered option (1, 2, etc or 'exit' to exit): "
        ).strip()
        if account_scope_input == "1":
            return "single"
        elif account_scope_input == "2":
            return "all"
        else:
            print("Invalid selection. Please enter 'Y' or 'N'.")


def budget_opt_prompt():
    """Prompt the user for available budget reporting options.

    Returns:
        str: Keyword describing the chosen budget report type.
    """

    while True:
        print("Budget Report Options:\n")
        for option, label, _ in common.BUDGET_REPORT_MENU_OPTIONS:
            print(f"{option}. {label}")
        print("Or type 'exit' at any prompt to quit immediately.\n")
        budget_opt_input = input(
            "Choose a numbered option (1, 2, etc or 'exit' to exit): "
        ).strip()
        if budget_opt_input in common.BUDGET_REPORT_MENU_LOOKUP:
            return common.BUDGET_REPORT_MENU_LOOKUP[budget_opt_input]
        else:
            print("Invalid option. Please try again.")


def report_details_prompt(report_opt):
    """Collect the full reporting context for the selected report option.

    Args:
        report_opt (str): Report option keyword.

    Returns:
        tuple[str, str, str, str, str]: Date description, start date, end date,
        time segmentation, and account scope.
    """

    if report_opt == "clickview":
        report_date_details = common.get_timerange(force_single=True)
    else:
        report_date_details = common.get_timerange(force_single=False)
    date_opt, start_date, end_date, time_seg = report_date_details
    account_scope = account_scope_prompt()  # returns 'single' or 'all'
    report_details = (date_opt, start_date, end_date, time_seg, account_scope)
    return report_details


# timer
def execution_time(start_time, end_time):
    """Display the elapsed time for a report.

    Args:
        start_time (float): Start timestamp from 'time.time'.
        end_time (float): End timestamp from 'time.time'.

    Returns:
        None: Output is written directly to stdout.
    """

    print(f"\nReport compiled - Execution time: {end_time - start_time:.2f} seconds\n")


# debugs
def data_review(report_details, *, debug=False, **toggles):
    """Display the collected prompt inputs for debugging purposes.

    Args:
        report_details (tuple): Tuple containing date description, start date,
            end date, time segmentation, and account scope.
        debug (bool): Flag indicating whether debug output should be emitted.
        **toggles: Keyword arguments representing additional configuration
            flags selected by the user.

    Returns:
        None: The function only prints debugging information when 'debug' is
        'True'.
    """

    if not debug:
        return

    date_opt, start_date, end_date, time_seg, account_scope = report_details
    print(
        "\nServices params passback after prompts:\n"
        f"account_scope: {account_scope}\n"
        f"date_opt: {date_opt}\n"
        f"time_seg: {time_seg}\n"
        f"start_date: {start_date}\n"
        f"end_date: {end_date}"
    )
    for key, value in toggles.items():
        print(f"{key}: {value}")
    input("\nPause for debug - press ENTER to continue or input 'exit' to exit: ")
    return


def output_prompt():
    """Prompt the user to choose how report results should be reviewed.

    Returns:
        str: Keyword describing the selected output handling option.
    """

    output_options = {
        "1": "csv",
        "2": "table",
        "3": "auto",
    }
    while True:
        print(
            "Output handling options:\n"
            "1. Save to CSV\n"
            "2. Display table on screen\n"
            "3. Auto-display results without additional prompts\n"
        )
        selection = input("Choose a numbered option (1-3 or 'exit' to exit): ").strip()
        choice = output_options.get(selection)
        if choice:
            return choice
        print("Invalid option. Please try again.")
