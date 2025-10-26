# -*- coding: utf-8 -*-
"""Command-line entry points for the Google Ads Reporter prototype."""

import argparse
import sys
import time
from textwrap import dedent

import consts
import helpers
import prompts
import services


def parse_toggle_choice(value):
    normalized = str(value).strip().lower()
    if normalized in consts.TOGGLE_INCLUDE_VALUES:
        return True
    if normalized in consts.TOGGLE_EXCLUDE_VALUES:
        return False
    raise argparse.ArgumentTypeError(
        "Toggle arguments accept 'include' or 'exclude' (case-insensitive)."
    )


def canonicalize_scope(raw_scope):
    if raw_scope is None:
        return None
    scope = consts.REPORT_SCOPE_ALIASES.get(str(raw_scope).lower())
    if scope is None:
        raise ValueError(f"Unknown report scope: {raw_scope}")
    return scope


def canonicalize_option(raw_option, scope=None):
    if raw_option is None:
        return None, None
    option_entry = consts.REPORT_OPTION_ALIASES.get(str(raw_option).lower())
    if option_entry is None:
        raise ValueError(f"Unknown report option: {raw_option}")
    option_scope, option = option_entry
    if scope and option_scope != scope:
        raise ValueError(
            f"Report option '{option}' is not available under the '{scope}' scope."
        )
    return option_scope, option


def parse_report_argument(argument):
    if not argument:
        return None, None
    parts = argument.split(":", 1)
    scope = canonicalize_scope(parts[0])
    option = None
    if len(parts) == 2 and parts[1]:
        _, option = canonicalize_option(parts[1], scope=scope)
    return scope, option


def normalize_account_id(account_id):
    if account_id is None:
        return None
    return "".join(ch for ch in str(account_id) if ch.isdigit())


def parse_account_argument(argument):
    if not argument:
        return None, None
    parts = argument.split(":", 1)
    scope_alias = parts[0].strip().lower()
    scope = consts.ACCOUNT_SCOPE_ALIASES.get(scope_alias)
    if scope is None:
        raise ValueError(f"Unknown account scope: {argument}")
    account_id = None
    if scope == "single" and len(parts) == 2:
        account_id = normalize_account_id(parts[1])
    return scope, account_id


def parse_date_argument(argument, *, force_single=False):
    if not argument:
        return None
    raw_value = argument.strip()
    lower_value = raw_value.lower()
    if lower_value in {"last30", "last30days", "last_30", "last_30_days"}:
        date_opt, start_date, end_date, time_seg = helpers.get_last30days()
        return (
            date_opt,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            time_seg,
        )
    if lower_value in {"last_month", "lastcalendar", "last_calendar_month"}:
        date_opt, start_date, end_date, time_seg = helpers.get_last_calendar_month()
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
        parsed_date = helpers.parse_supported_date(remainder)
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
        start_val = helpers.parse_supported_date(segments[0])
        end_val = helpers.parse_supported_date(segments[1])
        if start_val > end_val:
            raise ValueError("Start date cannot be later than end date.")
        if len(segments) >= 3:
            seg_alias = consts.TIME_SEGMENT_ALIASES.get(segments[2].lower())
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

    # If only a bare date is provided, treat it as a specific date.
    parsed_date = helpers.parse_supported_date(remainder or raw_value)
    iso_date = parsed_date.strftime("%Y-%m-%d")
    if force_single:
        return ("Specific date", iso_date, iso_date, "date")
    return ("Specific date", iso_date, iso_date, "date")


def determine_cli_mode(args):
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


def resolve_report_scope(cli_args):
    if getattr(cli_args, "report_scope", None):
        return cli_args.report_scope

    scope_map = {"1": "performance", "2": "audit", "3": "budget"}
    while True:
        selection = prompts.report_menu()
        scope = scope_map.get(selection)
        if scope:
            cli_args.report_scope = scope
            return scope
        print("Invalid input, please select one of the indicated numbered options.")


def resolve_performance_option(cli_args):
    if getattr(cli_args, "report_option", None) in consts.PERFORMANCE_REPORT_OPTIONS:
        return cli_args.report_option
    report_option = prompts.report_opt_prompt()
    cli_args.report_option = report_option
    return report_option


def resolve_audit_option(cli_args):
    if getattr(cli_args, "report_option", None) in consts.AUDIT_REPORT_OPTIONS:
        return cli_args.report_option
    while True:
        selection = prompts.audit_opt_prompt()
        option = consts.AUDIT_OPTION_MAP.get(selection)
        if option:
            cli_args.report_option = option
            return option
        print("Invalid option. Please try again.")


def resolve_budget_option(cli_args):
    if getattr(cli_args, "report_option", None) in consts.BUDGET_REPORT_OPTIONS:
        return cli_args.report_option
    report_option = prompts.budget_opt_prompt()
    cli_args.report_option = report_option
    return report_option


def resolve_performance_toggles(cli_args, report_option):
    toggles = {}
    ignored_cli_arguments = []
    provided_fields = getattr(cli_args, "provided_toggle_fields", set())

    for toggle_name, config in consts.PERFORMANCE_TOGGLE_CONFIG.items():
        attr_name = config["attr"]
        allowed_reports = config["reports"]
        current_value = getattr(cli_args, attr_name, None)

        if report_option not in allowed_reports:
            if attr_name in provided_fields:
                ignored_cli_arguments.append(config["cli_option"])
            continue

        if current_value is None:
            if cli_args.cli_mode:
                resolved_value = config.get("default", False)
            else:
                resolved_value = config["prompt"]()
            setattr(cli_args, attr_name, resolved_value)
        else:
            resolved_value = current_value

        toggles[toggle_name] = resolved_value

    if ignored_cli_arguments and cli_args.cli_mode:
        formatted = ", ".join(sorted(ignored_cli_arguments))
        print(
            "Note: The following toggle arguments are not applicable to this "
            f"report option and were ignored: {formatted}"
        )

    return toggles


def resolve_date_details(cli_args, *, force_single):
    if getattr(cli_args, "date_details", None):
        return cli_args.date_details
    if cli_args.date:
        try:
            date_details = parse_date_argument(cli_args.date, force_single=force_single)
        except ValueError as exc:
            print(f"Invalid --date argument: {exc}")
            sys.exit(1)
    else:
        date_details = helpers.get_timerange(force_single=force_single)
    cli_args.date_details = date_details
    return date_details


def resolve_output_preference(cli_args):
    if getattr(cli_args, "output_mode", None):
        return cli_args.output_mode
    if cli_args.output:
        cli_args.output_mode = cli_args.output
        return cli_args.output_mode
    output_mode = prompts.output_prompt()
    cli_args.output_mode = output_mode
    return output_mode


def resolve_account_scope(cli_args, customer_dict):
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
            account_name = customer_dict.get(normalized_id)
            if account_name:
                cli_args.account_scope = "single"
                cli_args.account_id = normalized_id
                cli_args.account_name = account_name
                return "single", normalized_id, account_name
            print(
                f"Account ID {account_id} not found in accessible accounts. Prompting for selection."
            )
        # scope was single but no ID provided; fall back to prompts below

    scope = prompts.account_scope_prompt()
    cli_args.account_scope = scope
    if scope == "single":
        account_id, account_name = helpers.get_account_properties(customer_dict)
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
    toggles,
):
    if not cli_args.cli_mode or cli_args.debug:
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


def build_parser():
    parser = argparse.ArgumentParser(
        prog="google-ads-reporter",
        description=dedent(
            """
            Run Google Ads performance, audit, and budget reports via the command line.

            Combine CLI arguments with the interactive workflow to pre-select options
            such as report scope, date ranges, output handling, and additional data
            toggles. Arguments default to the standard interactive prompts when
            omitted.
            """
        ).strip(),
        epilog=dedent(
            """
            Examples:
              python main.py --report performance:arc --date last30 --output csv --account single:1234567890
              python main.py --report performance:ads --channel-types include --ad-group include --date specific:2024-01-15
              python main.py --report audit --report-option account_labels --account all --debug
            """
        ).strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-y",
        "--yaml",
        dest="yaml",
        help="Path to a YAML config file containing OAuth or Service Account credentials.",
    )
    parser.add_argument(
        "--report",
        help="Report scope (performance, audit, budget) optionally followed by ':<option>'.",
    )
    parser.add_argument(
        "--report-option",
        dest="report_option_arg",
        help="Explicit report option (e.g., arc, account, account_labels).",
    )
    parser.add_argument(
        "--date",
        help=(
            "Date configuration. Examples: 'specific:2024-01-15', "
            "'range:2024-01-01,2024-01-31,month', 'last30days'."
        ),
    )
    parser.add_argument(
        "--account",
        help="Account scope ('single' or 'all'), optionally with an ID (e.g., single:1234567890).",
    )
    parser.add_argument(
        "--output",
        choices=sorted(consts.OUTPUT_CHOICES),
        help="Preferred output handling for report data (csv, table, or auto).",
    )
    parser.add_argument(
        "--channel-types",
        "--channel_types",
        "--channel",
        dest="include_channel_type",
        type=parse_toggle_choice,
        metavar="{include,exclude}",
        help=(
            "Include or exclude channel type segmentation (default: exclude when not "
            "specified)."
        ),
    )
    parser.add_argument(
        "--campaign-info",
        "--campaign",
        dest="include_campaign_info",
        type=parse_toggle_choice,
        metavar="{include,exclude}",
        help=(
            "Include or exclude campaign metadata in supported reports (default: "
            "exclude when not specified)."
        ),
    )
    parser.add_argument(
        "--ad-group",
        "--ad_group",
        dest="include_adgroup_info",
        type=parse_toggle_choice,
        metavar="{include,exclude}",
        help=(
            "Include or exclude ad group metadata in supported reports (default: "
            "exclude when not specified)."
        ),
    )
    parser.add_argument(
        "--device",
        "--device-type",
        "--device_types",
        dest="include_device_type",
        type=parse_toggle_choice,
        metavar="{include,exclude}",
        help=(
            "Include or exclude device segmentation in supported reports (default: "
            "exclude when not specified)."
        ),
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug prompts before executing requests.",
    )
    return parser


def normalize_cli_args(parser, args):
    args.report_scope = None
    args.report_option = None
    args.account_scope_cli = None
    args.account_id_cli = None
    args.account_scope = None
    args.account_id = None
    args.account_name = None
    args.date_details = None
    args.output_mode = args.output

    try:
        scope_from_report, option_from_report = parse_report_argument(args.report)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    args.report_scope = scope_from_report
    args.report_option = option_from_report

    if args.report_option_arg:
        try:
            option_scope, option_value = canonicalize_option(
                args.report_option_arg, scope=args.report_scope
            )
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        if args.report_option and args.report_option != option_value:
            raise ValueError("Conflicting report options specified.")
        args.report_option = option_value
        if args.report_scope and args.report_scope != option_scope:
            raise ValueError(
                f"Report option '{args.report_option_arg}' is not valid for the '{args.report_scope}' scope."
            )
        if not args.report_scope:
            args.report_scope = option_scope

    try:
        account_scope, account_id = parse_account_argument(args.account)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    args.account_scope_cli = account_scope
    args.account_id_cli = account_id

    args.cli_mode = determine_cli_mode(args)
    args.provided_toggle_fields = {
        field
        for field in consts.PERFORMANCE_TOGGLE_FIELDS
        if getattr(args, field, None) is not None
    }
    return args


# MENUS
def init_menu(cli_args):
    """Start the interactive reporter experience.

    The function authenticates against the Google Ads API, displays the
    available accounts to the user, and transitions into the primary menu.

    Args:
        cli_args (argparse.Namespace): Parsed command-line arguments that may
            pre-populate portions of the workflow.

    Returns:
        None: Control flow continues into the menu loop.
    """

    print(
        "\nGoogle Ads Reporter, developed by JDT using GAds API and gRPC\n"
        "NOTE: Enter 'exit' at any prompt will exit this reporting tool."
    )
    if not cli_args.cli_mode:
        input("Press Enter When Ready...")
    print("Authorization in progress...")
    gads_service, customer_service, client = services.generate_services(cli_args.yaml)
    print("Authorization complete!\n")
    print("Retrieving account information...")
    full_accounts_info = services.get_accounts(gads_service, customer_service, client)
    customer_list, account_headers, customer_dict, num_accounts = full_accounts_info
    print(
        "\nAccount information retrieved successfully!\n"
        f"Number of accounts found: {num_accounts}\n"
    )
    helpers.data_handling_options(
        table_data=customer_list, headers=account_headers, auto_view=True
    )
    main_menu(gads_service, client, full_accounts_info, cli_args)


def main_menu(gads_service, client, full_accounts_info, cli_args):
    """Route the user to the appropriate reporting menu.

    Args:
        gads_service (GoogleAdsService): The authenticated Google Ads
            service used for reporting queries.
        client (GoogleAdsClient): The authenticated client instance used to
            generate additional services.
        full_accounts_info (tuple[list[list[str]], list[str], dict[str, str], int]):
            Tuple containing the tabular account listing, column headers, the
            mapping of customer IDs to names, and the number of accounts.
        cli_args (argparse.Namespace): Parsed CLI arguments guiding the flow.

    Returns:
        None: Control flow continues into downstream menus.
    """

    report_scope = resolve_report_scope(cli_args)
    if report_scope == "performance":
        print("\nPerformance Reporting selected.\n")
        performance_menu(gads_service, client, full_accounts_info, cli_args)
    elif report_scope == "audit":
        print("\nAccount Auditing selected.\n")
        audit_menu(gads_service, client, full_accounts_info, cli_args)
    elif report_scope == "budget":
        print("\nBudget Reporting selected.\n")
        budget_menu(gads_service, client, full_accounts_info, cli_args)
    else:
        print("Invalid input, please select one of the indicated numbered options.")
        sys.exit(1)


def performance_menu(gads_service, client, full_accounts_info, cli_args):
    """Display and execute performance-related report options.

    Args:
        gads_service (GoogleAdsService): The Google Ads service used for
            query execution.
        client (GoogleAdsClient): Authenticated Google Ads client instance.
        full_accounts_info (tuple[list[list[str]], list[str], dict[str, str], int]):
            Tuple with account table data, display headers, account lookup
            dictionary, and the number of available accounts.
        cli_args (argparse.Namespace): Parsed CLI arguments guiding the flow.

    Returns:
        None: Data is processed and passed to downstream helpers.
    """

    customer_list, account_headers, customer_dict, num_accounts = full_accounts_info
    report_opt = resolve_performance_option(cli_args)

    print(f"{report_opt.replace('_', ' ').title()} report selected...")

    toggles = resolve_performance_toggles(cli_args, report_opt)
    force_single_date = report_opt == "clickview"
    date_opt, start_date, end_date, time_seg = resolve_date_details(
        cli_args, force_single=force_single_date
    )
    output_mode = resolve_output_preference(cli_args)
    account_scope, account_id, account_name = resolve_account_scope(
        cli_args, customer_dict
    )

    report_details = (date_opt, start_date, end_date, time_seg, account_scope)
    prompts.data_review(report_details, debug=cli_args.debug, **toggles)
    maybe_print_configuration_summary(
        cli_args,
        report_scope="performance",
        report_option=report_opt,
        date_details=(date_opt, start_date, end_date, time_seg),
        output_mode=output_mode,
        account_scope=account_scope,
        account_id=account_id,
        toggles=toggles,
    )

    single_dispatch = {
        "arc": services.arc_report_single,
        "account": services.account_report_single,
        "ads": services.ad_level_report_single,
        "clickview": services.click_view_report_single,
        "paid_organic_terms": services.paid_org_search_term_report_single,
    }
    all_dispatch = {
        "arc": services.arc_report_all,
        "account": services.account_report_all,
        "ads": services.ad_level_report_all,
        "clickview": services.click_view_report_all,
        "paid_organic_terms": services.paid_org_search_term_report_all,
    }

    if account_scope == "single":
        if not account_id:
            account_id, account_name = helpers.get_account_properties(customer_dict)
        start_time = time.time()
        table_data, headers = single_dispatch[report_opt](
            gads_service,
            client,
            start_date,
            end_date,
            time_seg,
            customer_id=account_id,
            **toggles,
        )
        end_time = time.time()
    elif account_scope == "all":
        start_time = time.time()
        table_data, headers = all_dispatch[report_opt](
            gads_service,
            client,
            start_date,
            end_date,
            time_seg,
            customer_dict,
            **toggles,
        )
        end_time = time.time()
    else:
        print("Invalid account scope resolved; exiting.")
        sys.exit(1)

    prompts.execution_time(start_time, end_time)
    helpers.data_handling_options(
        table_data,
        headers,
        auto_view=False,
        preselected_output=output_mode,
    )


def budget_menu(gads_service, client, full_accounts_info, cli_args):
    """Display budgeting report options and run the selected workflow.

    Args:
        gads_service (GoogleAdsService): The Google Ads service used for
            executing reports.
        client (GoogleAdsClient): Authenticated Google Ads client instance.
        full_accounts_info (tuple[list[list[str]], list[str], dict[str, str], int]):
            Tuple with account table data, headers, lookup dictionary, and the
            count of accounts available to the user.
        cli_args (argparse.Namespace): Parsed CLI arguments guiding the flow.

    Returns:
        None: Execution continues through subsequent reporting steps.
    """

    _, _, customer_dict, _ = full_accounts_info
    report_opt = resolve_budget_option(cli_args)
    print("Budget report selected...")

    date_opt, start_date, end_date, time_seg = resolve_date_details(
        cli_args, force_single=False
    )
    output_mode = resolve_output_preference(cli_args)
    account_scope, account_id, account_name = resolve_account_scope(
        cli_args, customer_dict
    )
    report_details = (date_opt, start_date, end_date, time_seg, account_scope)

    prompts.data_review(report_details, debug=cli_args.debug)
    maybe_print_configuration_summary(
        cli_args,
        report_scope="budget",
        report_option=report_opt,
        date_details=(date_opt, start_date, end_date, time_seg),
        output_mode=output_mode,
        account_scope=account_scope,
        account_id=account_id,
        toggles={},
    )

    if account_scope == "single":
        if not account_id:
            account_id, account_name = helpers.get_account_properties(customer_dict)
        start_time = time.time()
        services.budget_report_single(
            gads_service,
            client,
            start_date,
            end_date,
            time_seg,
            customer_id=account_id,
        )
        end_time = time.time()
    elif account_scope == "all":
        start_time = time.time()
        services.budget_report_all(
            gads_service, client, start_date, end_date, time_seg, customer_dict
        )
        end_time = time.time()
    else:
        print("End of prototype options")
        sys.exit("Exiting - exit testing...")

    prompts.execution_time(start_time, end_time)


def audit_menu(gads_service, client, full_accounts_info, cli_args):
    """Run account auditing prompts and associated service calls.

    Args:
        gads_service (GoogleAdsService): The Google Ads service used for
            executing audit-related queries.
        client (GoogleAdsClient): Authenticated Google Ads client instance.
        full_accounts_info (tuple[list[list[str]], list[str], dict[str, str], int]):
            Tuple containing the account table, headers, account lookup
            dictionary, and count of accounts.
        cli_args (argparse.Namespace): Parsed CLI arguments guiding the flow.

    Returns:
        None: Argument parsing triggers the interactive workflow.
    """

    _, _, customer_dict, _ = full_accounts_info
    audit_opt = resolve_audit_option(cli_args)

    descriptive_labels = {
        "account_labels": "Account Labels Only Audit selected...",
        "campaign_groups": "Campaign Group Only Audit selected...",
        "label_assignments": "Campaign and Ad Group Label Assignments Audit selected...",
    }
    print(descriptive_labels.get(audit_opt, "Audit workflow selected."))

    output_mode = resolve_output_preference(cli_args)
    account_scope, account_id, account_name = resolve_account_scope(
        cli_args, customer_dict
    )
    if account_scope != "single":
        print("Audit workflows require selecting a single account.")
        account_id, account_name = helpers.get_account_properties(customer_dict)
        cli_args.account_scope = "single"
        cli_args.account_id = account_id
        cli_args.account_name = account_name

    maybe_print_configuration_summary(
        cli_args,
        report_scope="audit",
        report_option=audit_opt,
        date_details=None,
        output_mode=output_mode,
        account_scope="single",
        account_id=cli_args.account_id,
        toggles={},
    )

    if audit_opt == "account_labels":
        label_table, label_table_headers, label_dict = services.get_labels(
            gads_service, client, customer_id=cli_args.account_id
        )
        helpers.data_handling_options(
            label_table,
            label_table_headers,
            auto_view=False,
            preselected_output=output_mode,
        )
    elif audit_opt == "campaign_groups":
        camp_group_table, camp_group_headers, camp_group_dict = (
            services.get_campaign_groups(
                gads_service, client, customer_id=cli_args.account_id
            )
        )
        helpers.data_handling_options(
            camp_group_table,
            camp_group_headers,
            auto_view=False,
            preselected_output=output_mode,
        )
    elif audit_opt == "label_assignments":
        full_audit_table, full_audit_headers, full_audit_dict = (
            services.complete_labels_audit(
                gads_service, client, customer_id=cli_args.account_id
            )
        )
        helpers.data_handling_options(
            full_audit_table,
            full_audit_headers,
            auto_view=False,
            preselected_output=output_mode,
        )
    else:
        print("Invalid input, please select one of the indicated options.")


def main():
    """Execute the command-line interface for the Google Ads Reporter."""

    parser = build_parser()
    args = parser.parse_args()
    try:
        normalize_cli_args(parser, args)
    except ValueError as exc:
        parser.error(str(exc))
    init_menu(args)


if __name__ == "__main__":
    main()
