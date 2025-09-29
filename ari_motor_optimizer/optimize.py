from random import seed
from tabnanny import verbose
from token import STAR
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.variable import Real,Integer
from pymoo.optimize import minimize
import numpy as np
import os

from motorlib.motor import Motor
from simulate_motor import simulate, MAX_PRESSURE_PSI, MAX_MASS_FLUX_LIMIT

BATESgene = {
    "diameter": (0.015, 0.025),  
    "bates_core_dia": (0.005, 0.012),  
    "bates_len": (0.08, 0.15),  
    "nozzle_convAngle": (30, 45),  
    "nozzle_divAngle": (12, 15),  
    "nozzle_expansion_ratio": (3.0, 6.0),  
    "nozzle_throat_dia": (0.004, 0.008),  
    "nozzle_throat_len": (0.008, 0.012)  
}

STARgene = {
    "diameter": (0.015, 0.025),  
    "star_len": (0.08, 0.15),  
    "star_points": (4, 6),  
    "star_point_len": (0.002, 0.008),  
    "star_point_width": (0.002, 0.005),  
    "nozzle_convAngle": (30, 45),  
    "nozzle_divAngle": (12, 15),  
    "nozzle_expansion_ratio": (3.0, 6.0), 
    "nozzle_throat_dia": (0.004, 0.008), 
    "nozzle_throat_len": (0.008, 0.012) 
}

BATESvar_types = [
    Real(bounds=BATESgene['diameter']),          # (0.01,0.03)
    Real(bounds=BATESgene['bates_core_dia']),    # (0.005,0.03)
    Real(bounds=BATESgene['bates_len']),
    Integer(bounds=BATESgene['nozzle_convAngle']),
    Integer(bounds=BATESgene['nozzle_divAngle']),
    Real(bounds=BATESgene['nozzle_expansion_ratio']),
    Real(bounds=BATESgene['nozzle_throat_dia']),
    Real(bounds=BATESgene['nozzle_throat_len'])
]

STARvar_types = [
    Real(bounds=STARgene['star_len']),
    Integer(bounds=STARgene['star_points']),    # (3,8)
    Real(bounds=STARgene['star_point_len']),
    Real(bounds=STARgene['star_point_width']),
    Integer(bounds=STARgene['nozzle_convAngle']),
    Integer(bounds=STARgene['nozzle_divAngle']),
    Real(bounds=STARgene['nozzle_expansion_ratio']),
    Real(bounds=STARgene['nozzle_throat_dia']),
    Real(bounds=STARgene['nozzle_throat_len'])
]

n_obj = 1

class MotorProblem(ElementwiseProblem):

    def __init__(self, params, xl, xu, grain_type):
        super().__init__(n_var = len(params),
                         n_obj = n_obj,
                         n_ieq_constr = 4,
                         xl = xl,
                         xu = xu)
        self.params = params
        self.grain_type = grain_type
                         

    def _evaluate(self, x, out, *args, **kwargs):

        design = dict(zip(self.params,x))
    
        pressure, impulse, port_ratio, peak_massflux_ratio, exit_pressure_ratio = simulate(design, self.grain_type)

        # -- Objectives --
        out['F'] = -impulse #minimize negative of impulses aka maximize | 'F' is for objectives

        # -- Constraints --
        g1 = pressure - MAX_PRESSURE_PSI  # Pressure constraint
        g2 = 2.0 - port_ratio     # Port/Throat constraint
        g3 = peak_massflux_ratio - MAX_MASS_FLUX_LIMIT # Mass flux constraint
        g4 = 0.1 - exit_pressure_ratio   # Flow separation constraint

        out['G'] = [g1, g2, g3, g4] # 'G" is for constraints | fails if constraint <= 0


if __name__ == "__main__":

    
    print("============ Starting BATES Optimization ============")
    bates_params = list(BATESgene.keys())  #.keys() returns view object -> convert to list
    print(f"Current settings: no.of parameters : {len(bates_params)} || no. of objectives : {n_obj}\n")

    bates_xl = [BATESgene[key][0] for key in bates_params]
    bates_xu = [BATESgene[key][1] for key in bates_params]

    bates_problem = MotorProblem(params=bates_params, xl=bates_xl, xu = bates_xu,grain_type='bates')
    bates_algorithm = NSGA2(pop_size=50)

    bates_res = minimize(problem=bates_problem,
                         algorithm=bates_algorithm,
                         termination=("n_gen",40),
                         seed = 1,
                         verbose = True)
    
    print("============ ✨ BATES OPTIMIZATION DONE ✨ ============")
    print(f"{bates_res.exec_time:.2f} seconds")
       
    print("============ ⭐️ Starting STAR Optimization ============")
    star_params = list(STARgene.keys())
    print(f"Current settings: no.of parameters : {len(bates_params)} || no. of objectives : {n_obj}\n")

    star_xl = [STARgene[key][0] for key in star_params]
    star_xu = [STARgene[key][1] for key in star_params]
    
    star_problem = MotorProblem(params = star_params, xl = star_xl, xu = star_xu, grain_type='star')
    star_algorithm = NSGA2(pop_size=40)

    star_res = minimize(problem=star_problem,
                        algorithm=star_algorithm,
                        termination=("n_gen",50),
                        seed = 1,
                        verbose = True)
    
    print("============ ✨ STAR OPTIMIZATION DONE ✨ ============")
    print(f"{star_res.exec_time:.2f} seconds")

    print("=======================")
    print("🏆 Final Results: ")

    best_bates_imp = -bates_res.F[0]
    best_star_imp = -star_res.F[0]

    print(f"Best BATES impulse: {best_bates_imp:.2f} Ns")
    print(f"Best STAR impulse: {best_star_imp:.2f} Ns")
  
    if best_bates_imp > best_star_imp:
        print("\n Recommended: BATES grain")
        best_params = dict(zip(bates_params,bates_res.X))


    else:
        print("\n Recommended: STAR grain")
        best_params = dict(zip(star_params, star_res.X))

    print("Winning Parameters: ", best_params)
    