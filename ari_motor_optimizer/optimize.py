from random import seed
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.variable import Real,Integer
from pymoo.optimize import minimize
import numpy as np
import os

from simulate_motor import simulate, MAX_PRESSURE_PSI

gene = {
            "grain_type" : (0,1), # Bates - 0, Star - 1
            "diameter" : (0.01, 0.03),
            "bates_core_dia" : (0.005, 0.03),
            "bates_len" : (0.05, 0.2 ),
            "star_len" : (0.05,0.20),
            "star_points" : (3,8),
            "star_point_len" : (0.005,0.03),
            "star_point_width" : (0.003,0.008),
            "nozzle_convAngle" : (20,60),
            "nozzle_divAngle" : (12,18),
            "nozzle_exit_dia" : (0.004,0.025),
            "nozzle_throat_dia" : (0.003,0.015),
            "nozzle_throat_len" : (0.006,0.015)
        }

params = list(gene.keys())
xl = np.array([gene[key][0] for key in params])
xu = np.array([gene[key][1] for key in params])

n_obj = 1

class MotorProblem(ElementwiseProblem):

    def __init__(self):
        super().__init__(n_var=len(params),
                         n_obj = n_obj,
                         n_ieq_constr = 1,
                         xl = xl,
                         xu = xu,
                         )

    def _evaluate(self, x, out, *args, **kwargs):

        design = dict(zip(params,x))
        
        # rounding the stuff to integers since optimizer gives values as float 
        design['grain_type'] = round(design['grain_type'])
        design['star_points'] = round(design['star_points'])
        design['nozzle_convAngle'] = round(design['nozzle_convAngle'])
        design['nozzle_divAngle'] = round(design['nozzle_divAngle'])

        pressure, impulse = simulate(design)

        out['F'] = -impulse #minimize negative of impulses aka maximize | 'F' is for objectives
        out['G'] = pressure - MAX_PRESSURE_PSI # 'G" is for constraints | fails if constraint <= 0


if __name__ == "__main__":

    initial_guess = np.array([[
        1.0,      # grain_type (1 for Star)
        0.03,     # diameter
        0.005,    # bates_core_dia 
        0.20,     # bates_len 
        0.20,     # star_len
        4.0,      # star_points
        0.005,    # star_point_len
        0.003,    # star_point_width
        37.0,     # nozzle_convAngle
        16.0,     # nozzle_divAngle
        0.01653,  # nozzle_exit_dia
        0.0069,   # nozzle_throat_dia
        0.00785   # nozzle_throat_len
    ]])

    problem = MotorProblem()
    algorithm = NSGA2(pop_size=40,
                      sampling = initial_guess)

    os.system("clear")
    print("========= Starting Optimization =========")
    print(f"Current settings: no.of parameters : {len(params)} || no. of objectives : {n_obj}\n")
    
   

    optimRES = minimize(problem=problem,
                        algorithm=algorithm,
                        termination=("n_gen",40),
                        verbose=True,
                        seed = 1)
    
    print("Cha-ching | ✅ Optimization done!")
    print(f"{optimRES.exec_time:.2f} seconds")
    print("=======================")

    if optimRES is not None:
        best_params = dict(zip(params,optimRES.X))
        best_performance = optimRES.F
        print(f"🏆 Best Design Found:")
        print(f"Diameter : {best_params['diameter']*1000:.2f} mm")
        print(f"Nozzle convergence Angle : {round(best_params['nozzle_convAngle'])} degrees")
        print(f"Nozzle divergence angle : {round(best_params['nozzle_divAngle'])} degrees")
        print(f"Nozzle throat diameter : {best_params['nozzle_throat_dia']*1000:.2f} mm")
        print(f"Nozzle exit diameter : {best_params['nozzle_exit_dia']*1000:.2f} mm")
        print(f"Nozzle throat length : {best_params['nozzle_throat_len']*1000:.2f} mm")

        if round(best_params['grain_type']) == 0:

            print(f"Grain  : BATES")
            print(f"Core diameter : {best_params['bates_core_dia']*1000:.2f} mm")
            print(f"Grain length : {best_params['bates_len']*1000:.2f} mm")
        
        elif round(best_params['grain_type']) == 1:
            print(f"Grain  : Star")
            print(f"Grain length : {best_params['star_len']*1000:.2f} mm")
            print(f"Num points : {round(best_params['star_points'])}")
            print(f"Star point length : {best_params['star_point_len']*1000:.2f} mm")
            print(f"Star point width : {best_params['star_point_width']*1000:.2f} mm")

        print("=======================")
        print(f"Achieved impulse : {-best_performance[0]:.2f} Ns")

        print("========= Simulating with best params =========")
        sim_params = simulate(best_params)
        print(f"Pressure : {sim_params[0]:.2f} PSI")
        print(f"Impulse : {sim_params[1]:.2f} Ns")