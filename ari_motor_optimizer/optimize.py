from random import seed
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
import numpy as np
import os

from simulate_motor import simulate, MAX_PRESSURE_PSI


class MotorProblem(Problem):

    def _evaluate(self, designs, out, *args, **kwargs):

        res = []

        for design in designs:
            d,l,t,cA,dA,tl = design
            res.append(simulate(d,l,t,cA,dA,tl))
        
        res = np.array(res) # pymoo operates in numpy shiz

        pressures = res[:,0]
        impulses = res[:,1]

        out['F'] = -impulses #minimize negative of impulses aka maximize | 'F' is for objectives
        out['G'] = pressures - MAX_PRESSURE_PSI # 'G" is for constraints | fails if constraint <= 0


if __name__ == "__main__":

    n_params = 6 #core dia, grain length and nozzle throat
    n_obj = 1 # maximise total impulse
    problem = MotorProblem(n_var = n_params,
                           n_obj = n_obj,
                           n_ieq_constr=1,
                           xl=np.array([0.005, 0.05,20,12, 0.003,0.2*0.003]),
                           xu=np.array([0.03, 0.20,60,18, 0.015, 0.5*0.015]))
    algorithm = NSGA2(pop_size=40)
    os.system("clear")
    print("========= Starting Optimization =========")
    print(f"Current settings: no.of parameters : {n_params} || no. of objectives : {n_obj}")
    

    optimRES = minimize(problem=problem,
                        algorithm=algorithm,
                        termination=("n_gen",40),
                        verbose=True,
                        seed = 1)
    
    print("Cha-ching | ✅ Optimization done!")
    print(f"{optimRES.exec_time:.2f} seconds")
    print("=======================")

    if optimRES is not None:
        best_params = optimRES.X
        best_performance = optimRES.F
        print(f"🏆 Best Design Found:")
        print(f"Core diameter : {best_params[0]*1000:.2f} mm")
        print(f"Grain length : {best_params[1]*100:.2f} cm")
        print(f"Nozzle convergence Angle : {best_params[2]:.2f} degrees")
        print(f"Nozzle divergence angle : {best_params[3]:.2f} degrees")
        print(f"Nozzle throat diameter : {best_params[4]*1000:.2f} mm")
        print(f"Nozzle throat length : {best_params[5]*1000:.2f} mm")
        print("=======================")
        print(f"Achieved impulse : {-best_performance[0]:.2f} Ns")

        print("========= Simulating with best params =========")
        sim_params = simulate(best_params[0],best_params[1],best_params[2],best_params[3],best_params[4],best_params[5])
        print(f"Pressure : {sim_params[0]:.2f} PSI")
        print(f"Impulse : {sim_params[1]:.2f} Ns")