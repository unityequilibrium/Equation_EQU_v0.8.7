"""
📈 UET Time Series Prediction
=============================
Use UET dynamics (Cahn-Hilliard) to predict future values.

Key insight: UET says systems evolve to minimize free energy Ω.
So we can predict NEXT state by finding dC/dt from current C.

This is a BREAKTHROUGH test - if it works, UET can forecast!

Updated for UET V3.0
"""

import numpy as np

# Import from UET V3.0 Master Equation
import sys
from pathlib import Path
_root = Path(__file__).parent
while _root.name != "research_uet" and _root.parent != _root:
    _root = _root.parent
sys.path.insert(0, str(_root.parent))
try:
    from research_uet.core.uet_master_equation import (
        UETParameters, SIGMA_CRIT, strategic_boost, potential_V, KAPPA_BEKENSTEIN
    )
except ImportError:
    pass  # Use local definitions if not available

import matplotlib.pyplot as plt
from pathlib import Path

# Try to load real market data
# CORRECTED PATH: Points to the verified 'references/economy' folder
DATA_DIR = Path(__file__).parents[3] / "data" / "references" / "economy"


def load_market_data(symbol="SP500_yahoo_real.csv"):
    """Load real market data."""
    path = DATA_DIR / symbol
    if path.exists():
        import pandas as pd

        df = pd.read_csv(path)
        if "Close" in df.columns:
            prices = pd.to_numeric(df["Close"], errors="coerce").dropna().values
        elif "Price" in df.columns:
            prices = pd.to_numeric(df["Price"], errors="coerce").dropna().values
        else:
            prices = pd.to_numeric(df.iloc[:, 1], errors="coerce").dropna().values
        prices = prices.astype(float)
        print(f"✅ Loaded {symbol}: {len(prices)} data points")
        return prices
    else:
        print(f"⚠️ {symbol} not found, generating synthetic data")
        return generate_synthetic_market(1000)


def generate_synthetic_market(n=1000):
    """Generate synthetic market with UET dynamics."""
    np.random.seed(42)

    # Start with random walk
    returns = np.random.randn(n) * 0.01  # 1% daily vol

    # Add mean reversion (UET-like)
    prices = [100]
    for i in range(1, n):
        # UET: dC/dt = -dV/dC, where V = (C - C_eq)²
        C = prices[-1]
        C_eq = 100  # Equilibrium
        mean_rev = -0.01 * (C - C_eq) / C_eq

        noise = returns[i]
        new_price = C * (1 + mean_rev + noise)
        prices.append(max(new_price, 1))  # Prevent negative

    return np.array(prices)


def uet_predict_next(prices, window=20, kappa=0.1):
    """
    Predict next price using UET dynamics.

    UET says: dC/dt = -δΩ/δC

    For time series:
    - C(t) = current price
    - I(t) = volatility (hidden information)
    - V(C) = potential energy
    """
    if len(prices) < window:
        return prices[-1]

    recent = prices[-window:]

    # Calculate "chemical potential" μ = δΩ/δC
    C = recent[-1]
    C_mean = np.mean(recent)
    C_std = np.std(recent) + 1e-10

    # Potential: V(C) = (C - C_eq)² / 2
    # dV/dC = (C - C_eq)
    dV_dC = (C - C_mean) / C_std  # Normalized

    # Gradient term: -κ∇²C ≈ -κ(C - local_mean)
    local_mean = np.mean(recent[-5:])
    grad_term = -kappa * (C - local_mean) / C_std

    # Chemical potential
    mu = dV_dC + grad_term

    # Prediction: C_next = C - dt * dΩ/dC = C - dt * μ
    # But for Cahn-Hilliard: dC/dt = ∇²μ ≈ Δμ
    # Simpler: use momentum + mean reversion

    momentum = (recent[-1] - recent[-2]) / recent[-2] if len(recent) > 1 else 0
    mean_rev = -0.05 * (C - C_mean) / C_mean

    # Combine with UET weighting
    alpha = 0.3  # Mean reversion strength
    predicted_return = alpha * mean_rev + (1 - alpha) * momentum

    # Limit extreme predictions
    predicted_return = np.clip(predicted_return, -0.05, 0.05)

    C_next = C * (1 + predicted_return)
    return C_next


def run_prediction_test(prices, train_fraction=0.8):
    """
    Test UET prediction on historical data.

    Split data into train/test and evaluate.
    """
    n = len(prices)
    train_size = int(n * train_fraction)

    train = prices[:train_size]
    test = prices[train_size:]

    print(f"\nTrain: {train_size} points, Test: {len(test)} points")

    # Predict each test point
    predictions = []
    actuals = []

    window = train.tolist()

    for i, actual in enumerate(test):
        pred = uet_predict_next(np.array(window))
        predictions.append(pred)
        actuals.append(actual)
        window.append(actual)  # Add actual for next prediction

    predictions = np.array(predictions)
    actuals = np.array(actuals)

    return predictions, actuals


def evaluate_predictions(predictions, actuals):
    """Evaluate prediction quality."""

    # Direction accuracy
    pred_returns = np.diff(predictions) / predictions[:-1]
    actual_returns = np.diff(actuals) / actuals[:-1]

    direction_correct = np.sum(np.sign(pred_returns) == np.sign(actual_returns))
    direction_accuracy = direction_correct / len(pred_returns) * 100

    # RMSE
    rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
    rmse_pct = rmse / np.mean(actuals) * 100

    # MAPE
    mape = np.mean(np.abs(predictions - actuals) / actuals) * 100

    return {"direction_accuracy": direction_accuracy, "rmse_pct": rmse_pct, "mape": mape}


def run_test():
    print("=" * 70)
    print("📈 UET TIME SERIES PREDICTION TEST")
    print("=" * 70)
    print()
    print("Goal: Predict future prices using UET dynamics")
    print("Method: Cahn-Hilliard inspired mean reversion + momentum")
    print()

    # Test on multiple datasets (Real Data verified)
    datasets = ["SP500_yahoo_real.csv", "Bitcoin_yahoo_real.csv", "Gold_yahoo_real.csv"]

    results = []

    for dataset in datasets:
        print(f"\n{'='*50}")
        print(f"Testing: {dataset}")
        print("=" * 50)

        prices = load_market_data(dataset)

        if len(prices) < 100:
            print("⚠️ Not enough data, skipping")
            continue

        predictions, actuals = run_prediction_test(prices)
        metrics = evaluate_predictions(predictions, actuals)

        results.append({"dataset": dataset, **metrics})

        print(f"\nResults for {dataset}:")
        print(f"  Direction Accuracy: {metrics['direction_accuracy']:.1f}%")
        print(f"  RMSE: {metrics['rmse_pct']:.2f}%")
        print(f"  MAPE: {metrics['mape']:.2f}%")

        if metrics["direction_accuracy"] > 50:
            print("  ✅ Better than random!")
        else:
            print("  ❌ Worse than random")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if results:
        avg_direction = np.mean([r["direction_accuracy"] for r in results])
        avg_mape = np.mean([r["mape"] for r in results])

        print(f"\nAverage Direction Accuracy: {avg_direction:.1f}%")
        print(f"Average MAPE: {avg_mape:.2f}%")

        if avg_direction > 55:
            print("\n🎉 BREAKTHROUGH! UET can predict direction!")
        elif avg_direction > 50:
            print("\n✅ Slight edge over random")
        else:
            print("\n⚠️ No predictive power detected")

    # Plot last result
    if results:
        plt.figure(figsize=(12, 6))

        n_plot = min(100, len(predictions))
        plt.plot(actuals[-n_plot:], "b-", label="Actual", linewidth=2)
        plt.plot(predictions[-n_plot:], "r--", label="UET Prediction", linewidth=1.5)

        plt.title(f'UET Time Series Prediction - {results[-1]["dataset"]}')
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Save to current script directory to avoid path errors
        output_path = Path(__file__).parent / "time_series_prediction.png"
        plt.savefig(output_path, dpi=150)
        print(f"\nPlot saved: {output_path}")
        plt.close()


if __name__ == "__main__":
    run_test()
