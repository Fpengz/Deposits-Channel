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


def test_macro_regime_matrix_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Regime Matrix" in content
    assert "Crisis" in content


def test_case_study_counterfactual_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Q4: What would have reduced the damage?" in content
    assert "Lower duration" in content


def test_monitoring_tab_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Monitoring & Scenarios" in content


def test_monitoring_playbook_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "If this, then that playbook" in content
    assert "Higher for longer" in content


def test_monitoring_tab_matches_planned_structure() -> None:
    content = Path("src/app.py").read_text()

    for label in [
        "Stress composite",
        "Bank beta regime",
        "Curve regime",
        "MMF pressure",
        "Credit stress trend",
    ]:
        assert label in content

    for scenario in [
        "Higher for longer",
        "Rapid cuts",
        "Volatility shock",
        "Bank-specific confidence shock",
    ]:
        assert scenario in content

    assert "Spreads | Deposits | Stress | Banks" in content
    assert "if" in content.lower()
    assert "then" in content.lower()


def test_monitoring_tab_uses_scenario_expectations_helper() -> None:
    content = Path("src/app.py").read_text()

    assert "scenario_expectations(" in content


def test_monitoring_scorecard_uses_shorter_lookback_fallbacks() -> None:
    content = Path("src/app.py").read_text()

    assert "_build_recent_stress_series(" in content
    assert "_recent_beta_regime(" in content
    assert "_recent_change(" in content
    assert "for lookback in (252, 126, 63, 21, 10, 5):" in content


def test_monitoring_credit_trend_does_not_normalize_ff_proxy_into_treasury_price() -> None:
    content = Path("src/app.py").read_text()

    assert 'credit_data["Credit_Price"], credit_data["FF_Proxy"] / 100 + 1' not in content
    assert 'credit_frame["Credit_Price"], credit_frame["FF_Proxy"] / 100 + 1' not in content
    assert "Credit_Stress_Trend" in content
    assert '_recent_change(credit_frame["Credit_Price"])' in content


def test_monitoring_playbook_contains_exact_planned_rules() -> None:
    content = Path("src/app.py").read_text()

    assert (
        "If rates rise while VIX stays low: expect orderly spread widening before panic." in content
    )
    assert "If rates are stable but VIX spikes: expect fear to dominate rate mechanics." in content
    assert (
        "If the curve steepens through cuts: expect temporary relief in funding stress." in content
    )
    assert (
        "If MMFs outperform while bank betas stay negative: treat that as an active-channel warning."
        in content
    )
