"""
Prediction Market Expected Value (EV) & Kelly Bet Sizing Engine
Validates market implied probabilities vs model true probabilities.
"""
def compute_ev_and_kelly(implied_prob: float, model_prob: float, bankroll: float, fraction: float = 0.5):
    """
    implied_prob: Market price / probability (e.g., 0.45 for 45c share)
    model_prob: Fundamental modeled probability (e.g., 0.55)
    """
    if implied_prob <= 0 or implied_prob >= 1:
        return {"error": "Invalid market probability"}
        
    payout_odds = (1.0 - implied_prob) / implied_prob
    expected_value = (model_prob * payout_odds) - (1.0 - model_prob)
    
    # Kelly Formula: f* = (b*p - q) / b
    kelly_fraction = ((payout_odds * model_prob) - (1.0 - model_prob)) / payout_odds
    adjusted_kelly = max(0.0, kelly_fraction * fraction)
    recommended_bet = bankroll * adjusted_kelly
    
    return {
        "positive_ev": expected_value > 0,
        "edge_percentage": round(expected_value * 100, 2),
        "kelly_stake_pct": round(adjusted_kelly * 100, 2),
        "recommended_allocation_usd": round(recommended_bet, 2)
    }

if __name__ == "__main__":
    result = compute_ev_and_kelly(0.42, 0.54, 10000.0)
    print("EV Analysis:", result)
