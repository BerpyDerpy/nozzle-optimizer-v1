import streamlit as st
import numpy as np
import time
from optimize_v2 import MotorProblem, BATESgene, predict_performance
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
import matplotlib.pyplot as plt


st.title("Motor optimizer")

# --- User inputs ---
target_impulse = st.number_input("Desired Impulse (Ns)", min_value=0.0, value=50.0, step=1.0)

pop_size = st.slider("Population Size", min_value=50, max_value=500, value=200, step=50)
n_gen = st.slider("Number of Generations", min_value=10, max_value=300, value=100, step=10)

st.subheader("🔧 Parameter Ranges")
ranges = {}
for param, (low, high) in BATESgene.items():
    col1, col2 = st.columns(2)
    with col1:
        min_val = st.number_input(f"{param} min", value=float(low))
    with col2:
        max_val = st.number_input(f"{param} max", value=float(high))
    ranges[param] = (min_val, max_val)

if st.button("Run"):
    start_time = time.time()
    params = list(ranges.keys())
    xl = [ranges[k][0] for k in params]
    xu = [ranges[k][1] for k in params]

    problem = MotorProblem(params=params, xl=xl, xu=xu)
    algorithm = NSGA2(pop_size=pop_size)

    with st.spinner("Running optimization..."):
        res = minimize(
            problem=problem,
            algorithm=algorithm,
            termination=("n_gen", n_gen),
            seed=1,
            verbose=True,
            save_history=True  # <-- enables res.history
        )

    end_time = time.time()

    # Extract best impulse from final result

    best_impulse = float(-res.F[0])

    # Fix for res.X being 2D in some cases
    X = res.X[0] if res.X.ndim > 1 else res.X
    best_params = {k: float(v) for k, v in zip(params, X)}

    st.success("Optimization done")
    st.write(f"⏱ Execution Time: {(end_time - start_time):.2f} seconds")
    st.write(f"🏆 Best Impulse: {best_impulse:.2f} Ns")
    st.write("Winning Parameters:", best_params)


    if target_impulse > 0:
        diff = abs(best_impulse - target_impulse)
        st.write(f"Difference from target impulse ({target_impulse} Ns): {diff:.2f} Ns")

    # --- Convergence Plot ---

    best_impulses = []
    for algo in res.history:
        F = algo.opt.get("F")  # objective values of best individuals
        best_val = F.min()     # best one if multiple
        best_impulses.append(float(-best_val))  # negate since we minimize -impulse

    fig, ax = plt.subplots()
    ax.plot(range(1, len(best_impulses) + 1), best_impulses, marker="o")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best Impulse (Ns)")
    ax.set_title("Convergence Curve")

    # Optional: plot target impulse for reference
    if target_impulse > 0:
        ax.axhline(y=target_impulse, color="red", linestyle="--", label="Target Impulse")
        ax.legend()

    st.pyplot(fig)

