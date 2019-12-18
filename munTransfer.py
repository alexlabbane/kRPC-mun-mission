import krpc
from time import sleep
import math

def engage(vessel, space_center, connection):
    vessel.control.rcs = True
    fairings = vessel.parts.fairings
    for fairing in fairings:
        fairing.jettison()
    vessel.control.antennas = True  # Deploy antennas


    destSemiMajor = space_center.bodies["Mun"].orbit.semi_major_axis
    hohmannSemiMajor = destSemiMajor / 2
    neededPhase = 2 * math.pi * (1 / (2 * (destSemiMajor ** 3 / hohmannSemiMajor ** 3) ** (1 / 2)))
    optimalPhaseAngle = 180 - neededPhase * 180 / math.pi  # In degrees; for mun, mun should be ahead of vessel

    # Get current phase angle
    phaseAngle = 1080  # Random default value
    vessel.auto_pilot.engage()
    vessel.auto_pilot.reference_frame = vessel.orbital_reference_frame
    vessel.auto_pilot.target_direction = (0.0, 1.0, 0.0)  # Point pro-grade

    angleDec = False  # Whether or not phase angle is decreasing; used to make sure mun is ahead of vessel
    prevPhase = 0
    while abs(phaseAngle - optimalPhaseAngle) > 1 or not angleDec:
        bodyRadius = space_center.bodies["Mun"].orbit.radius
        vesselRadius = vessel.orbit.radius

        sleep(1)

        bodyPos = space_center.bodies["Mun"].orbit.position_at(space_center.ut, space_center.bodies["Mun"].reference_frame)
        vesselPos = vessel.orbit.position_at(space_center.ut, space_center.bodies["Mun"].reference_frame)

        bodyVesselDistance = ((bodyPos[0] - vesselPos[0])**2 + (bodyPos[1] - vesselPos[1])**2 + (bodyPos[2] - vesselPos[2])**2)**(1/2)

        try:
            phaseAngle = math.acos((bodyRadius**2 + vesselRadius**2 - bodyVesselDistance**2) / (2 * bodyRadius * vesselRadius))
        except:
            print("Domain error! Cannot calculate. Standby...")
            continue  # Domain error
        phaseAngle = phaseAngle * 180 / math.pi

        if prevPhase - phaseAngle > 0:
            angleDec = True
            if abs(phaseAngle - optimalPhaseAngle) > 20:
                space_center.rails_warp_factor = 2
            else:
                space_center.rails_warp_factor = 0
        else:
            angleDec = False
            space_center.rails_warp_factor = 4


        prevPhase = phaseAngle

        print("Phase:", phaseAngle)


    # Use vis-viva to calculate deltaV required to raise orbit to that of the moon
    GM = vessel.orbit.body.gravitational_parameter# Get gravitation parameter (GM) for Kerbin
    r = vessel.orbit.radius
    a = vessel.orbit.semi_major_axis

    initialV = (GM * ((2/r) - (1/a)))**(1/2)

    a = (space_center.bodies["Mun"].orbit.radius + vessel.orbit.radius) / 2

    finalV = (GM * ((2/r) - (1/a)))**(1/2)

    deltaV = finalV - initialV
    print("Maneuver Now With DeltaV:", deltaV)

    actualDeltaV = 0
    vessel.control.throttle = 1.0
    while(deltaV > actualDeltaV):  # Complete maneuver node with <= 2% inaccuracy
        sleep(0.15)
        r = vessel.orbit.radius
        a = vessel.orbit.semi_major_axis
        actualDeltaV = (GM * ((2/r) - (1/a)))**(1/2) - initialV
        print("DeltaV so far: ", actualDeltaV, "out of needed", deltaV)
    vessel.control.throttle = 0
    vessel.auto_pilot.disengage()

    print("We should have a mun encounter!")
    print()
