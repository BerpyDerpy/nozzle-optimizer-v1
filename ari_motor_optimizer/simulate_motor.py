from motorlib.motor import Motor
from uilib.fileIO import loadFile, fileTypes 
import copy

MAX_PRESSURE_PSI = 1000
TEMPLATE = "template2.ric"

motor_template_file = loadFile(TEMPLATE, fileTypes.MOTOR)
motor_template_instance = Motor() 
motor_template_instance.applyDict(motor_template_file)

def simulate(core_diameter, grain_length,convAngle,divAngle, nozzle_throat, nozzle_throat_length):

    motor = copy.deepcopy(motor_template_instance)

    motor.grains[0].props['coreDiameter'].setValue(core_diameter)
    motor.grains[0].props['length'].setValue(grain_length)
    motor.nozzle.props['convAngle'].setValue(convAngle)
    motor.nozzle.props['divAngle'].setValue(divAngle)
    motor.nozzle.props['throat'].setValue(nozzle_throat)
    motor.nozzle.props['throatLength'].setValue(nozzle_throat_length)

    sim_result = motor.runSimulation()

    if not sim_result.success:
        return MAX_PRESSURE_PSI + 1, 0  # (pressure, impulse)
    max_pressure = sim_result.getMaxPressure()
    total_impulse = sim_result.getImpulse()

    return max_pressure* 0.000145038, total_impulse # (PSI, Ns)
