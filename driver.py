import krpc
import time
import _thread as thread
import startLanding
import toLKO
import munTransfer
import stageMonitor
import orbitMun
import testingTools
import targetLandingSite

"""This program is a work in progress and does not work as well as I would like for any vessel yet"""

# Set up a connection to server
connection = krpc.connect("Connection")
space_center = connection.space_center
vessel = space_center.active_vessel

# Set up stage monitor thread
args = [vessel]
thread.start_new_thread(stageMonitor.monitor, tuple(args))

'''Begining of completely automated kerbin to moon'''
# Get to LKO
toLKO.engage(vessel, space_center, connection, 0.5)

# Mun transfer burn
munTransfer.engage(vessel, space_center, connection)
time_to_warp = vessel.orbit.next_orbit.time_to_periapsis + vessel.orbit.time_to_soi_change
space_center.warp_to(space_center.ut + time_to_warp - 300)  # 5 minutes before periapsis of mun encounter

# Get ready for landing
orbitMun.engage(vessel, space_center, connection)

# Engage Landing (vertical)
vessel.auto_pilot.engage()
vessel.auto_pilot.reference_frame = vessel.surface_velocity_reference_frame
vessel.auto_pilot.target_direction = (0.0, -1.0, 0.0)  # Point retro-grade surface
startLanding.begin_landing(vessel, space_center, connection)

print("Stabilizing...")
vessel.auto_pilot.reference_frame = vessel.surface_reference_frame
vessel.auto_pilot.target_direction = (1.0, 0.0, 0.0)
time.sleep(10)
vessel.auto_pilot.disengage()
vessel.control.sas = True
print("DONE")
