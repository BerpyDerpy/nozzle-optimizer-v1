from motorlib.motor import Motor
from uilib.fileIO import loadFile, fileTypes 
import copy

MAX_PRESSURE_PSI = 1000
BATES_TEMPLATE = "template2.ric"
STAR_TEMPLATE = "templateStar.ric"

bates_template_file = loadFile(BATES_TEMPLATE, fileTypes.MOTOR)
bates_template_instance = Motor() 
bates_template_instance.applyDict(bates_template_file)

star_template_file = loadFile(STAR_TEMPLATE, fileTypes.MOTOR)
star_template_instance = Motor() 
star_template_instance.applyDict(star_template_file)

def simulate(grain, diameter,
             bates_core_diameter, bates_length,
             star_len, star_points, star_point_len, star_point_width,
             convAngle,divAngle, nozzle_throat, nozzle_throat_length):

    bates_motor = copy.deepcopy(bates_template_instance)
    star_motor = copy.deepcopy(star_template_instance)

    

    if grain == 0:
        bates_motor.grains[0].props['diameter'].setValue(diameter)
        bates_motor.grains[0].props['coreDiameter'].setValue(bates_core_diameter)
        bates_motor.grains[0].props['length'].setValue(bates_length)
        bates_motor.nozzle.props['convAngle'].setValue(convAngle)
        bates_motor.nozzle.props['divAngle'].setValue(divAngle)
        bates_motor.nozzle.props['throat'].setValue(nozzle_throat)
        bates_motor.nozzle.props['throatLength'].setValue(nozzle_throat_length)

        sim_result = bates_motor.runSimulation()
    
    elif grain == 1:
        star_motor.grains[0].props['diameter'].setValue(diameter)
        star_motor.grains[0].props['length'].setValue(star_len)
        star_motor.grains[0].props['numPoints'].setValue(star_points)
        star_motor.grains[0].props['pointLength'].setValue(star_point_len)
        star_motor.grains[0].props['pointWidth'].setValue(star_point_width)
        star_motor.nozzle.props['convAngle'].setValue(convAngle)
        star_motor.nozzle.props['divAngle'].setValue(divAngle)
        star_motor.nozzle.props['throat'].setValue(nozzle_throat)
        star_motor.nozzle.props['throatLength'].setValue(nozzle_throat_length)

        sim_result = star_motor.runSimulation()

    if not sim_result.success:
        return MAX_PRESSURE_PSI + 1, 0  # (pressure, impulse)
    max_pressure = sim_result.getMaxPressure()
    total_impulse = sim_result.getImpulse()

    return max_pressure* 0.000145038, total_impulse # (PSI, Ns)
