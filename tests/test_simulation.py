import pytest
from src.simulation import calculate_deposit_rate, calculate_deposit_volume

def test_calculate_deposit_rate():
    # Fed funds rate 5%, market power index 0.5
    rate = calculate_deposit_rate(fed_funds_rate=0.05, market_power=0.5)
    # Expected: partial pass-through
    assert rate == 0.025

def test_calculate_deposit_volume():
    # Base volume 1000, spread 0.025, elasticity 10
    vol = calculate_deposit_volume(base_volume=1000, spread=0.025, elasticity=10)
    assert vol == 750.0
