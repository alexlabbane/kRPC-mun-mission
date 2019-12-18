import krpc
import time as t
import msgpack

def determine_mass_burn_rate(space_center, vessel):
    times = []
    masses = []
    initial_time = space_center.ut
    print("Started.")
    while vessel.thrust > 0:
        times.append(space_center.ut - initial_time)
        masses.append(vessel.mass)
        t.sleep(0.05)
        print("Thrust:", vessel.thrust)

    # Write to csv
    filename = vessel.parts.engines[0].part.name + "_burn_rate.csv"
    with open(filename, 'w+') as file:
        for i in range(len(times)):
            line = str(times[i]) + "," + str(masses[i]) + "\n"
            file.write(line)
            print("Line", i, "written.")
    print("Mass burn rate determined. Use produced csv.")

def isp_vs_pressure(space_center, vessel, flight):

    current_body = vessel.orbit.body
    atmospheric_pressures = []
    isps = []

    # Get the engine to investigate
    engine = vessel.parts.engines[0]
    engine_name = engine.part.name
    vessel.control.throttle = 0.01
    while len(vessel.parts.engines) > 0:
        atmospheric_pressures.append(current_body.pressure_at(flight.mean_altitude))
        isps.append(engine.specific_impulse)
        t.sleep(0.02)
    vessel.control.throttle = 0

    filename = engine_name + "_isp_vs_pressure"
    with open(filename, 'w+') as file:
        for i in range(len(isps)):
            line = str(atmospheric_pressures[i]) + "," + str(isps[i]) + "\n"
            file.write(line)
    print("ISP curve created successfully for", engine_name)
