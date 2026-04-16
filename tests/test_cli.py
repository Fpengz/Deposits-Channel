from pathlib import Path

from src import cli


def test_build_app_command() -> None:
    command = cli.build_command("app", ["--server.headless", "true"])

    assert command == ["streamlit", "run", "src/app.py", "--server.headless", "true"]


def test_build_check_commands() -> None:
    commands = cli.build_pipeline("check", [])

    assert commands == [
        ["ruff", "check", "."],
        ["ty", "check", "--extra-search-path", "src"],
        ["pytest"],
    ]


def test_build_hooks_command_passes_extra_args() -> None:
    command = cli.build_command("hooks", ["tests/test_cli.py"])

    assert command == ["pre-commit", "run", "--all-files", "tests/test_cli.py"]


def test_theory_tab_story_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Q5: When do outflows and AOCI become destabilizing?" in content
    assert "Research takeaway" in content


def test_empirical_terminal_signal_board_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Signal Board" in content
    assert "Dormant" in content


def test_empirical_terminal_keeps_mmf_out_of_core_dropna_path() -> None:
    content = Path("src/app.py").read_text()
    assert 'core_empirical_cols = ["FF_Proxy", "KBE", "IAT", "SPY", "VIX"]' in content
    assert "data = data_full[core_empirical_cols].dropna().copy()" in content


def test_empirical_terminal_drops_missing_factor_rows_before_regressions() -> None:
    content = Path("src/app.py").read_text()
    assert 'required_empirical_factors = ["d_ff", "r_kbe", "r_iat", "r_spy"]' in content
    assert "data = data.dropna(subset=required_empirical_factors)" in content


def test_empirical_terminal_warns_and_skips_when_filtered_data_is_empty() -> None:
    content = Path("src/app.py").read_text()
    assert "Selected timeframe does not have enough return/rate observations" in content
    assert "if data.empty:" in content
