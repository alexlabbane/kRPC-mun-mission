import krpc
from time import sleep

def monitor(vessel):
    sleep(3)
    while True:
        resources = vessel.resources_in_decouple_stage(vessel.control.current_stage - 1, False)

        solidFuel = resources.amount("SolidFuel")
        liquidFuel = resources.amount("LiquidFuel")

        if solidFuel == 0 and liquidFuel == 0:
            vessel.control.activate_next_stage()  # Activates stage when fuel depleted
            print()
            print("Stage decoupled!")
            print()

        sleep(0.2)
