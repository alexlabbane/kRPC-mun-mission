import krpc
from time import sleep

def engage(vessel, space_center, connection):
    vessel.control.rcs = True
    vessel.control.antennas = True
    vessel.auto_pilot.engage()
    vessel.auto_pilot.reference_frame = vessel.surface_velocity_reference_frame
    vessel.auto_pilot.target_direction = (0.0, -1.0, 0.0)  # Point retro-grade surface

    vessel.auto_pilot.wait()  # Wait until pointing retro-grade
    time_to_warp = vessel.orbit.time_to_periapsis
    space_center.warp_to(space_center.ut + time_to_warp - 30)  # 30 seconds from periapsis

    vessel.auto_pilot.wait()
    print("Fire engine...")
    # Stream surface velocity
    sfcRefFrame = vessel.orbit.body.reference_frame
    flight = vessel.flight(sfcRefFrame)
    surfaceSpeed = connection.add_stream(getattr, flight, 'speed')


    first = True
    while vessel.flight().surface_altitude > 20000 or first:  # Needed to make sure there is not too much horizontal velocity
        sleep(0.5)
        if vessel.flight().surface_altitude < 30000 or first:  # Correct at 110000 meters (110 km)
            while surfaceSpeed() > 1.0:
                first = False
                vessel.control.throttle = 1 - (0.95 / 1.01**surfaceSpeed())

                error = (vessel.auto_pilot.pitch_error**2 + vessel.auto_pilot.heading_error**2)**(1/2)
                if error > 3:
                    vessel.control.throttle = 0
                    while error > 1.2:
                        error = (vessel.auto_pilot.pitch_error ** 2 + vessel.auto_pilot.heading_error ** 2) ** (1 / 2)
                        print(vessel.auto_pilot.error)
                        sleep(0.25)
            vessel.control.throttle = 0
            if vessel.flight().surface_altitude < 30000:
                break

    vessel.control.throttle = 0
    print("Prepared for landing...")
    print()