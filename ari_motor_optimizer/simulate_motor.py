from motorlib.motor import Motor
from uilib.fileIO import loadFile, fileTypes 
import copy

MAX_PRESSURE_PSI = 1000
MAX_MASS_FLUX_LIMIT = 1406.4697609001405 # change later (picked up from template file)
BATES_TEMPLATE = "ari_motor_optimizer/template2.ric"
STAR_TEMPLATE = "ari_motor_optimizer/templateStar.ric"

bates_template_file = loadFile(BATES_TEMPLATE, fileTypes.MOTOR)
bates_template_instance = Motor() 
bates_template_instance.applyDict(bates_template_file)

star_template_file = loadFile(STAR_TEMPLATE, fileTypes.MOTOR)
star_template_instance = Motor() 
star_template_instance.applyDict(star_template_file)

def simulate(design, grain_type):
    # Input validation and bounds checking
    try:
        # Validate core design parameters
        if grain_type == 'bates':
            if design['bates_core_dia'] >= design['diameter']:
                return MAX_PRESSURE_PSI + 1, 0, 0, MAX_MASS_FLUX_LIMIT + 1, 0
        elif grain_type == 'star':
            # Ensure star geometry is physically reasonable
            if design['star_point_len'] >= design['diameter']/2:
                return MAX_PRESSURE_PSI + 1, 0, 0, MAX_MASS_FLUX_LIMIT + 1, 0
        
        # Ensure nozzle throat is smaller than grain diameter
        if design['nozzle_throat_dia'] >= design['diameter']:
            return MAX_PRESSURE_PSI + 1, 0, 0, MAX_MASS_FLUX_LIMIT + 1, 0
            
        # Ed = Td * sqrt(Ae/At)
        exit_dia = design['nozzle_throat_dia'] * (design['nozzle_expansion_ratio'] ** 0.5)
        
        # Ensure exit diameter is reasonable
        if exit_dia > design['diameter'] * 2:  # Sanity check
            return MAX_PRESSURE_PSI + 1, 0, 0, MAX_MASS_FLUX_LIMIT + 1, 0

        if grain_type == 'bates':
            motor = copy.deepcopy(bates_template_instance)
            motor.grains[0].props['coreDiameter'].setValue(design['bates_core_dia'])
            motor.grains[0].props['length'].setValue(design['bates_len'])

        elif grain_type == 'star':
            motor = copy.deepcopy(star_template_instance)
            motor.grains[0].props['length'].setValue(design['star_len'])
            motor.grains[0].props['numPoints'].setValue(int(design['star_points']))
            motor.grains[0].props['pointLength'].setValue(design['star_point_len'])
            motor.grains[0].props['pointWidth'].setValue(design['star_point_width'])
        
        # Common params for every template
        motor.grains[0].props['diameter'].setValue(design['diameter'])
        motor.nozzle.props['convAngle'].setValue(int(design['nozzle_convAngle']))
        motor.nozzle.props['divAngle'].setValue(int(design['nozzle_divAngle']))
        motor.nozzle.props['throat'].setValue(design['nozzle_throat_dia'])
        motor.nozzle.props['exit'].setValue(exit_dia)
        motor.nozzle.props['throatLength'].setValue(design['nozzle_throat_len'])

        # Suppress warnings during simulation for cleaner output
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sim_result = motor.runSimulation()
            
        if not sim_result.success:
            return MAX_PRESSURE_PSI + 1, 0, 0, MAX_MASS_FLUX_LIMIT + 1, 0
            
    except Exception as e:
        # Don't print every exception to reduce noise
        return MAX_PRESSURE_PSI + 1, 0, 0, MAX_MASS_FLUX_LIMIT + 1, 0

    try:
        max_pressure = sim_result.getMaxPressure() * 0.000145038  # Pa to PSI
        total_impulse = sim_result.getImpulse()  # Ns
        port_throat_ratio = sim_result.getPortRatio()
        peak_massflux_ratio = sim_result.getPeakMassFlux()
        exit_pressure_ratio = sim_result.getMinExitPressure()/motor.config.props['ambPressure'].getValue()
        
        # Additional validation of results
        if any(x != x for x in [max_pressure, total_impulse, port_throat_ratio, peak_massflux_ratio, exit_pressure_ratio]):  # Check for NaN
            return MAX_PRESSURE_PSI + 1, 0, 0, MAX_MASS_FLUX_LIMIT + 1, 0
            
        return max_pressure, total_impulse, port_throat_ratio, peak_massflux_ratio, exit_pressure_ratio
        
    except Exception as e:
        return MAX_PRESSURE_PSI + 1, 0, 0, MAX_MASS_FLUX_LIMIT + 1, 0