# -*- coding: utf-8 -*-
"""Command-line entry points for the Google Ads Reporter prototype."""

import argparse
import sys
import time

import helpers
import prompts
import services


# MENUS
def init_menu(yaml_loc=None):
    """Start the interactive reporter experience.

    The function authenticates against the Google Ads API, displays the
    available accounts to the user, and transitions into the primary menu.

    Args:
        yaml_loc (str | None): Optional path to a Google Ads configuration
            file. When ``None`` the default ``google-ads.yaml`` file within the
            repository is used.

    Returns:
        None: Control flow continues into the menu loop.
    """

    print(
        "\nGoogle Ads Reporter, developed by JDT using GAds API and gRPC\n"
        "NOTE: Enter 'exit' at any prompt will exit this reporting tool."
    )
    input("Press Enter When Ready...")
    print("Authorization in progress...")
    gads_service, customer_service, client = services.generate_services(yaml_loc)
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
    main_menu(gads_service, client, full_accounts_info)


def main_menu(gads_service, client, full_accounts_info):
    """Route the user to the appropriate reporting menu.

    Args:
        gads_service (GoogleAdsService): The authenticated Google Ads
            service used for reporting queries.
        client (GoogleAdsClient): The authenticated client instance used to
            generate additional services.
        full_accounts_info (tuple[list[list[str]], list[str], dict[str, str], int]):
            Tuple containing the tabular account listing, column headers, the
            mapping of customer IDs to names, and the number of accounts.

    Returns:
        None: Control flow continues into downstream menus.
    """

    report_scope = prompts.report_menu()
    if report_scope == "1":
        print("\nPerformance Reporting selected.\n")
        performance_menu(gads_service, client, full_accounts_info)
    elif report_scope == "2":
        print("\nAccount Auditing selected.\n")
        audit_menu(gads_service, client, full_accounts_info)
    elif report_scope == "3":
        print("\nBudget Reporting selected.\n")
        budget_menu(gads_service, client, full_accounts_info)
    else:
        print("Invalid input, please select one of the indicated numbered options.")
        # exit
        sys.exit(1)


def performance_menu(gads_service, client, full_accounts_info):
    """Display and execute performance-related report options.

    Args:
        gads_service (GoogleAdsService): The Google Ads service used for
            query execution.
        client (GoogleAdsClient): Authenticated Google Ads client instance.
        full_accounts_info (tuple[list[list[str]], list[str], dict[str, str], int]):
            Tuple with account table data, display headers, account lookup
            dictionary, and the number of available accounts.

    Returns:
        None: Data is processed and passed to downstream helpers.
    """

    customer_list, account_headers, customer_dict, num_accounts = full_accounts_info
    report_opt = prompts.report_opt_prompt()
    # ARC report
    if report_opt == "arc":
        print("ARC Report selected...")
        report_details = prompts.report_details_prompt(report_opt)
        date_opt, start_date, end_date, time_seg, account_scope = report_details
        # reporting options kwargs
        kwargs = {
            "include_channel_types": helpers.include_channel_types(),
            # "aggregate_channels": helpers.aggregate_channels(),
            "include_campaign_info": helpers.include_campaign_info(),
            # "include_adgroup_info": helpers.include_adgroup_info(),
            # "include_device_info": helpers.include_device_info()
        }

        prompts.data_review(report_details, **kwargs)

        if account_scope == "single":
            # parse single account info
            account_info = helpers.get_account_properties(customer_dict)
            account_id, account_name = account_info  # pass single accountID
            start_time = time.time()
            table_data, headers = services.arc_report_single(
                gads_service,
                client,
                start_date,
                end_date,
                time_seg,
                customer_id=account_id,  # pass single accountID
                **kwargs,
            )
            end_time = time.time()
            prompts.execution_time(start_time, end_time)
            # handle data
            helpers.data_handling_options(table_data, headers, auto_view=False)
        elif account_scope == "all":
            start_time = time.time()
            all_account_data, headers = services.arc_report_all(
                gads_service,
                client,
                start_date,
                end_date,
                time_seg,
                customer_dict,  # pass all accounts
                **kwargs,
            )
            end_time = time.time()
            prompts.execution_time(start_time, end_time)
            # handle data
            helpers.data_handling_options(all_account_data, headers, auto_view=False)
    # Account report
    elif report_opt == "account":
        print("Accounts Report selected...")
        report_details = prompts.report_details_prompt(report_opt)
        date_opt, start_date, end_date, time_seg, account_scope = report_details
        # reporting options kwargs
        kwargs = {
            # "include_channel_types": helpers.include_channel_types(),
            # "include_campaign_info": helpers.include_campaign_info(),
            # "include_adgroup_info": helpers.include_adgroup_info(),
            # "include_device_info": helpers.include_device_info()
        }

        prompts.data_review(report_details, **kwargs)

        if account_scope == "single":
            account_info = helpers.get_account_properties(customer_dict)
            account_id, account_name = account_info
            start_time = time.time()
            table_data, headers = services.account_report_single(
                gads_service,
                client,
                start_date,
                end_date,
                time_seg,
                customer_id=account_id,  # pass single accountID
                **kwargs,
            )
            end_time = time.time()
            prompts.execution_time(start_time, end_time)
            # handle data
            helpers.data_handling_options(table_data, headers, auto_view=False)
        elif account_scope == "all":
            start_time = time.time()
            all_account_data, headers = services.account_report_all(
                gads_service,
                client,
                start_date,
                end_date,
                time_seg,
                customer_dict,  # pass all accounts
                **kwargs,
            )
            end_time = time.time()
            prompts.execution_time(start_time, end_time)
            # handle data
            helpers.data_handling_options(all_account_data, headers, auto_view=False)
    # Ads report
    elif report_opt == "ads":
        print("Ads Report selected...")
        report_details = prompts.report_details_prompt(report_opt)
        date_opt, start_date, end_date, time_seg, account_scope = report_details
        # reporting options kwargs
        kwargs = {
            "include_channel_types": helpers.include_channel_types(),
            "include_campaign_info": helpers.include_campaign_info(),
            "include_adgroup_info": helpers.include_adgroup_info(),
            # "include_device_info": helpers.include_device_info()
        }

        prompts.data_review(report_details, **kwargs)

        if account_scope == "single":
            account_info = helpers.get_account_properties(customer_dict)
            account_id, account_name = account_info
            start_time = time.time()
            table_data, headers = services.ad_level_report_single(
                gads_service,
                client,
                start_date,
                end_date,
                time_seg,
                customer_id=account_id,  # pass single accountID
                **kwargs,
            )
            end_time = time.time()
            prompts.execution_time(start_time, end_time)
            # handle data
            helpers.data_handling_options(table_data, headers, auto_view=False)
        elif account_scope == "all":
            start_time = time.time()
            all_account_data, headers = services.ad_level_report_all(
                gads_service,
                client,
                start_date,
                end_date,
                time_seg,
                customer_dict,  # pass all accounts
                **kwargs,
            )
            end_time = time.time()
            prompts.execution_time(start_time, end_time)
            # handle data
            helpers.data_handling_options(all_account_data, headers, auto_view=False)
    # click_view/GCLID report
    elif report_opt == "clickview":
        print("GCLID/ClickView Report selected...")
        report_details = prompts.report_details_prompt(report_opt)
        date_opt, start_date, end_date, time_seg, account_scope = report_details
        # reporting options kwargs
        kwargs = {
            "include_channel_types": helpers.include_channel_types(),
            "include_campaign_info": helpers.include_campaign_info(),
            "include_adgroup_info": helpers.include_adgroup_info(),
            "include_device_info": helpers.include_device_info(),
        }

        prompts.data_review(report_details, **kwargs)

        if account_scope == "single":
            account_info = helpers.get_account_properties(customer_dict)
            account_id, account_name = account_info
            start_time = time.time()
            table_data, headers = services.click_view_report_single(
                gads_service,
                client,
                start_date,
                end_date,
                time_seg,
                customer_id=account_id,  # pass single accountID
                **kwargs,
            )
            end_time = time.time()
            prompts.execution_time(start_time, end_time)
            # handle data
            helpers.data_handling_options(table_data, headers, auto_view=False)
        elif account_scope == "all":
            start_time = time.time()
            all_account_data, headers = services.click_view_report_all(
                gads_service,
                client,
                start_date,
                end_date,
                time_seg,
                customer_dict,  # pass all accounts
                **kwargs,
            )
            end_time = time.time()
            prompts.execution_time(start_time, end_time)
            # handle data
            helpers.data_handling_options(all_account_data, headers, auto_view=False)
    # paid/org search terms report
    elif report_opt == "paid_organic_terms":
        print("Paid and Organic Search Terms Report selected...")
        report_details = prompts.report_details_prompt(report_opt)
        date_opt, start_date, end_date, time_seg, account_scope = report_details
        # reporting options kwargs
        kwargs = {
            "include_channel_types": helpers.include_channel_types(),
            "include_campaign_info": helpers.include_campaign_info(),
            "include_adgroup_info": helpers.include_adgroup_info(),
            "include_device_info": helpers.include_device_info(),
        }

        # debug
        prompts.data_review(report_details, **kwargs)

        if account_scope == "single":
            account_info = helpers.get_account_properties(customer_dict)
            account_id, account_name = account_info
            start_time = time.time()
            table_data, headers = services.paid_org_search_term_report_single(
                gads_service,
                client,
                start_date,
                end_date,
                time_seg,
                customer_id=account_id,  # pass single accountID
                **kwargs,
            )
            end_time = time.time()
            prompts.execution_time(start_time, end_time)
            # handle data
            helpers.data_handling_options(table_data, headers, auto_view=False)
        elif account_scope == "all":
            start_time = time.time()
            all_account_data, headers = services.paid_org_search_term_report_all(
                gads_service,
                client,
                start_date,
                end_date,
                time_seg,
                customer_dict,  # pass all accounts
                **kwargs,
            )
            end_time = time.time()
            prompts.execution_time(start_time, end_time)
            # handle data
            helpers.data_handling_options(all_account_data, headers, auto_view=False)

        """
        elif report_opt == 'x':
            services.test_query(gads_service, client, customer_id=account_id)
        """
    else:
        print("Invalid input, please select one of the indicated options.")
        # exit
        sys.exit(1)


def budget_menu(gads_service, client, full_accounts_info):
    """Display budgeting report options and run the selected workflow.

    Args:
        gads_service (GoogleAdsService): The Google Ads service used for
            executing reports.
        client (GoogleAdsClient): Authenticated Google Ads client instance.
        full_accounts_info (tuple[list[list[str]], list[str], dict[str, str], int]):
            Tuple with account table data, headers, lookup dictionary, and the
            count of accounts available to the user.

    Returns:
        None: Execution continues through subsequent reporting steps.
    """

    customer_list, account_headers, customer_dict, num_accounts = full_accounts_info
    report_opt = prompts.budget_opt_prompt()
    # budget report
    if report_opt == "budget":
        report_details = prompts.report_details_prompt(report_opt)

        prompts.data_review(report_details)

        date_opt, start_date, end_date, time_seg, account_scope = report_details

        if account_scope == "single":
            account_info = helpers.get_account_properties(customer_dict)
            account_id, account_name = account_info
            start_time = time.time()

            # dev ph
            services.budget_report_single(
                gads_service,
                client,
                start_date,
                end_date,
                time_seg,
                customer_id=account_id,
            )

            end_time = time.time()
            prompts.execution_time(start_time, end_time)
            # handle data
            # helpers.data_handling_options(table_data, headers, auto_view=False)
        elif account_scope == "all":
            start_time = time.time()

            # dev ph
            services.budget_report_all(
                gads_service, client, start_date, end_date, time_seg, customer_dict
            )
            end_time = time.time()
            prompts.execution_time(start_time, end_time)
            # handle data
            # helpers.data_handling_options(all_account_data, headers, auto_view=False)
        else:
            # update when reports are developed
            print("End of prototype options")
            sys.exit("Exiting - exit testing...")


def audit_menu(gads_service, client, full_accounts_info):
    """Run account auditing prompts and associated service calls.

    Args:
        gads_service (GoogleAdsService): The Google Ads service used for
            executing audit-related queries.
        client (GoogleAdsClient): Authenticated Google Ads client instance.
        full_accounts_info (tuple[list[list[str]], list[str], dict[str, str], int]):
            Tuple containing the account table, headers, account lookup
            dictionary, and count of accounts.

    Returns:
        None: Argument parsing triggers the interactive workflow.
    """

    customer_list, account_headers, customer_dict, num_accounts = full_accounts_info
    audit_opt = prompts.audit_opt_prompt()
    if audit_opt == "1":
        print("Account Labels Only Audit selected...")
        account_info = helpers.get_account_properties(customer_dict)
        account_id, account_name = account_info
        label_table, label_table_headers, label_dict = services.get_labels(
            gads_service, client, customer_id=account_id
        )
        # handle data
        helpers.data_handling_options(label_table, label_table_headers, auto_view=False)
    elif audit_opt == "2":
        print("Campaign Group Only Audit selected...")
        account_info = helpers.get_account_properties(customer_dict)
        account_id, account_name = account_info
        camp_group_table, camp_group_headers, camp_group_dict = (
            services.get_campaign_groups(gads_service, client, customer_id=account_id)
        )
        # handle data
        helpers.data_handling_options(
            camp_group_table, camp_group_headers, auto_view=False
        )
    elif audit_opt == "3":
        print("Campaign and Ad Group Label Assignments Audit selected...")
        account_info = helpers.get_account_properties(customer_dict)
        account_id, account_name = account_info
        # execute full report
        full_audit_table, full_audit_headers, full_audit_dict = (
            services.complete_labels_audit(gads_service, client, customer_id=account_id)
        )
        # handle data
        helpers.data_handling_options(
            full_audit_table, full_audit_headers, auto_view=False
        )
    else:
        print("Invalid input, please select one of the indicated options.")


def main():
    """Execute the command-line interface for the Google Ads Reporter."""

    parser = argparse.ArgumentParser(
        prog="GAR",
        description="Google Ads Reporter",
        epilog="Developed by Joe Thompson",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-y",
        "--yaml",
        help="Path to a YAML config file containing OAuth or Service Account credentials.",
    )
    args = parser.parse_args()
    init_menu(yaml_loc=args.yaml)


if __name__ == "__main__":
    main()
