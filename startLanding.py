import krpc
import time as t
import msgpack
import _thread as thread
import matplotlib.pyplot as plt
from math import log

def entryBurn(vessel, space_center):
    """T30 Reliant Engine: Burns 8.68 oxidizer and 7.11 fuel per second at max throttle
    Total fuel weight is 2 tons and fuel lasts approx. 25.32 seconds
    Mass lost at a rate of 0.078945 tons per second - used in calculation of force of gravity
    and subsequently work needed to land"""

    fuel_mass_burn_rate = 0.078945  # Full throttle
    print(vessel.flight().terminal_velocity)
    t.sleep(5)
    terminal_velocity = 320

    # Calculate work needed to land the vessel
    time = 0
    mass = vessel.mass
    gravity_acceleration = vessel.orbit.body.surface_gravity  # Approximation but fine for heights close to the surface

    f_grav = mass * gravity_acceleration  # Force of gravity acting on vessel as a function of time
    f_thrust = vessel.available_thrust  # Force of max available thrust

    f_net = f_thrust - f_grav  # Net force if object thrusts as a function of time (up defined as positive)

    '''Run simulation to determine if it will land'''

    t_vals = []
    acceleration_vals = []

    while vessel.available_thrust == 0:
        pass
    initial_ut = space_center.ut



    while vessel.available_thrust > 0:

        time = 0
        mass = vessel.mass
        gravity_acceleration = vessel.orbit.body.surface_gravity  # Approximation but fine for heights close to the surface

        f_grav = mass * gravity_acceleration  # Force of gravity acting on vessel as a function of time
        f_thrust = vessel.available_thrust  # Force of max available thrust

        curr_ut = space_center.ut

        f_net = f_thrust - f_grav  # Net force if object thrusts as a function of time (up defined as positive)

        print("Force of Gravity:\t", f_grav)
        print("Thrust:\t", f_thrust)
        print("Net force:\t", f_net)
        print("Acceleration:\t", f_net/mass)
        print("Time:\t", curr_ut-initial_ut)
        print("Mass:\t", mass)
        print()

        #t_vals.append(curr_ut - initial_ut)
        #acceleration_vals.append(f_net/mass)

        #t.sleep(0.02)

    '''with open("acceleration.csv", 'w+') as file:
        for i in range(len(t_vals)):
            line = str(t_vals[i]) + "," + str(acceleration_vals[i]) + "\n"
            file.write(line)'''


'''EVERYTHING BELOW HERE IS DONE'''

def begin_landing(vessel, space_center, connection):
    deployed = False
    hybrid_frame = space_center.ReferenceFrame.create_hybrid(vessel.reference_frame, rotation=vessel.orbit.body.non_rotating_reference_frame)
    #height_prediction = connection.drawing.add_text("Height Prediction: Null", hybrid_frame, (-2,0,0), (1.57,3.14,3.14,0))
    #time_prediction = connection.drawing.add_text("Time Prediction: Null", hybrid_frame, (-1,0,2),(1.57,3.14,3.14,0))
    #velocity_prediction = connection.drawing.add_text("Velocity Prediction: Null", hybrid_frame, (-3,0,2), (1.57,3.14,3.14,0))
    # Start of script
    # TODO: Provide very slight corrections to cancel all horizontal velocity/add guidance

    # Get current body
    current_body = vessel.orbit.body

    landing_reference_frame = space_center.ReferenceFrame.create_hybrid(
        position=current_body.reference_frame, rotation=vessel.surface_reference_frame)
    flight = vessel.flight(landing_reference_frame)

    while True:
        # Finds initial time to begin burn
        #print("Mass", vessel.mass)
        time = velocity_intercept(vessel, -flight.velocity[0])
        #print("Initial height:", flight.surface_altitude)
        height = height_intercept(vessel, time, -flight.velocity[0], flight.surface_altitude)
        print("Predicted final height:", height, "with ", time, "second burn")
        temp = "Height Prediction: " + str(height)
        #height_prediction.content = temp
        temp = "Time Prediction: " + str(time)
        #time_prediction.content = temp

        if height < 1000 and time < 9 and not deployed:
            deployed = True
            vessel.control.legs = True

        if height < 8:
            break

    # Fire engine at max throttle
    initial_time_prediction = time
    print("FIRING ENGINE")
    vessel.control.throttle = 1
    t.sleep(0.1)
    initial_time = space_center.ut
    new_time = time
    # Run calculations in an attempt to keep vessel on track for landing
    #while abs(flight.surface_altitude) > 700:
    #    pass
    while abs(flight.velocity[0]) > 1:

        if flight.surface_altitude < 30:
            print("Disengaging autopilot for final touchdown...")
            #vessel.auto_pilot.reference_frame = vessel.surface_reference_frame
            #vessel.auto_pilot.engage()
            #vessel.auto_pilot.target_pitch_and_heading(90, 90)
            vessel.auto_pilot.disengage()

        time = velocity_intercept(vessel, -flight.velocity[0], 0.01, vessel.control.throttle)
        height = height_intercept(vessel, time, -flight.velocity[0], flight.surface_altitude, vessel.control.throttle)
        temp = "Height Prediction: " + str(height)
        #height_prediction.content = temp
        temp = "Time Prediction: " + str(time)
        #time_prediction.content = temp

        if height > 3.5:
            vessel.control.throttle -= 0.005
        elif height < 0.5:
            vessel.control.throttle += 0.004

        if time < 9 and not deployed:
            print("Deploying landing legs...")
            deployed = True
            vessel.control.legs = True

    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_pitch_and_heading(90, 90)  # Attempt to make rocket stand up straight
    vessel.control.throttle = 0
    print("Time to burn:", space_center.ut - initial_time)
    print("Expected:", initial_time_prediction)
    print()
    print("Final height:", flight.surface_altitude)
    print("Landed! Exiting...")

def velocity_intercept(vessel, initial_velocity, tolerance=0.01, thrust_multiplier=1):
    """Finds how long it will take for velocity to equal zero
    Only considers times between 0 and 92 seconds"""
    current_body = vessel.orbit.body

    initial_t = t.time()
    if initial_velocity > 0:
        initial_velocity *= -1
    time = 10
    thrust = thrust_multiplier * determine_surface_isp_ratio(current_body, vessel.flight(current_body.reference_frame), vessel.parts.engines) * (vessel.max_vacuum_thrust/1000)
    # TODO: Adjust for current direction of vessel (not needed for nearly vertical entry)
    gravity_accel = current_body.surface_gravity
    mass = vessel.mass/1000
    mass_burn_rate = approximate_mass_burn_rate(vessel)

    velocity = 1

    # Perform binary search on velocity function to find time to burn
    upper_bound = 92
    lower_bound = 0
    num_iterations = 0
    while abs(velocity) > tolerance and time > 0.0001 and time < 91.99:
        velocity = (-thrust / mass_burn_rate) * log(mass - mass_burn_rate * time) \
                   - gravity_accel * time + initial_velocity + (thrust / mass_burn_rate) * log(mass)

        num_iterations += 1

        if velocity < 0:
            lower_bound = time
            time = (time + upper_bound) / 2
        elif velocity > 0:
            upper_bound = time
            time = (time + lower_bound) / 2

    if num_iterations == 0:
        print("Big issues!")  # we don't have issues anymore, redundant
        print(velocity)
        print(time)
        print(thrust_multiplier)
        print()
    return time


def height_intercept(vessel, time, initial_velocity, current_height, thrust_multiplier = 1):
    """Gets the predicted final height of the vessel if the burn began now and ran for 'time' seconds"""
    current_body = vessel.orbit.body

    thrust = thrust_multiplier * determine_surface_isp_ratio(current_body, vessel.flight(current_body.reference_frame), vessel.parts.engines) * (vessel.max_vacuum_thrust/1000)
    gravity_accel = current_body.surface_gravity
    mass = vessel.mass/1000
    mass_burn_rate = approximate_mass_burn_rate(vessel)

    if initial_velocity > 0:
        initial_velocity *= -1

    final_height = (-1 / mass_burn_rate**2) * (
        mass_burn_rate * initial_velocity * (mass - mass_burn_rate * time) + thrust * log(mass) * (mass - mass_burn_rate * time)
        + gravity_accel * (((mass - mass_burn_rate * time)**2) / 2 - mass * (mass - mass_burn_rate * time))
        - thrust * (mass * log(mass - mass_burn_rate * time) - mass_burn_rate * time * log(mass - mass_burn_rate * time) - mass + mass_burn_rate * time)
    ) + current_height + (1/mass_burn_rate**2) * (
        mass_burn_rate * initial_velocity * mass + thrust * log(mass) * mass
        + gravity_accel * ((mass**2) / 2 - mass**2)
        - thrust * (mass * log(mass) - mass)
    )

    return final_height

def velocity_function(vessel, initial_velocity, time, thrust):
    """velocity function as function of time"""
    current_body = vessel.orbit.body

    if initial_velocity > 0:
        initial_velocity *= -1

    gravity_accel = current_body.surface_gravity
    mass = vessel.mass/1000
    mass_burn_rate = approximate_mass_burn_rate(vessel)
    try:
        velocity = (-thrust / mass_burn_rate) * log(mass - mass_burn_rate * time) \
                   - gravity_accel * time + initial_velocity + (thrust / mass_burn_rate) * log(mass)
    except:
        velocity = 0
    return velocity

def height_function(vessel, time, initial_velocity, current_height, thrust):
    """height function as a function of time"""
    current_body = vessel.orbit.body

    gravity_accel = current_body.surface_gravity
    mass = vessel.mass / 1000
    mass_burn_rate = approximate_mass_burn_rate(vessel)

    if initial_velocity > 0:
        initial_velocity *= -1

    final_height = (-1 / mass_burn_rate ** 2) * (
            mass_burn_rate * initial_velocity * (mass - mass_burn_rate * time) + thrust * log(mass) * (
                mass - mass_burn_rate * time)
            + gravity_accel * (((mass - mass_burn_rate * time) ** 2) / 2 - mass * (mass - mass_burn_rate * time))
            - thrust * (mass * log(mass - mass_burn_rate * time) - mass_burn_rate * time * log(
        mass - mass_burn_rate * time) - mass + mass_burn_rate * time)
    ) + current_height + (1 / mass_burn_rate ** 2) * (
                           mass_burn_rate * initial_velocity * mass + thrust * log(mass) * mass
                           + gravity_accel * ((mass ** 2) / 2 - mass ** 2)
                           - thrust * (mass * log(mass) - mass)
                   )
    #print("Height: ", final_height)
    return final_height


def approximate_mass_burn_rate(vessel):
    """how fast the vessel burns mass
    only calculates for reliant, terrier, and swivel engines currently"""
    mass_burn_rate = 0

    engines = vessel.parts.engines
    for engine in engines:
        if engine.active or engine.available_thrust > 0:
            if engine.part.name == "liquidEngine":
                # Reliant Engine
                mass_burn_rate += 0.078926
            elif engine.part.name == "liquidEngine3.v2" or engine.part.name == "liquidEngine3":
                # Terrier Engine
                mass_burn_rate += 0.017734
            elif engine.part.name == "liquidEngine2":
                # Swivel Engine
                mass_burn_rate += 0.068512
    return mass_burn_rate


def determine_surface_isp_ratio(body, flight, engines):
    """Determines ratio of specific impulse at surface level to specific impulse in a vacuum for active engines"""

    engine = None
    isp = 0
    for e in engines:
        if e.active or e.available_thrust > 0:
            engine = e

    # Uses up to sixth order polynomial to approximate isp as function of pressure (very good approximation in most cases)
    if body.has_atmosphere:
        pressure = body.pressure_at(0) / 101325  # Convert from pascals to atm
        if engine.part.name == "liquidEngine":
            # Reliant Engine
            isp = 0  # TODO: Find approximate isp function experimentally
        elif engine.part.name == "liquidEngine3.v2" or engine.part.name == "liquidEngine3":
            # Terrier Engine
            if pressure < 3:
                isp = -1.8606 * pressure**6 + 25.868 * pressure**5 - 133.61 * pressure**4 + 300.47 * pressure**3 - 202.47 * pressure**2 - 246.61 * pressure + 344.87
            else:
                isp = 0

        elif engine.part.name == "liquidEngine2":
            # Swivel Engine
            isp = -0.8236 * pressure**3 + 8.534 * pressure**2 - 77.194 * pressure + 320.14

        return isp / engine.vacuum_specific_impulse  # No wiggle room needed because of drag
    else:
        return 0.99  # Will get vacuum isp with no atmosphere, so ratio is 1 (0.99 to give a little wiggle room on landing)