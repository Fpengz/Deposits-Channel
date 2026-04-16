from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from src import cli

APP_SOURCE = Path(__file__).resolve().parents[1] / "src" / "app.py"


def _load_app_helper(name: str, extra_globals: dict[str, object] | None = None):
    source = APP_SOURCE.read_text()
    module = ast.parse(source)
    func = next(
        node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == name
    )
    namespace: dict[str, object] = {"pd": pd, "np": np}
    if extra_globals:
        namespace.update(extra_globals)
    exec(compile(ast.Module(body=[func], type_ignores=[]), str(APP_SOURCE), "exec"), namespace)
    return namespace[name]


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


def test_app_supports_package_and_script_imports() -> None:
    content = Path("src/app.py").read_text()

    assert "from src.analysis import (" in content
    assert "except ImportError:" in content
    assert "from analysis import (" in content
    assert "from src.data_fetcher import (" in content
    assert "from src.simulation import (" in content


def test_macro_sections_guard_all_join_dependencies() -> None:
    content = Path("src/app.py").read_text()

    assert (
        "if not ff_proxy.empty and not mmf_proxy.empty and not tnx_proxy.empty and not kbe_proxy.empty:"
        in content
    )
    assert "and not spy_proxy.empty" in content


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


def test_build_recent_stress_series_can_populate_with_short_fallback_history() -> None:
    calls: list[tuple[int, int, int]] = []

    def fake_build_stress_index(
        d_ff: pd.Series,
        r_vix: pd.Series,
        kbe_price: pd.Series,
        window: int = 252,
        smoothing: int = 5,
    ) -> pd.Series:
        calls.append((len(d_ff), window, smoothing))
        if len(d_ff) >= 10 and window == 5 and smoothing == 5:
            return pd.Series([np.nan] * (len(d_ff) - 1) + [1.0], index=d_ff.index)
        return pd.Series(dtype=float, index=d_ff.index)

    build_recent_stress_series = _load_app_helper(
        "_build_recent_stress_series", {"build_stress_index": fake_build_stress_index}
    )
    index = pd.date_range("2024-01-01", periods=10, freq="D")
    frame = pd.DataFrame(
        {
            "d_ff": np.linspace(0.0, 1.0, len(index)),
            "r_vix": np.linspace(1.0, 2.0, len(index)),
            "KBE": np.linspace(30.0, 20.0, len(index)),
        },
        index=index,
    )

    result = build_recent_stress_series(frame)

    assert not result.empty
    assert result.iloc[-1] == 1.0
    assert any(length == 10 and window == 5 for length, window, _ in calls)


def test_recent_change_reports_actual_horizon_used_in_ui_labels() -> None:
    recent_change = _load_app_helper("_recent_change")
    series = pd.Series(
        np.linspace(100.0, 114.0, 5),
        index=pd.date_range("2024-01-01", periods=5, freq="D"),
    )

    change, horizon = recent_change(series)
    content = APP_SOURCE.read_text()

    assert horizon == 4
    assert change == pytest.approx(0.14)
    assert 'mmf_delta = f"{mmf_horizon}d={mmf_trend:+.1%}"' in content
    assert 'credit_delta = f"{credit_horizon}d={credit_trend:+.1%}"' in content
