"""Tests covering the constant definitions in ``common``."""

import sys
from pathlib import Path

from gar import common

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def test_toggle_value_sets():
    """Toggle include/exclude values should contain expected keywords."""

    assert common.TOGGLE_INCLUDE_VALUES == {
        "include",
        "in",
        "yes",
        "y",
        "true",
        "1",
    }
    assert common.TOGGLE_EXCLUDE_VALUES == {
        "exclude",
        "ex",
        "no",
        "n",
        "false",
        "0",
    }


def test_performance_toggle_config_structure():
    """Performance toggle configuration should point at helper prompts."""

    config = common.PERFORMANCE_TOGGLE_CONFIG
    expected_reports = {
        "include_channel_types": {
            "attr": "include_channel_type",
            "reports": {"mac", "ads", "clickview", "paid_organic_terms"},
            "prompt": common.include_channel_types,
            "label": "channel type segmentation",
            "cli_option": "--channel-types",
            "default": False,
        },
        "include_campaign_info": {
            "attr": "include_campaign_info",
            "reports": {"mac", "ads", "clickview", "paid_organic_terms"},
            "prompt": common.include_campaign_info,
            "label": "campaign metadata",
            "cli_option": "--campaign-info",
            "default": False,
        },
        "include_adgroup_info": {
            "attr": "include_adgroup_info",
            "reports": {"ads", "clickview", "paid_organic_terms"},
            "prompt": common.include_adgroup_info,
            "label": "ad group metadata",
            "cli_option": "--ad-group",
            "default": False,
        },
        "include_device_info": {
            "attr": "include_device_type",
            "reports": {"clickview", "paid_organic_terms"},
            "prompt": common.include_device_info,
            "label": "device segmentation",
            "cli_option": "--device",
            "default": False,
        },
    }

    assert config == expected_reports


def test_performance_toggle_fields_matches_config():
    """Ensure toggle field tuple stays synced with the toggle config."""

    expected_fields = tuple(
        entry["attr"] for entry in common.PERFORMANCE_TOGGLE_CONFIG.values()
    )
    assert common.PERFORMANCE_TOGGLE_FIELDS == expected_fields


def test_account_and_scope_aliases_cover_expected_inputs():
    """Critical alias dictionaries should expose known shortcuts."""

    assert common.ACCOUNT_SCOPE_ALIASES["single"] == "single"
    assert common.ACCOUNT_SCOPE_ALIASES["*"] == "all"
    assert common.REPORT_SCOPE_ALIASES["perf"] == "performance"
    assert common.REPORT_SCOPE_ALIASES["auditing"] == "audit"
    assert common.REPORT_OPTION_ALIASES["ads"] == ("performance", "ads")
    assert common.REPORT_OPTION_ALIASES["campaigns"] == ("audit", "campaign_groups")


def test_output_and_audit_constants():
    """Output choices and audit option mappings should stay consistent."""

    assert common.OUTPUT_CHOICES == {"csv", "table", "auto"}
    assert common.AUDIT_OPTION_MAP == {
        "1": "account_labels",
        "2": "campaign_groups",
        "3": "label_assignments",
    }
