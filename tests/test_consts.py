"""Tests covering the constant definitions in ``consts``."""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import consts
import helpers


def test_toggle_value_sets():
    """Toggle include/exclude values should contain expected keywords."""

    assert consts.TOGGLE_INCLUDE_VALUES == {
        "include",
        "in",
        "yes",
        "y",
        "true",
        "1",
    }
    assert consts.TOGGLE_EXCLUDE_VALUES == {
        "exclude",
        "ex",
        "no",
        "n",
        "false",
        "0",
    }


def test_performance_toggle_config_structure():
    """Performance toggle configuration should point at helper prompts."""

    config = consts.PERFORMANCE_TOGGLE_CONFIG
    expected_reports = {
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

    assert config == expected_reports


def test_performance_toggle_fields_matches_config():
    """Ensure toggle field tuple stays synced with the toggle config."""

    expected_fields = tuple(
        entry["attr"] for entry in consts.PERFORMANCE_TOGGLE_CONFIG.values()
    )
    assert consts.PERFORMANCE_TOGGLE_FIELDS == expected_fields


def test_account_and_scope_aliases_cover_expected_inputs():
    """Critical alias dictionaries should expose known shortcuts."""

    assert consts.ACCOUNT_SCOPE_ALIASES["single"] == "single"
    assert consts.ACCOUNT_SCOPE_ALIASES["*"] == "all"
    assert consts.REPORT_SCOPE_ALIASES["perf"] == "performance"
    assert consts.REPORT_SCOPE_ALIASES["auditing"] == "audit"
    assert consts.REPORT_OPTION_ALIASES["ads"] == ("performance", "ads")
    assert consts.REPORT_OPTION_ALIASES["campaigns"] == ("audit", "campaign_groups")


def test_output_and_audit_constants():
    """Output choices and audit option mappings should stay consistent."""

    assert consts.OUTPUT_CHOICES == {"csv", "table", "auto"}
    assert consts.AUDIT_OPTION_MAP == {
        "1": "account_labels",
        "2": "campaign_groups",
        "3": "label_assignments",
    }
    assert consts.AUDIT_OPTION_DESCRIPTIONS == {
        "account_labels": "Account Labels Only Audit selected...",
        "campaign_groups": "Campaign Group Only Audit selected...",
        "label_assignments": "Campaign and Ad Group Label Assignments Audit selected...",
    }


def test_menu_option_alignment():
    """Menu option structures should align with report aliases and sets."""

    assert consts.REPORT_SCOPE_MENU_LOOKUP == {
        option: scope for option, _, scope in consts.REPORT_SCOPE_MENU_OPTIONS
    }
    assert {scope for _, _, scope in consts.REPORT_SCOPE_MENU_OPTIONS} == set(
        consts.REPORT_SCOPE_ALIASES.values()
    )

    performance_menu_options = {
        report for _, _, report in consts.PERFORMANCE_REPORT_MENU_OPTIONS
    }
    assert performance_menu_options == consts.PERFORMANCE_REPORT_OPTIONS
    assert consts.PERFORMANCE_REPORT_MENU_LOOKUP == {
        option: report for option, _, report in consts.PERFORMANCE_REPORT_MENU_OPTIONS
    }

    assert consts.AUDIT_REPORT_MENU_LOOKUP == {
        option: report for option, _, report in consts.AUDIT_REPORT_MENU_OPTIONS
    }
    assert consts.AUDIT_REPORT_MENU_LOOKUP == consts.AUDIT_OPTION_MAP
    assert {
        report for _, _, report in consts.AUDIT_REPORT_MENU_OPTIONS
    } == consts.AUDIT_REPORT_OPTIONS

    assert consts.BUDGET_REPORT_MENU_LOOKUP == {
        option: report for option, _, report in consts.BUDGET_REPORT_MENU_OPTIONS
    }
    assert {
        report for _, _, report in consts.BUDGET_REPORT_MENU_OPTIONS
    } == consts.BUDGET_REPORT_OPTIONS
