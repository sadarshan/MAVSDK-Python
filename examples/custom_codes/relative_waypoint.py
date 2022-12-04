import logging
import asyncio
from mavsdk import System
import random
import logging
import os

random_number_for_logging= random.randint(100000, 1000000)

file_path=os.path.abspath(__file__)
log_path = "/home/darshan/Documents/MAVSDK-Python/examples/logs/"
log_filename = log_path + (os.path.basename(__file__)).rsplit(".")[0] + "_"+ str(random_number_for_logging) + ".log"
handlers = [logging.FileHandler(log_filename), logging.StreamHandler()]
logging.basicConfig(handlers=handlers, format="%(asctime)s.%(msecs)03d - %(levelname)s-%(message)s", level=logging.DEBUG,datefmt="%d-%b-%y %H:%M:%S")
logging.info(f"file:{file_path}")
logging.info(f"logs:{log_filename}")


async def createRelativeWaypoint():
    pass

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    status_text_task = asyncio.ensure_future(print_status_text(drone))
    logging.info("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            logging.info("-- Connected to drone!")
            break
    
    logging.info("Waiting for drone to have a global position estimate")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            logging.info("-- Global position and home position estimate OK")
            break
    
    logging.info("-- Arming")
    await drone.action.arm()

    logging.info("-- Taking off")
    await drone.action.takeoff()

    logging.info(f"position: {drone.telemetry.position()}")

    await asyncio.sleep(10)

    logging.info("-- Landing")
    await drone.action.land()

    logging.info(f"position: {drone.telemetry.position()}")

    drone.telemetry.status_text()
    
    status_text_task.cancel()

async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            logging.info(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
