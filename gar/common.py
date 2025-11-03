# -*- coding: utf-8 -*-
"""
Shared constants and utility helpers for CLI parsing, data handling, and reporting.

Any functions that need `prompts` do a local (lazy) import inside the function body.
"""

from __future__ import annotations

import argparse
import csv
import pydoc
import re
import sys
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any, Dict, Optional

from tabulate import tabulate

# -----------------------------
# Builtins monkey-patch for input "exit"
# -----------------------------


def _custom_input(prompt: str = "") -> str:
    """Wrap built-in input to allow 'exit' to quit gracefully."""
    user_input = _original_input(prompt)
    if user_input.lower() == "exit":
        print("Exiting the program.")
        sys.exit()
    return user_input


# Set __builtins__ module or a dictionary
if isinstance(__builtins__, dict):
    _original_input = __builtins__["input"]
    __builtins__["input"] = _custom_input
else:
    _original_input = __builtins__.input
    __builtins__.input = _custom_input


# -----------------------------
# Constants
# -----------------------------

PERFORMANCE_REPORT_OPTIONS = {
    "mac",
    "account",
    "ads",
    "clickview",
    "paid_organic_terms",
}

AUDIT_REPORT_OPTIONS = {
    "account_labels",
    "campaign_groups",
    "label_assignments",
}

BUDGET_REPORT_OPTIONS = {"budget"}

BUDGET_REPORT_MENU_OPTIONS = (("1", "Budget Report", "budget"),)

BUDGET_REPORT_MENU_LOOKUP = {
    option: report for option, _, report in BUDGET_REPORT_MENU_OPTIONS
}

REPORT_SCOPE_ALIASES = {
    "performance": "performance",
    "perf": "performance",
    "p": "performance",
    "auditing": "audit",
    "audit": "audit",
    "a": "audit",
    "budget": "budget",
    "budgets": "budget",
    "b": "budget",
}

REPORT_SCOPE_MENU_OPTIONS = (
    ("1", "Performance Reporting", "performance"),
    ("2", "Account Auditing", "audit"),
    ("3", "Budget Reporting", "budget"),
)

REPORT_SCOPE_MENU_LOOKUP = {
    option: scope for option, _, scope in REPORT_SCOPE_MENU_OPTIONS
}

REPORT_OPTION_ALIASES = {
    "mac": ("performance", "mac"),
    "account": ("performance", "account"),
    "accounts": ("performance", "account"),
    "ads": ("performance", "ads"),
    "ad": ("performance", "ads"),
    "clickview": ("performance", "clickview"),
    "click_view": ("performance", "clickview"),
    "gclid": ("performance", "clickview"),
    "paid_organic_terms": ("performance", "paid_organic_terms"),
    "paid-organic": ("performance", "paid_organic_terms"),
    "paidorganic": ("performance", "paid_organic_terms"),
    "account_labels": ("audit", "account_labels"),
    "labels": ("audit", "account_labels"),
    "campaign_groups": ("audit", "campaign_groups"),
    "campaign-group": ("audit", "campaign_groups"),
    "campaigns": ("audit", "campaign_groups"),
    "label_assignments": ("audit", "label_assignments"),
    "assignments": ("audit", "label_assignments"),
    "budget": ("budget", "budget"),
}

PERFORMANCE_REPORT_MENU_OPTIONS = (
    ("1", "MAC Report", "mac"),
    ("2", "Account Report", "account"),
    ("3", "Ads Report", "ads"),
    ("4", "GCLID/ClickView Report", "clickview"),
    ("5", "Paid and Organic Search Terms Report", "paid_organic_terms"),
)

PERFORMANCE_REPORT_MENU_LOOKUP = {
    option: report for option, _, report in PERFORMANCE_REPORT_MENU_OPTIONS
}

ACCOUNT_SCOPE_ALIASES = {
    "single": "single",
    "one": "single",
    "all": "all",
    "*": "all",
}

AUDIT_REPORT_MENU_OPTIONS = (
    ("1", "Account Labels List", "account_labels"),
    ("2", "Campaign Group List", "campaign_groups"),
    ("3", "Campaign and Ad Group Label Assignments", "label_assignments"),
)

AUDIT_REPORT_MENU_LOOKUP = {
    option: report for option, _, report in AUDIT_REPORT_MENU_OPTIONS
}

TIME_SEGMENT_ALIASES = {
    "day": "date",
    "date": "date",
    "daily": "date",
    "week": "week",
    "weekly": "week",
    "month": "month",
    "monthly": "month",
    "quarter": "quarter",
    "quarterly": "quarter",
    "year": "year",
    "yearly": "year",
}

OUTPUT_CHOICES = {"csv", "table", "auto"}

TOGGLE_INCLUDE_VALUES = {"include", "in", "yes", "y", "true", "1"}
TOGGLE_EXCLUDE_VALUES = {"exclude", "ex", "no", "n", "false", "0"}


# -----------------------------
# Formula helpers
# -----------------------------

MICROS_PER_UNIT = Decimal("1000000")


def micros_to_decimal(
    micros: Optional[int | str],
    quantize: Optional[Decimal] = None,
    rounding=ROUND_HALF_UP,
) -> Decimal:
    """Convert micro-units to Decimal without precision loss."""
    if micros in (None, ""):
        value = Decimal("0")
    else:
        value = Decimal(str(micros)) / MICROS_PER_UNIT
    if quantize is not None:
        return value.quantize(quantize, rounding=rounding)
    return value


# -----------------------------
# Console errors
# -----------------------------


def user_error(err_type: int) -> None:
    """Exit with a consistent user-facing error message."""
    if err_type == 1:
        sys.exit("Problem with MAIN loop.")
    if err_type == 2:
        sys.exit("Invalid input.")
    elif err_type in [3, 4]:
        sys.exit("Problem with output data.")


# -----------------------------
# Account selection / display helpers
# -----------------------------


def display_account_list(accounts_info: Dict[str, str]) -> tuple[str, str]:
    """Print accounts as a table and prompt for a selection."""
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
            table_data=account_table,
            headers=account_headers,
            auto_view=True,
        )
        selection = input(
            "\nSelect an account by number (1, 2, 3, etc.) or enter 'exit' to quit: "
        ).strip()
        if selection.isdigit():
            selection_i = int(selection)
            if 1 <= selection_i <= len(accounts_info):
                account_id = list(accounts_info.keys())[selection_i - 1]
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


def get_account_properties(accounts_info: Dict[str, str]) -> tuple[str, str]:
    """Prompt the user to select an account ID and name from a mapping."""
    print("\nSelect a account to report on:\n")
    account_id, account_name = display_account_list(accounts_info)
    print(
        f"Selected prop info:\naccount_name: {account_name}\naccount_id: {account_id}\n"
    )
    input("If correct, press ENTER to continue or input 'exit' to exit: ")
    return account_id, account_name


# -----------------------------
# Table / CSV display
# -----------------------------


def sanitize_filename(name: str) -> str:
    """Remove invalid characters from a filename string."""
    return re.sub(r'[<>:"/\\|?*]', "", name)


def save_csv(table_data, headers) -> None:
    """Persist table data to a CSV in the user's home directory."""
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

    file_path = Path.home() / file_name
    try:
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(table_data)
        print(f"\nData saved to: {file_path}\n")
    except Exception as e:
        print(f"\nFailed to save file: {e}\n")


def display_table(table_data, headers, auto_view: bool = False) -> None:
    """Render tabular data via 'tabulate'."""
    if auto_view:
        print(tabulate(table_data, headers, tablefmt="simple_grid"))
    else:
        input(
            "Report ready for viewing. Press ENTER to display results and 'Q' to exit output when done..."
        )
        pydoc.pager(tabulate(table_data, headers=headers, tablefmt="simple_grid"))


def data_handling_options(
    table_data,
    headers,
    auto_view: bool = False,
    preselected_output: Optional[str] = None,
) -> None:
    """Handle report output mode (CSV vs. table)."""
    if auto_view:
        if not table_data or not headers:
            print("No data to display.")
            return
        display_table(table_data, headers, auto_view=True)
        return

    report_view = preselected_output
    if not report_view:
        print(
            "How would you like to view the report?\n1. CSV\n2. Display table on screen\n"
        )
        report_view = input("Choose 1 or 2 ('exit' to exit): ").strip().lower()

    if report_view in ("1", "csv"):
        save_csv(table_data, headers)
    elif report_view in ("2", "table"):
        display_table(table_data, headers)
    elif report_view == "auto":
        display_table(table_data, headers, auto_view=True)
    else:
        print("Invalid input, please select one of the indicated options.")
        sys.exit(1)


# -----------------------------
# Small string transforms
# -----------------------------


def extract_mac(campaign_name: Optional[str]) -> str:
    """Extract MAC (suffix after the final colon) from a campaign name."""
    if not campaign_name or ":" not in campaign_name:
        return "UNDEFINED"
    mac = campaign_name.rsplit(":", 1)[-1].strip()
    return mac if mac else "UNDEFINED"


# -----------------------------
# Report/toggle options
# -----------------------------


def aggregate_channels() -> bool:
    """Prompt whether to aggregate channel types."""
    while True:
        print(
            "\nWould you like a detailed report that includes aggregates channel types? (Y)es or (N)o"
        )
        val = input("Please select Y or N: ").strip().lower()
        if val in ("y", "yes"):
            print("Channel types will be aggregated in the report.")
            return True
        if val in ("n", "no"):
            print("Channel types will NOT be aggregated in the report.")
            return False
        print("Invalid input, please select one of the indicated options (Y/N).")


def include_channel_types() -> bool:
    while True:
        print(
            "\nWould you like a detailed report that includes channel types? (Y)es or (N)o"
        )
        val = input("Please select Y or N: ").strip().lower()
        if val in ("y", "yes"):
            print("Channel types will be included in the report.")
            return True
        if val in ("n", "no"):
            print("Channel types will NOT be included in the report.")
            return False
        print("Invalid input, please select one of the indicated options (Y/N).")


def include_campaign_info() -> bool:
    while True:
        print(
            "\nWould you like a detailed report that includes campaign names and IDs? (Y)es or (N)o"
        )
        val = input("Please select Y or N: ").strip().lower()
        if val in ("y", "yes"):
            print("Campaign names and IDs will be included in the report.")
            return True
        if val in ("n", "no"):
            print("Campaign names and IDs will NOT be included in the report.")
            return False
        print("Invalid input, please select one of the indicated options (Y/N).")


def include_adgroup_info() -> bool:
    while True:
        print(
            "\nWould you like a detailed report that includes ad group names and IDs? (Y)es or (N)o"
        )
        val = input("Please select Y or N: ").strip().lower()
        if val in ("y", "yes"):
            print("Ad group names and IDs will be included in the report.")
            return True
        if val in ("n", "no"):
            print("Ad group names and IDs will NOT be included in the report.")
            return False
        print("Invalid input, please select one of the indicated options (Y/N).")


def include_device_info() -> bool:
    while True:
        print(
            "\nWould you like a detailed report that includes device types? (Y)es or (N)o"
        )
        val = input("Please select Y or N: ").strip().lower()
        if val in ("y", "yes"):
            print("Device types will be included in the report.")
            return True
        if val in ("n", "no"):
            print("Device types will NOT be included in the report.")
            return False
        print("Invalid input, please select one of the indicated options (Y/N).")


# -----------------------------
# PERFORMANCE_TOGGLE_CONFIG
# -----------------------------

PERFORMANCE_TOGGLE_CONFIG = {
    "include_channel_types": {
        "attr": "include_channel_type",
        "reports": {"mac", "ads", "clickview", "paid_organic_terms"},
        "prompt": include_channel_types,
        "label": "channel type segmentation",
        "cli_option": "--channel-types",
        "default": False,
    },
    "include_campaign_info": {
        "attr": "include_campaign_info",
        "reports": {"mac", "ads", "clickview", "paid_organic_terms"},
        "prompt": include_campaign_info,
        "label": "campaign metadata",
        "cli_option": "--campaign-info",
        "default": False,
    },
    "include_adgroup_info": {
        "attr": "include_adgroup_info",
        "reports": {"ads", "clickview", "paid_organic_terms"},
        "prompt": include_adgroup_info,
        "label": "ad group metadata",
        "cli_option": "--ad-group",
        "default": False,
    },
    "include_device_info": {
        "attr": "include_device_type",
        "reports": {"clickview", "paid_organic_terms"},
        "prompt": include_device_info,
        "label": "device segmentation",
        "cli_option": "--device",
        "default": False,
    },
}

PERFORMANCE_TOGGLE_FIELDS = tuple(
    config["attr"] for config in PERFORMANCE_TOGGLE_CONFIG.values()
)

AUDIT_OPTION_MAP = {
    "1": "account_labels",
    "2": "campaign_groups",
    "3": "label_assignments",
}

AUDIT_OPTION_DESCRIPTIONS = {
    "account_labels": "Account Labels Only Audit selected...",
    "campaign_groups": "Campaign Group Only Audit selected...",
    "label_assignments": "Campaign and Ad Group Label Assignments Audit selected...",
}


# -----------------------------
# Date parsing / ranges
# -----------------------------

SUPPORTED_DATE_FORMATS = ("%Y-%m-%d", "%Y%m%d")


def parse_supported_date(date_str: str) -> date:
    """Parse date string using supported formats."""
    for fmt in SUPPORTED_DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt).date()
        except (TypeError, ValueError):
            continue
    raise ValueError(f"Unsupported date format: {date_str}")


def validate_date_input(
    date_str: Optional[str], default_today: bool = False
) -> Optional[str]:
    """Validate a date string and normalize optional defaults."""
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


def get_last30days() -> tuple[str, date, date, str]:
    today_actual = date.today()
    start_date = today_actual - timedelta(days=30)
    end_date = today_actual - timedelta(days=1)
    return "Date range", start_date, end_date, "date"


def get_last_calendar_month() -> tuple[str, date, date, str]:
    today_actual = date.today()
    first_of_this_month = today_actual.replace(day=1)
    last_day_prev_month = first_of_this_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)
    return "Last calendar month", first_day_prev_month, last_day_prev_month, "month"


def get_quarter_dates(year: int, quarter: int) -> tuple[date, date]:
    if quarter not in (1, 2, 3, 4):
        raise ValueError("Quarter must be between 1 and 4")
    if quarter == 1:
        return date(year, 1, 1), date(year, 3, 31)
    if quarter == 2:
        return date(year, 4, 1), date(year, 6, 30)
    if quarter == 3:
        return date(year, 7, 1), date(year, 9, 30)
    return date(year, 10, 1), date(year, 12, 31)


def get_current_quarter_to_date() -> tuple[str, date, date, str]:
    today_actual = date.today()
    year = today_actual.year
    month = today_actual.month
    current_quarter = (month - 1) // 3 + 1
    q_start, _ = get_quarter_dates(year, current_quarter)
    start_date = q_start
    end_date = today_actual - timedelta(days=1)
    return "Date range", start_date, end_date, "quarter"


def get_previous_calendar_quarter() -> tuple[str, date, date, str]:
    today_actual = date.today()
    year = today_actual.year
    month = today_actual.month
    current_quarter = (month - 1) // 3 + 1
    if current_quarter == 1:
        prev_quarter = 4
        year -= 1
    else:
        prev_quarter = current_quarter - 1
    start_date, end_date = get_quarter_dates(year, prev_quarter)
    return "Date range", start_date, end_date, "quarter"


# -----------------------------
# CLI parsing transforms
# -----------------------------


def parse_toggle_choice(value: Any) -> bool:
    normalized = str(value).strip().lower()
    if normalized in TOGGLE_INCLUDE_VALUES:
        return True
    if normalized in TOGGLE_EXCLUDE_VALUES:
        return False
    raise argparse.ArgumentTypeError(
        "Toggle arguments accept 'include' or 'exclude' (case-insensitive)."
    )


def canonicalize_scope(raw_scope: Optional[str]) -> Optional[str]:
    if raw_scope is None:
        return None
    scope = REPORT_SCOPE_ALIASES.get(str(raw_scope).lower())
    if scope is None:
        raise ValueError(f"Unknown report scope: {raw_scope}")
    return scope


def canonicalize_option(
    raw_option: Optional[str], scope: Optional[str] = None
) -> tuple[Optional[str], Optional[str]]:
    if raw_option is None:
        return None, None
    option_entry = REPORT_OPTION_ALIASES.get(str(raw_option).lower())
    if option_entry is None:
        raise ValueError(f"Unknown report option: {raw_option}")
    option_scope, option = option_entry
    if scope and option_scope != scope:
        raise ValueError(
            f"Report option '{option}' is not available under the '{scope}' scope."
        )
    return option_scope, option


def parse_report_argument(
    argument: Optional[str],
) -> tuple[Optional[str], Optional[str]]:
    if not argument:
        return None, None
    parts = argument.split(":", 1)
    scope = canonicalize_scope(parts[0])
    option = None
    if len(parts) == 2 and parts[1]:
        _, option = canonicalize_option(parts[1], scope=scope)
    return scope, option


def normalize_account_id(account_id: Optional[str]) -> Optional[str]:
    if account_id is None:
        return None
    return "".join(ch for ch in str(account_id) if ch.isdigit())


def parse_account_argument(
    argument: Optional[str],
) -> tuple[Optional[str], Optional[str]]:
    if not argument:
        return None, None
    parts = argument.split(":", 1)
    scope_alias = parts[0].strip().lower()
    scope = ACCOUNT_SCOPE_ALIASES.get(scope_alias)
    if scope is None:
        raise ValueError(f"Unknown account scope: {argument}")
    account_id = None
    if scope == "single" and len(parts) == 2:
        account_id = normalize_account_id(parts[1])
    return scope, account_id


def parse_date_argument(
    argument: Optional[str], *, force_single: bool = False
) -> Optional[tuple[str, str, str, str]]:
    if not argument:
        return None
    raw_value = argument.strip()
    lower_value = raw_value.lower()

    if lower_value in {"last30", "last30days", "last_30", "last_30_days"}:
        date_opt, start_date, end_date, time_seg = get_last30days()
        return (
            date_opt,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            time_seg,
        )

    if lower_value in {"last_month", "lastcalendar", "last_calendar_month"}:
        date_opt, start_date, end_date, time_seg = get_last_calendar_month()
        return (
            date_opt,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            time_seg,
        )

    if ":" in raw_value:
        prefix, remainder = raw_value.split(":", 1)
    elif "=" in raw_value:
        prefix, remainder = raw_value.split("=", 1)
    else:
        prefix, remainder = "specific", raw_value

    prefix = prefix.strip().lower()
    remainder = remainder.strip()

    if prefix in {"specific", "single"}:
        parsed_date = parse_supported_date(remainder)
        iso_date = parsed_date.strftime("%Y-%m-%d")
        return ("Specific date", iso_date, iso_date, "date")

    if prefix == "range":
        if force_single:
            raise ValueError("The selected report only accepts a single date.")
        segments = [
            segment.strip() for segment in remainder.split(",") if segment.strip()
        ]
        if len(segments) < 2:
            raise ValueError(
                "Date range arguments must include start and end dates separated by commas."
            )
        start_val = parse_supported_date(segments[0])
        end_val = parse_supported_date(segments[1])
        if start_val > end_val:
            raise ValueError("Start date cannot be later than end date.")
        if len(segments) >= 3:
            seg_alias = TIME_SEGMENT_ALIASES.get(segments[2].lower())
            if seg_alias is None:
                raise ValueError(f"Unknown time segmentation: {segments[2]}")
            time_seg = seg_alias
        else:
            time_seg = "date"
        return (
            "Date range",
            start_val.strftime("%Y-%m-%d"),
            end_val.strftime("%Y-%m-%d"),
            time_seg,
        )

    # If only a bare date is provided, treat as specific date
    parsed_date = parse_supported_date(remainder or raw_value)
    iso_date = parsed_date.strftime("%Y-%m-%d")
    if force_single:
        return ("Specific date", iso_date, iso_date, "date")
    return ("Specific date", iso_date, iso_date, "date")


def determine_cli_mode(args) -> bool:
    return any(
        [
            args.report is not None,
            args.report_option_arg is not None,
            args.date is not None,
            args.account is not None,
            args.output is not None,
            args.include_channel_type is not None,
            args.include_campaign_info is not None,
            args.include_adgroup_info is not None,
            args.include_device_type is not None,
        ]
    )


# -----------------------------
# Resolvers (lazy-import prompts to avoid cycles)
# -----------------------------


def resolve_report_scope(cli_args) -> str:
    if getattr(cli_args, "report_scope", None):
        return cli_args.report_scope

    # lazy import to avoid circular import at module level
    from gar import prompts as _prompts

    while True:
        selection = _prompts.report_menu()
        scope = REPORT_SCOPE_MENU_LOOKUP.get(selection)
        if scope:
            cli_args.report_scope = scope
            return scope
        print("Invalid input, please select one of the indicated numbered options.")


def resolve_performance_option(cli_args) -> str:
    if getattr(cli_args, "report_option", None) in PERFORMANCE_REPORT_OPTIONS:
        return cli_args.report_option

    from gar import prompts as _prompts

    report_option = _prompts.report_opt_prompt()
    cli_args.report_option = report_option
    return report_option


def resolve_audit_option(cli_args) -> str:
    if getattr(cli_args, "report_option", None) in AUDIT_REPORT_OPTIONS:
        return cli_args.report_option

    from gar import prompts as _prompts

    while True:
        selection = _prompts.audit_opt_prompt()
        option = AUDIT_OPTION_MAP.get(selection)
        if option:
            cli_args.report_option = option
            return option
        print("Invalid option. Please try again.")


def resolve_budget_option(cli_args) -> str:
    if getattr(cli_args, "report_option", None) in BUDGET_REPORT_OPTIONS:
        return cli_args.report_option

    from gar import prompts as _prompts

    report_option = _prompts.budget_opt_prompt()
    cli_args.report_option = report_option
    return report_option


def resolve_performance_toggles(cli_args, report_option: str) -> Dict[str, bool]:
    toggles: Dict[str, bool] = {}
    ignored_cli_arguments = []
    provided_fields = getattr(cli_args, "provided_toggle_fields", set())

    for toggle_name, config in PERFORMANCE_TOGGLE_CONFIG.items():
        attr_name = config["attr"]
        allowed_reports = config["reports"]
        current_value = getattr(cli_args, attr_name, None)

        if report_option not in allowed_reports:
            if attr_name in provided_fields:
                ignored_cli_arguments.append(config["cli_option"])
            continue

        if current_value is None:
            if getattr(cli_args, "cli_mode", False):
                resolved_value = config.get("default", False)
            else:
                resolved_value = config["prompt"]()
            setattr(cli_args, attr_name, resolved_value)
        else:
            resolved_value = current_value

        toggles[toggle_name] = resolved_value

    if ignored_cli_arguments and getattr(cli_args, "cli_mode", False):
        formatted = ", ".join(sorted(ignored_cli_arguments))
        print(
            "Note: The following toggle arguments are not applicable to this "
            f"report option and were ignored: {formatted}"
        )

    return toggles


def resolve_date_details(cli_args, *, force_single: bool):
    if getattr(cli_args, "date_details", None):
        return cli_args.date_details
    if cli_args.date:
        try:
            date_details = parse_date_argument(cli_args.date, force_single=force_single)
        except ValueError as exc:
            print(f"Invalid --date argument: {exc}")
            sys.exit(1)
        if date_details is None:
            print("The --date argument did not resolve to a valid range.")
            sys.exit(1)
    else:
        # lazy import to avoid cycle (prompts -> common -> prompts)
        from gar import (
            prompts as _prompts,  # noqa: F401  (used indirectly via get_timerange)
        )

        date_details = get_timerange(force_single=force_single)
    if date_details is None:
        print("Failed to resolve a reporting date range.")
        sys.exit(1)
    cli_args.date_details = date_details
    return date_details


def resolve_output_preference(cli_args) -> str:
    if getattr(cli_args, "output_mode", None):
        return cli_args.output_mode
    if cli_args.output:
        cli_args.output_mode = cli_args.output
        return cli_args.output_mode

    from gar import prompts as _prompts

    output_mode = _prompts.output_prompt()
    cli_args.output_mode = output_mode
    return output_mode


def resolve_account_scope(cli_args, customer_dict: Dict[str, str]):
    if getattr(cli_args, "account_scope", None):
        scope = cli_args.account_scope
        if scope == "single" and cli_args.account_id:
            account_id = cli_args.account_id
            account_name = customer_dict.get(account_id)
            if account_name:
                return scope, account_id, account_name
            print(
                f"Configured account ID {account_id} not found. Returning to account selection."
            )

    if getattr(cli_args, "account_scope_cli", None):
        scope = cli_args.account_scope_cli
        account_id = cli_args.account_id_cli
        if scope == "all":
            cli_args.account_scope = "all"
            cli_args.account_id = None
            cli_args.account_name = None
            return "all", None, None
        if scope == "single" and account_id:
            normalized_id = normalize_account_id(account_id)
            if normalized_id is None:
                print(
                    f"Account ID {account_id} is not in a valid format. Prompting for selection."
                )
            else:
                account_name = customer_dict.get(normalized_id)
                if account_name:
                    cli_args.account_scope = "single"
                    cli_args.account_id = normalized_id
                    cli_args.account_name = account_name
                    return "single", normalized_id, account_name
                print(
                    f"Account ID {account_id} not found in accessible accounts. Prompting for selection."
                )
        # fallthrough to prompts

    from gar import prompts as _prompts

    scope = _prompts.account_scope_prompt()
    cli_args.account_scope = scope
    if scope == "single":
        account_id, account_name = get_account_properties(customer_dict)
        cli_args.account_id = account_id
        cli_args.account_name = account_name
        return scope, account_id, account_name
    cli_args.account_id = None
    cli_args.account_name = None
    return scope, None, None


def maybe_print_configuration_summary(
    cli_args,
    *,
    report_scope,
    report_option,
    date_details,
    output_mode,
    account_scope,
    account_id,
    toggles: Dict[str, bool],
) -> None:
    if not getattr(cli_args, "cli_mode", False) or getattr(cli_args, "debug", False):
        return

    print("\nResolved configuration:")
    print(f"  Report scope: {report_scope}")
    print(f"  Report option: {report_option}")
    if date_details:
        date_opt, start_date, end_date, time_seg = date_details
        print(f"  Date option: {date_opt}")
        print(f"  Start date: {start_date}")
        print(f"  End date: {end_date}")
        print(f"  Time segmentation: {time_seg}")
    if output_mode:
        print(f"  Output preference: {output_mode}")
    print(f"  Account scope: {account_scope}")
    if account_scope == "single" and account_id:
        print(f"  Account ID: {account_id}")
    for key, value in toggles.items():
        print(f"  {key}: {value}")
    print()


def get_timerange(
    force_single: bool = False,
) -> tuple[str, str | date, str | date, str]:
    """Prompt for a single date or range, with validation."""
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
        # specific date
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
        # range
        elif date_opt_input == "2":
            date_opt = "Date range"
            while True:
                start_input = input("Start Date (YYYY-MM-DD or YYYYMMDD): ").strip()
                end_input = input("End Date (YYYY-MM-DD or YYYYMMDD): ").strip()
                start_val = validate_date_input(start_input, default_today=True)
                end_val = validate_date_input(end_input, default_today=True)
                if not (start_val and end_val):
                    continue
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
                    print("Invalid segmentation option, please choose 1-5.")
        else:
            print("Invalid option, please enter 1 or 2.")
