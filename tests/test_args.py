# tests/test_args.py

import os
from argparse import ArgumentParser

import pytest

from gar import common, services
from gar.main import build_parser, normalize_cli_args


# ------------------------------
# Helper: build parser for tests
# ------------------------------
@pytest.fixture
def parser() -> ArgumentParser:
    return build_parser()


# ------------------------------
# Defaults & YAML handling
# ------------------------------
def test_no_args_defaults_to_interactive(parser):
    args = parser.parse_args([])
    args = normalize_cli_args(parser, args)
    assert args.report_scope is None
    assert args.cli_mode is False  # should drop into interactive mode


def test_yaml_arg(parser):
    args = parser.parse_args(["--yaml", "authfiles/test.yaml"])
    args = normalize_cli_args(parser, args)
    assert args.yaml == "authfiles/test.yaml"


def test_missing_yaml(monkeypatch, parser):
    # force os.path.exists to return False
    monkeypatch.setattr(os.path, "exists", lambda _: False)
    # fake input to test blocking
    monkeypatch.setattr("builtins.input", lambda _: "somepath.yaml")

    with pytest.raises(SystemExit):
        services.generate_services("nonexistent.yaml")


# ------------------------------
# Report argument parsing
# ------------------------------
def test_report_with_scope_and_option(parser):
    args = parser.parse_args(["--report", "performance:mac"])
    args = normalize_cli_args(parser, args)
    assert args.report_scope == "performance"
    assert args.report_option == "mac"


def test_conflicting_report_options(parser):
    args = parser.parse_args(
        ["--report", "performance:mac", "--report-option", "account"]
    )
    with pytest.raises(ValueError):
        normalize_cli_args(parser, args)


def test_report_and_account(parser):
    args = parser.parse_args(
        ["--report", "performance:ads", "--account", "single:1234567890"]
    )
    normalized = normalize_cli_args(parser, args)
    assert normalized.report_scope == "performance"
    assert normalized.report_option == "ads"
    assert normalized.account_scope_cli == "single"
    assert normalized.account_id_cli == "1234567890"


# ------------------------------
# Account parsing
# ------------------------------
def test_account_single(parser):
    args = parser.parse_args(["--account", "single:1234567890"])
    args = normalize_cli_args(parser, args)
    assert args.account_scope_cli == "single"
    assert args.account_id_cli == "1234567890"


def test_invalid_account(parser):
    args = parser.parse_args(["--account", "weirdformat"])
    with pytest.raises(ValueError):
        normalize_cli_args(parser, args)


def test_account_all_scope(parser):
    args = parser.parse_args(["--report", "performance:mac", "--account", "all"])
    normalized = normalize_cli_args(parser, args)
    assert normalized.account_scope_cli == "all"
    assert normalized.account_id_cli is None


# ------------------------------
# Toggle flags (include/exclude)
# ------------------------------
def test_device_toggle_include(parser):
    args = parser.parse_args(["--device", "include"])
    normalized = normalize_cli_args(parser, args)
    assert normalized.include_device_type is True


def test_device_toggle_exclude(parser):
    args = parser.parse_args(["--device", "exclude"])
    normalized = normalize_cli_args(parser, args)
    assert normalized.include_device_type is False


def test_channel_toggle_include(parser):
    args = parser.parse_args(["--channel-types", "include"])
    normalized = normalize_cli_args(parser, args)
    assert normalized.include_channel_type is True


# ------------------------------
# Date parsing
# ------------------------------
def test_date_last30days(parser):
    args = parser.parse_args(["--date", "last30days"])
    normalized = normalize_cli_args(parser, args)
    date_opt, start, end, seg = common.resolve_date_details(
        normalized, force_single=False
    )
    assert date_opt == "Date range"
    assert start is not None and end is not None


def test_date_specific(parser):
    args = parser.parse_args(["--date", "specific:2025-01-15"])
    normalized = normalize_cli_args(parser, args)
    date_opt, start, end, seg = common.resolve_date_details(
        normalized, force_single=False
    )
    assert date_opt == "Specific date"
    assert "2025-01-15" in str(start)


# ------------------------------
# Output handling
# ------------------------------
def test_output_csv(parser):
    args = parser.parse_args(["--output", "csv"])
    normalized = normalize_cli_args(parser, args)
    assert normalized.output_mode == "csv"


# ------------------------------
# CLI entrypoint behavior
# ------------------------------
def test_help_flag(capsys, parser):
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    captured = capsys.readouterr()
    assert "usage:" in captured.out
    assert "google-ads-reporter" in captured.out
