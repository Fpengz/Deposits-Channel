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
    volume = base_volume - (elasticity * spread * 1000) # scale factor for realistic numbers
    return max(0.0, volume)
