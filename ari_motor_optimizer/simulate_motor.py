from motorlib.motor import Motor
from uilib.fileIO import loadFile, fileTypes 
import copy

MAX_PRESSURE_PSI = 1000
BATES_TEMPLATE = "ari_motor_optimizer/template2.ric"
STAR_TEMPLATE = "ari_motor_optimizer/templateStar.ric"

bates_template_file = loadFile(BATES_TEMPLATE, fileTypes.MOTOR)
bates_template_instance = Motor() 
bates_template_instance.applyDict(bates_template_file)

star_template_file = loadFile(STAR_TEMPLATE, fileTypes.MOTOR)
star_template_instance = Motor() 
star_template_instance.applyDict(star_template_file)

def simulate(design):


    grain = round(design['grain_type'])

    if grain == 0:
        motor = copy.deepcopy(bates_template_instance)
        
        motor.grains[0].props['coreDiameter'].setValue(design['bates_core_dia'])
        motor.grains[0].props['length'].setValue(design['bates_len'])
        
    
    elif grain == 1:
        motor = copy.deepcopy(star_template_instance)
        motor.grains[0].props['length'].setValue(design['star_len'])
        motor.grains[0].props['numPoints'].setValue(design['star_points'])
        motor.grains[0].props['pointLength'].setValue(design['star_point_len'])
        motor.grains[0].props['pointWidth'].setValue(design['star_point_width'])
    
    motor.grains[0].props['diameter'].setValue(design['diameter'])
    motor.nozzle.props['convAngle'].setValue(design['nozzle_convAngle'])
    motor.nozzle.props['divAngle'].setValue(design['nozzle_divAngle'])
    motor.nozzle.props['throat'].setValue(design['nozzle_throat_dia'])
    motor.nozzle.props['exit'].setValue(design['nozzle_exit_dia'])
    motor.nozzle.props['throatLength'].setValue(design['nozzle_throat_len'])

    try:
        sim_result = motor.runSimulation()
    except:
        return MAX_PRESSURE_PSI + 1, 0 
    
    if not sim_result.success:
        return MAX_PRESSURE_PSI + 1, 0  # (pressure, impulse)
    max_pressure = sim_result.getMaxPressure()
    total_impulse = sim_result.getImpulse()

    return max_pressure* 0.000145038, total_impulse # (PSI, Ns)
