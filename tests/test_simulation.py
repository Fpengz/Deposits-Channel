import pytest
from src.simulation import calculate_deposit_rate, calculate_deposit_volume, generate_rate_paths, generate_deposit_paths

def test_calculate_deposit_rate():
    # Fed funds rate 5%, market power index 0.5
    rate = calculate_deposit_rate(fed_funds_rate=0.05, market_power=0.5)
    # Expected: partial pass-through
    assert rate == 0.025

def test_calculate_deposit_volume():
    # Base volume 1000, spread 0.025, elasticity 10
    vol = calculate_deposit_volume(base_volume=1000, spread=0.025, elasticity=10)
    assert vol == 750.0

def test_generate_rate_paths_shape():
    paths = generate_rate_paths(current_rate=0.05, paths=9, days=252, seed=1)
    assert paths.shape == (9, 252)

def test_generate_deposit_paths_shape():
    paths = generate_rate_paths(current_rate=0.05, paths=9, days=10, seed=1)
    deposits = generate_deposit_paths(paths, market_power=0.5, base_volume=10000, elasticity=10)
    assert deposits.shape == (9, 10)
