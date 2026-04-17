from __future__ import annotations

import ast
import html
import re
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


def _extract_tab_block(source: str, tab_name: str) -> str:
    module = ast.parse(source)
    blocks: list[str] = []
    for node in module.body:
        if isinstance(node, ast.With):
            for item in node.items:
                expr = item.context_expr
                if isinstance(expr, ast.Name) and expr.id == tab_name:
                    lines = source.splitlines()
                    blocks.append("\n".join(lines[node.lineno - 1 : node.end_lineno]))
    if blocks:
        return "\n\n".join(blocks)
    raise AssertionError(f"Could not find block for {tab_name}")


def _extract_tab_nodes(source: str, tab_name: str) -> list[ast.With]:
    module = ast.parse(source)
    nodes: list[ast.With] = []
    for node in module.body:
        if isinstance(node, ast.With):
            for item in node.items:
                expr = item.context_expr
                if isinstance(expr, ast.Name) and expr.id == tab_name:
                    nodes.append(node)
    if nodes:
        return nodes
    raise AssertionError(f"Could not find node for {tab_name}")


def _call_name(call: ast.Call) -> str | None:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _tab_call_nodes(source: str, tab_name: str, func_name: str) -> list[ast.Call]:
    calls: list[ast.Call] = []
    for node in _extract_tab_nodes(source, tab_name):
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and _call_name(child) == func_name:
                calls.append(child)
    return calls


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
    theory_block = _extract_tab_block(content, "tab1")

    assert "Theory & Simulation" in theory_block
    assert "Q1: What is the deposits channel mechanism?" in theory_block
    assert "render_research_module_intro(" in theory_block
    assert "render_takeaway_block(" in theory_block
    assert "**Short answer:**" not in theory_block
    assert "By the end of this section" in theory_block
    assert "Q5: When do outflows and AOCI become destabilizing?" in theory_block
    assert "**What to notice:**" in theory_block


def test_research_seminar_spine_labels_and_tabs_present() -> None:
    content = APP_SOURCE.read_text()

    for label in ["Short answer", "What to notice", "Takeaway"]:
        assert label in content

    for heading in [
        "Theory & Simulation",
        "Empirical Terminal",
        "Macro & Credit",
        "Case Study",
        "Monitoring & Scenarios",
    ]:
        assert heading in content


def test_empirical_terminal_signal_board_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Signal Board" in content
    assert "Transmission dormant" in content


def test_empirical_terminal_reads_like_research_seminar() -> None:
    content = Path("src/app.py").read_text()
    empirical_block = _extract_tab_block(content, "tab2")

    assert "render_research_module_intro(" in empirical_block
    assert "render_takeaway_block(" in empirical_block
    assert "**Short answer:**" not in empirical_block
    assert "research seminar" in empirical_block
    assert "signal board" in empirical_block

    ordered_markers = [
        "Q1: Are banks sensitive to rate shocks?",
        "Q2: Is stress building in the system?",
        "Signal Board",
        "Q8: Which regime are we in?",
        "Q3: Do policy events create abnormal returns?",
        "Q5: Does fear amplify the channel?",
        "Q6: How do shocks propagate over time?",
        "render_takeaway_block(",
    ]
    positions = [empirical_block.index(marker) for marker in ordered_markers]
    assert positions == sorted(positions)

    assert "The selected timeframe leaves no overlapping observations" in empirical_block
    assert re.search(
        r"empirical board and stress composite.*signal board and regime summary are unavailable",
        empirical_block,
        re.IGNORECASE | re.DOTALL,
    )


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
    assert "does not leave enough aligned return and rate observations" in content
    assert "if data.empty:" in content


def test_guided_entry_orientation_preface_is_wired_into_page_flow() -> None:
    content = APP_SOURCE.read_text()
    module = ast.parse(content)

    start_date_line = next(
        node.lineno
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "start_date" for target in node.targets
        )
    )
    end_date_line = next(
        node.lineno
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "end_date" for target in node.targets)
    )
    render_preface_node = next(
        node
        for node in module.body
        if isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and _call_name(node.value) == "render_reading_preface"
    )
    tabs_node = next(
        node
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Tuple) for target in node.targets)
        and any(isinstance(target, ast.Name) and target.id == "tab1" for target in ast.walk(node))
    )

    assert "render_reading_preface(start_date, end_date)" in content
    assert "How to read this terminal" in content
    assert start_date_line < end_date_line < render_preface_node.lineno < tabs_node.lineno
    render_preface_call = render_preface_node.value
    assert isinstance(render_preface_call, ast.Call)
    render_preface_args: list[str] = []
    for arg in render_preface_call.args:
        assert isinstance(arg, ast.Name)
        render_preface_args.append(arg.id)
    assert render_preface_args == ["start_date", "end_date"]


def test_decision_layer_summary_band_is_wired_before_tabs() -> None:
    content = APP_SOURCE.read_text()
    module = ast.parse(content)

    summary_node = next(
        node
        for node in module.body
        if isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and _call_name(node.value) == "render_terminal_summary_band"
    )
    tabs_node = next(
        node
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Tuple) for target in node.targets)
        and any(isinstance(target, ast.Name) and target.id == "tab1" for target in ast.walk(node))
    )

    assert "Top summary" in content
    assert "Overall read" in content
    assert "Action posture" in content
    assert summary_node.lineno < tabs_node.lineno


def test_each_tab_surfaces_a_compact_state_label() -> None:
    content = APP_SOURCE.read_text()

    for tab_name in ["tab1", "tab2", "tab3", "tab4", "tab5"]:
        block = _extract_tab_block(content, tab_name)
        assert "render_state_label(" in block

    for label in [
        '"Theory"',
        '"Empirical"',
        '"Macro & Credit"',
        '"Case Study"',
        '"Monitoring"',
    ]:
        assert label in content


def test_tabs_include_orientation_strip_cues() -> None:
    content = APP_SOURCE.read_text()

    for tab_name in ["tab1", "tab2", "tab3", "tab4", "tab5"]:
        block = _extract_tab_block(content, tab_name)
        assert "render_tab_purpose_strip(" in block

    assert content.count("render_tab_purpose_strip(") >= 5


def test_guided_entry_orientation_is_present_without_becoming_tutorial_heavy() -> None:
    content = APP_SOURCE.read_text()
    module = ast.parse(content)

    read_next_count = content.count("Read this next")
    only_one_chart_count = content.count("If you only look at one chart")

    render_preface_calls = [
        node
        for node in ast.walk(module)
        if isinstance(node, ast.Call) and _call_name(node) == "render_reading_preface"
    ]
    tab_purpose_calls = [
        node
        for node in ast.walk(module)
        if isinstance(node, ast.Call) and _call_name(node) == "render_tab_purpose_strip"
    ]

    assert len(render_preface_calls) == 1
    assert len(tab_purpose_calls) >= 5
    assert "How to read this terminal" in content
    assert "Selected sample" in content
    assert "The case-study tab is a fixed March 2023 episode by design." in content
    assert 4 <= read_next_count <= 6
    assert 1 <= only_one_chart_count <= 2


def test_app_includes_within_tab_read_next_cues() -> None:
    content = APP_SOURCE.read_text()
    empirical_block = _extract_tab_block(content, "tab2")
    monitoring_block = _extract_tab_block(content, "tab5")

    assert content.count("Read this next") >= 5
    assert content.count("If you only look at one chart") >= 1
    assert (
        "Read this next: if the signal board looks active, move to Q8 before the event study."
        in empirical_block
    )
    assert (
        "Read this next: after the scorecard, use the scenario cards to pressure-test the most likely stress paths."
        in monitoring_block
    )
    assert "If you only look at one chart, start with the scorecard." in monitoring_block


def test_app_includes_cross_tab_handoffs() -> None:
    content = APP_SOURCE.read_text()

    assert content.count("Continue in") >= 3
    for prompt in [
        "Continue in Empirical Terminal if you want to see whether the mechanism appears in the selected sample.",
        "Continue in Macro & Credit if you want to trace the spillover into the wider funding backdrop.",
        "Continue in Monitoring & Scenarios if you want to turn the episode into a live watchlist.",
    ]:
        assert prompt in content


def test_macro_regime_matrix_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Regime Matrix" in content
    assert "Crisis" in content


def test_macro_tab_uses_flow_of_funds_seminar_framing() -> None:
    content = Path("src/app.py").read_text()
    macro_block = _extract_tab_block(content, "tab3")

    assert "Trace proxy evidence" in macro_block
    assert "render_research_module_intro(" in macro_block
    assert "render_takeaway_block(" in macro_block
    assert "**Short answer:**" not in macro_block
    assert "proxy-based" in macro_block
    assert "interpretive" in macro_block
    assert "downstream pressure" in macro_block
    assert "Q3: Is credit stress feeding back into banks?" in macro_block
    assert (
        "Widening credit 'stress' indicates a contraction in bank lending supply as deposits leave the system."
        in macro_block
    )


def test_case_study_counterfactual_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Q4: What would have changed the outcome?" in content
    assert "Lower duration" in content


def test_case_study_uses_narrative_arc_framing() -> None:
    content = Path("src/app.py").read_text()
    case_block = _extract_tab_block(content, "tab4")

    assert "March 2023 Banking Stress" in case_block
    assert "render_research_module_intro(" in case_block
    assert "render_takeaway_block(" in case_block
    assert "**Short answer:**" not in case_block
    for marker in [
        "preconditions",
        "break",
        "market interpretation",
        "counterfactual repair",
    ]:
        assert marker in case_block
    assert "duration, stickiness, or concentration" in case_block


def test_monitoring_tab_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Monitoring & Scenarios" in content


def test_monitoring_tab_reads_like_the_seminar_close() -> None:
    content = APP_SOURCE.read_text()
    monitoring_block = _extract_tab_block(content, "tab5")

    assert "Monitoring & Scenarios" in monitoring_block
    assert "render_research_module_intro(" in monitoring_block
    assert "render_takeaway_block(" in monitoring_block
    assert "**Short answer:**" not in monitoring_block
    assert "scorecard" in monitoring_block.lower()
    assert "If this, then that playbook" in monitoring_block
    assert "audience takeaways" in monitoring_block.lower()


def test_monitoring_playbook_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "If this, then that playbook" in content
    assert "Higher for longer" in content


def test_editorial_consistency_keeps_seminar_anchors_balanced() -> None:
    content = APP_SOURCE.read_text()
    monitoring_block = _extract_tab_block(content, "tab5")

    assert monitoring_block.count("**What to notice:**") >= 1
    assert "Audience Takeaways" in monitoring_block
    assert "**What to notice:**" in monitoring_block
    assert "render_takeaway_block(" in monitoring_block


def test_tabs_adopt_research_modules_takeaways_and_wrapped_diagnostics() -> None:
    content = APP_SOURCE.read_text()

    for tab_name in ["tab1", "tab2", "tab3", "tab4", "tab5"]:
        block = _extract_tab_block(content, tab_name)
        assert "render_research_module_intro(" in block
        assert "render_takeaway_block(" in block
        assert "**Short answer:**" not in block

    for tab_name in ["tab1", "tab2", "tab5"]:
        diagnostic_calls = _tab_call_nodes(content, tab_name, "render_diagnostic_band")
        assert diagnostic_calls
        assert any(
            any(keyword.arg == "body" for keyword in call.keywords) for call in diagnostic_calls
        )


def test_research_module_intros_replace_legacy_duplicate_subheaders() -> None:
    content = APP_SOURCE.read_text()

    duplicate_headings = [
        "Q1: Are banks sensitive to rate shocks?",
        "Q2: Is stress building in the system?",
        "Q8: Which regime are we in?",
        "Q3: Do policy events create abnormal returns?",
        "Q5: Does fear amplify the channel?",
        "Q6: How do shocks propagate over time?",
        "Q7: How do the variables co-move?",
        "Q1: Where do deposits go when spreads widen?",
        "Q2: What macro regime are we in?",
        "Q3: Is credit stress feeding back into banks?",
        "Q1: What conditions preceded the break?",
        "Q2: How did the market interpret the break?",
        "Q3: How does market interpretation map back to channel mechanics?",
        "Q4: What would have changed the outcome?",
        "Stress Test Simulation",
        "If this, then that playbook",
    ]

    for heading in duplicate_headings:
        assert content.count(f'st.subheader("{heading}")') == 0


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


def test_visual_system_guardrail_anchors_are_present_in_app_source() -> None:
    content = APP_SOURCE.read_text()

    for anchor in [
        "seminar-banner",
        "diagnostic-band",
        "research-module",
        "takeaway-block",
    ]:
        assert anchor in content


def test_visual_system_helpers_render_semantic_html() -> None:
    calls: list[tuple[str, bool]] = []

    class FakeStreamlit:
        def __init__(self) -> None:
            self.container_depth = 0
            self.container_events: list[str] = []

        def markdown(self, body: str, unsafe_allow_html: bool = False) -> None:
            calls.append((body, unsafe_allow_html))

        def container(self, border: bool = False):
            self.container_events.append(f"open:{border}")

            class _Container:
                def __enter__(inner_self):
                    fake_streamlit.container_depth += 1
                    return inner_self

                def __exit__(inner_self, exc_type, exc, tb):
                    fake_streamlit.container_depth -= 1
                    fake_streamlit.container_events.append("close")
                    return False

            return _Container()

    fake_streamlit = FakeStreamlit()
    render_seminar_banner = _load_app_helper(
        "render_seminar_banner", {"st": fake_streamlit, "html": html}
    )
    render_diagnostic_band = _load_app_helper(
        "render_diagnostic_band", {"st": fake_streamlit, "html": html}
    )
    render_terminal_summary_band = _load_app_helper(
        "render_terminal_summary_band", {"st": fake_streamlit, "html": html}
    )
    render_takeaway_block = _load_app_helper(
        "render_takeaway_block", {"st": fake_streamlit, "html": html}
    )

    def render_metric_surface() -> None:
        assert fake_streamlit.container_depth > 0
        fake_streamlit.markdown("<span>metric surface</span>", unsafe_allow_html=True)

    render_seminar_banner("Open <session>", "Framing & synthesis", "Answer <yes>")
    render_diagnostic_band(
        "Board",
        "Track the live read",
        "Use the scorecard first",
        body=render_metric_surface,
    )
    render_terminal_summary_band(
        "Transmission active but mixed",
        "Watch",
        "Empirical transmission broadening and monitoring stable, with mixed signals across the highest-weight tabs.",
        "Empirical Terminal for the live market evidence.",
        "Mixed signal across high-weight tabs",
    )
    render_takeaway_block("Lead with the surface <scan> before the narrative.")

    assert len(calls) == 5

    banner_body, banner_allow_html = calls[0]
    band_body, band_allow_html = calls[1]
    wrapped_surface_body, wrapped_surface_allow_html = calls[2]
    summary_body, summary_allow_html = calls[3]
    takeaway_body, takeaway_allow_html = calls[4]

    assert banner_allow_html is True
    assert '<div class="seminar-banner">' in banner_body
    assert "Research Seminar Module" in banner_body
    assert "Open &lt;session&gt;" in banner_body
    assert "Framing &amp; synthesis" in banner_body
    assert "<strong>Short answer:</strong> Answer &lt;yes&gt;" in banner_body

    assert band_allow_html is True
    assert fake_streamlit.container_events == ["open:True", "close"]
    assert '<div class="diagnostic-band">' in band_body
    assert "Diagnostic Band" in band_body
    assert "Board" in band_body
    assert "Track the live read" in band_body
    assert "<strong>Diagnostic note:</strong> Use the scorecard first" in band_body

    assert wrapped_surface_allow_html is True
    assert wrapped_surface_body == "<span>metric surface</span>"

    assert summary_allow_html is True
    assert '<div class="summary-band">' in summary_body
    assert "Top summary" in summary_body
    assert "Overall read" in summary_body
    assert "Action posture" in summary_body
    assert "Mixed signal across high-weight tabs" in summary_body

    assert takeaway_allow_html is True
    assert '<div class="takeaway-block">' in takeaway_body
    assert "Lead with the surface &lt;scan&gt; before the narrative." in takeaway_body
    assert "<strong>Takeaway:</strong>" in takeaway_body


def test_tabs_use_seminar_banners_and_diagnostic_bands() -> None:
    content = APP_SOURCE.read_text()

    assert content.count("render_seminar_banner(") >= 5
    assert content.count("render_diagnostic_band(") >= 5

    for tab_name in ["tab1", "tab2", "tab3", "tab4", "tab5"]:
        block = _extract_tab_block(content, tab_name)
        assert "render_seminar_banner(" in block
        assert "render_diagnostic_band(" in block


def test_future_navigation_anchors_are_not_missing_from_app_source() -> None:
    content = APP_SOURCE.read_text()

    for anchor in ["Jump to section", "Read this next", "Continue in"]:
        assert anchor in content


def test_tabs_include_section_navigator_helper_usage() -> None:
    content = APP_SOURCE.read_text()

    assert content.count("render_section_navigator(") >= 5

    for tab_name in ["tab1", "tab2", "tab3", "tab4", "tab5"]:
        block = _extract_tab_block(content, tab_name)
        assert "render_section_navigator(" in block


def test_navigation_layer_is_present_without_heavy_chrome() -> None:
    content = APP_SOURCE.read_text()
    module = ast.parse(content)

    navigator_calls = [
        node
        for node in ast.walk(module)
        if isinstance(node, ast.Call) and _call_name(node) == "render_section_navigator"
    ]
    continue_in_count = content.count("Continue in")
    read_next_count = content.count("Read this next")

    assert "Jump to section" in content
    assert len(navigator_calls) >= 5
    assert continue_in_count >= 3
    assert read_next_count >= 2
    assert "If you only look at one chart" in content
