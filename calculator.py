# calculator.py
# Tank factors for single tanks
TANK_FACTORS = {
    "AL40": 1.25,
    "AL80": 2.5,
    "LP80": 3.0,
    "LP83": 3.5,
    "LP95": 4.0,
    "LP104": 4.3,
    "LP120": 4.5,
    "HP80": 2.3,
    "HP100": 3.0,
    "HP120": 3.5,
    "HP130": 4.0
}

def calculate_minimum_gas(sac, depth, tank, config):
    """
    Calculate minimum gas needed in PSI based on SAC rate, depth, and tank config.
    """
    try:
        sac = float(sac)
        depth = float(depth)
        factor = TANK_FACTORS[tank]

        if config == "double":
            factor *= 2

        ata_avg = (depth / 2 / 33) + 1
        ascent_time = (depth / 10) + 1  # 10 ft/min ascent + 1 min safety _ the limit is 30ft/min
        min_gas_cf = sac * 2 * ata_avg * ascent_time
        min_gas_psi = min_gas_cf / factor * 100

        if min_gas_psi < 500:
            min_gas_psi = 500

        return min_gas_psi, ata_avg

    except (KeyError, ValueError, TypeError) as e:
        raise ValueError("Invalid input") from e


def calculate_turn_data(start_pressure, minimum_gas, tank, config, sac, depth):
    """
    Calculates usable gas, turn pressure, gas before turn (cf), and time before turn.
    """
    if start_pressure <= minimum_gas:
        raise ValueError("Start pressure must be greater than minimum gas.")
    usable_gas = start_pressure - minimum_gas
    turn_pressure = start_pressure  - (usable_gas /2 ) 

    factor = TANK_FACTORS[tank]
    if config == "double":
        factor *= 2

    ata_depth = (depth / 33) + 1
    consumption_rate = sac * ata_depth  # cf/min
    gas_before_turn_psi = start_pressure - turn_pressure
    gas_before_turn_cuft = (gas_before_turn_psi * factor) / 100
    time_before_turn = gas_before_turn_psi / (consumption_rate / factor*100)
    total_duration = usable_gas / (consumption_rate / factor * 100 )
    time_descending = depth / 30 +1 # descending at the rate 30ft per min 
    time_ascending = (depth / 10) + 1  # 10 ft/min ascent + 1 min safety _ the limit is 30ft/min
    if turn_pressure <= minimum_gas or gas_before_turn_psi <= minimum_gas:
        raise ValueError("The gas tank type/ starting pressure is not suitable for this dive.")
    return {
        "turn_pressure": turn_pressure,
        "consumption_rate": consumption_rate,
        "gas_before_turn_psi": round(gas_before_turn_psi,2 ),
        "gas_before_turn_cf": round (gas_before_turn_cuft,2),
        "time_before_turn": round (time_before_turn , 0),
        "time_descending": round (time_descending, 0),
        "total_dive_time_min": round(total_duration, 2), 
        "usable_gas": usable_gas,
        "time_ascending": round(time_ascending,0)
    }
