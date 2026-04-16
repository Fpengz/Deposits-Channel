import numpy as np

from src.analysis import calculate_bond_portfolio_loss


def calculate_deposit_rate(fed_funds_rate: float, market_power: float) -> float:
    """
    Calculate the deposit rate given the fed funds rate and bank market power.
    Higher market power means a lower deposit rate relative to fed funds.
    """
    # Simple model: deposit rate = f * (1 - market_power)
    return fed_funds_rate * (1.0 - market_power)


def calculate_deposit_volume(base_volume: float, spread: float, elasticity: float) -> float:
    """
    Calculate total deposit volume.
    As the spread (fed_funds - deposit_rate) widens, volume decreases due to elasticity.
    """
    # Simple linear demand: D = D_base - elasticity * spread
    # Ensure volume doesn't go below 0
    volume = base_volume - (elasticity * spread * 1000)  # scale factor for realistic numbers
    return max(0.0, volume)


def generate_rate_paths(
    current_rate: float, paths: int = 9, days: int = 252, vol: float = 0.0005, seed: int = 42
):
    """Generates random walk rate paths."""
    rng = np.random.default_rng(seed)
    shocks = rng.normal(0, vol, size=(paths, days))
    rates = current_rate + shocks.cumsum(axis=1)
    rates = np.clip(rates, 0.0, None)
    return rates


def generate_deposit_paths(rate_paths, market_power: float, base_volume: float, elasticity: float):
    """Calculates deposit volume paths given rate paths."""
    deposit_paths = []
    for path in rate_paths:
        vols = []
        for rate in path:
            dep_rate = calculate_deposit_rate(rate, market_power)
            spread = rate - dep_rate
            vols.append(calculate_deposit_volume(base_volume, spread, elasticity))
        deposit_paths.append(vols)
    return np.array(deposit_paths)


def counterfactual_channel_impact(
    deposit_outflow: float,
    rate_change: float,
    duration: float,
    deposit_friction: float,
    bond_base_value: float = 60.0,
) -> dict[str, float]:
    adjusted_outflow = deposit_outflow * (1.0 - deposit_friction)
    aoci_loss = abs(
        calculate_bond_portfolio_loss(
            base_value=bond_base_value,
            rate_change=rate_change,
            duration=duration,
        )
    )
    total_impact = adjusted_outflow + aoci_loss
    return {
        "deposit_outflow": adjusted_outflow,
        "aoci_loss": aoci_loss,
        "total_impact": total_impact,
    }
