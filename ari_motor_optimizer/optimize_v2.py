import os
import sys
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import joblib
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
import time

# --- 1. SETUP: LOAD AI MODEL AND SCALERS ---

class MotorSurrogate(nn.Module):
    def __init__(self, num_inputs, num_outputs):
        super(MotorSurrogate, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(num_inputs, 128), nn.ReLU(),
            nn.Linear(128, 256), nn.ReLU(),
            nn.Linear(256, 128), nn.ReLU(),
            nn.Linear(128, num_outputs)
        )
    def forward(self, x):
        return self.network(x)

# --- Base directory (always the folder where this script is) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_FILE = os.path.join(BASE_DIR, "model_surrogate.pth")
SCALER_X_FILE = os.path.join(BASE_DIR, "X_scaler")
SCALER_Y_FILE = os.path.join(BASE_DIR, "y_scaler")

# --- File existence checks ---
for f in [MODEL_FILE, SCALER_X_FILE, SCALER_Y_FILE]:
    if not os.path.exists(f):
        print(f"❌ Missing file: {f}")
        sys.exit(1)

INPUT_FEATURES = [
    "diameter", "bates_core_dia", "bates_len", "nozzle_convAngle",
    "nozzle_divAngle", "nozzle_expansion_ratio", "nozzle_throat_dia",
    "nozzle_throat_len"
]

# --- Load the trained model and the scalers ---
device = torch.device('cpu')
model = MotorSurrogate(len(INPUT_FEATURES), 4)
model.load_state_dict(torch.load(MODEL_FILE, map_location=device))
model.to(device)
model.eval()
print("✅ AI Surrogate Model loaded successfully.")

X_scaler = joblib.load(SCALER_X_FILE)
y_scaler = joblib.load(SCALER_Y_FILE)
print("✅ Data scalers loaded successfully via joblib.")

# Define the problem constraints
MAX_PRESSURE_PSI = 1000
MAX_MASS_FLUX_LIMIT = 1406.47

# Define the problem constraints
MAX_PRESSURE_PSI = 1000
MAX_MASS_FLUX_LIMIT = 1406.47

# --- 2. AI-POWERED PREDICTION FUNCTION ---

def predict_performance(design_dict):
    input_array = np.array([design_dict[key] for key in INPUT_FEATURES]).reshape(1, -1)
    input_scaled = X_scaler.transform(input_array)
    input_tensor = torch.tensor(input_scaled, dtype=torch.float32).to(device)
    
    with torch.no_grad():
        prediction_scaled = model(input_tensor)
        
    prediction = y_scaler.inverse_transform(prediction_scaled.cpu().numpy())
    return prediction[0]

# --- 3. MODIFIED PYMOO PROBLEM ---
BATESgene = {
    "diameter": (0.015, 0.025), "bates_core_dia": (0.005, 0.012),
    "bates_len": (0.08, 0.15), "nozzle_convAngle": (30, 45),
    "nozzle_divAngle": (12, 15), "nozzle_expansion_ratio": (3.0, 6.0),
    "nozzle_throat_dia": (0.004, 0.008), "nozzle_throat_len": (0.008, 0.012)
}

class MotorProblem(ElementwiseProblem):
    def __init__(self, params, xl, xu):
        super().__init__(n_var=len(params), n_obj=1, n_ieq_constr=3, xl=xl, xu=xu)
        self.params = params

    def _evaluate(self, x, out, *args, **kwargs):
        design = dict(zip(self.params, x))
        pressure, impulse, port_ratio, peak_massflux_ratio = predict_performance(design)
        out['F'] = -impulse
        out['G'] = [pressure - MAX_PRESSURE_PSI,
                    2.0 - port_ratio,
                    peak_massflux_ratio - MAX_MASS_FLUX_LIMIT]

# --- 4. RUN THE OPTIMIZATION ---
if __name__ == "__main__":
    start_time = time.time()
    print("\n============ Starting BATES Optimization (PyTorch + Joblib Powered) ============")
    bates_params = list(BATESgene.keys())
    bates_xl = [BATESgene[key][0] for key in bates_params]
    bates_xu = [BATESgene[key][1] for key in bates_params]
    bates_problem = MotorProblem(params=bates_params, xl=bates_xl, xu=bates_xu)
    bates_algorithm = NSGA2(pop_size=200)
    bates_res = minimize(
        problem=bates_problem,
        algorithm=bates_algorithm,
        termination=("n_gen", 100),
        seed=1,
        verbose=True
    )
    end_time = time.time()
    print("============ ✨ BATES OPTIMIZATION DONE ✨ ============")
    print(f"Execution Time: {(end_time - start_time):.2f} seconds")
    print("\n🏆 Final Results: ")
    print(f"Best BATES impulse: {-bates_res.F[0]:.2f} Ns")
    print("Winning Parameters: ", dict(zip(bates_params, bates_res.X)))