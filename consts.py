# -*- coding: utf-8 -*-
"""Centralized constant definitions for CLI parsing and reporting."""

import helpers

PERFORMANCE_REPORT_OPTIONS = {
    "arc",
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
    "arc": ("performance", "arc"),
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
    ("1", "ARC Report", "arc"),
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

PERFORMANCE_TOGGLE_CONFIG = {
    "include_channel_types": {
        "attr": "include_channel_type",
        "reports": {"arc", "ads", "clickview", "paid_organic_terms"},
        "prompt": helpers.include_channel_types,
        "label": "channel type segmentation",
        "cli_option": "--channel-types",
        "default": False,
    },
    "include_campaign_info": {
        "attr": "include_campaign_info",
        "reports": {"arc", "ads", "clickview", "paid_organic_terms"},
        "prompt": helpers.include_campaign_info,
        "label": "campaign metadata",
        "cli_option": "--campaign-info",
        "default": False,
    },
    "include_adgroup_info": {
        "attr": "include_adgroup_info",
        "reports": {"ads", "clickview", "paid_organic_terms"},
        "prompt": helpers.include_adgroup_info,
        "label": "ad group metadata",
        "cli_option": "--ad-group",
        "default": False,
    },
    "include_device_info": {
        "attr": "include_device_type",
        "reports": {"clickview", "paid_organic_terms"},
        "prompt": helpers.include_device_info,
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
