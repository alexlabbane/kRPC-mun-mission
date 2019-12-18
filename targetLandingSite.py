import krpc
import time
import msgpack
import matplotlib.pyplot as plt
import math


'''Used to set rocket on trajectory to target landing site
Should be able to go both from orbit and from sub-orbital trajectory (on a boostback burn, for example)'''

# Predict landing trajectory
def predict_impact_coordinates(connection, spacecenter, vessel, flight):
    acceleration = vessel.orbit.body.surface_gravity
    velocity0_z, velocity0_y, velocity0_x = flight.velocity
    height0 = flight.surface_altitude
    lat0 = flight.latitude
    long0 = flight.longitude

    # Determines difference between current latitude, longitude and the impact latitude, longitude
    # Uses trigonometry (factoring in height of vessel, etc)

    #TEST: Draw vector to launch pad
    print(lat0, long0)
    a = flight.elevation - flight.surface_altitude + vessel.orbit.body.equatorial_radius
    b = vessel.orbit.body.surface_height(-0.09716857406266075, -74.55768875892863) + vessel.orbit.body.equatorial_radius

    height_difference = vessel.orbit.body.surface_height(-0.09716857406266075, -74.55768875892863) - flight.elevation + flight.surface_altitude
    latitude_difference = (flight.latitude - (-0.09716857406266075)) * math.pi / 180
    longitude_difference = (flight.longitude - (-74.55768875892863)) * math.pi / 180

    north_distance = (a**2 + b**2 - 2*a*b*math.cos(latitude_difference))**(1/2)
    east_distance = (a**2 + b**2 - 2*a*b*math.cos(longitude_difference))**(1/2)

    print(east_distance)
    print(north_distance)
    print(height_difference)
    to_launch_pad = connection.drawing.add_line((0,0,0), (height_difference-height_difference, -north_distance, -east_distance), vessel.surface_reference_frame)
    to_launch_pad.thickness = 3

    while True:
        a = -flight.elevation + vessel.orbit.body.equatorial_radius
        b = -vessel.orbit.body.surface_height(-0.09716857406266075,
                                             -74.55768875892863) + vessel.orbit.body.equatorial_radius

        height_difference = vessel.orbit.body.surface_height(-0.09716857406266075, -74.55768875892863) - flight.elevation - flight.surface_altitude
        latitude_difference = (flight.latitude - (-0.09716857406266075)) * math.pi / 180
        longitude_difference = (flight.longitude - (-74.55768875892863)) * math.pi / 180

        #If the vessel is over the sea
        if flight.elevation < 0:
            height_difference += flight.elevation

        north_distance = (a ** 2 + b ** 2 - 2 * a * b * math.cos(latitude_difference)) ** (1 / 2)
        east_distance = (a ** 2 + b ** 2 - 2 * a * b * math.cos(longitude_difference)) ** (1 / 2)

        if latitude_difference > 0:
            north_distance *= -1
        if longitude_difference > 0:
            east_distance *= -1
        if height_difference > 0:
            height_difference += 8
        else:
            height_difference += 8
        print(vessel.orbit.body.surface_height(-0.09716857406266075, -74.55768875892863))
        print(-flight.elevation)
        print(-flight.surface_altitude)
        print(to_launch_pad.end)
        print()
        to_launch_pad.end = (height_difference, north_distance, east_distance)
        time.sleep(0.01)
