import asyncio
import random
from pywizlight import wizlight, PilotBuilder, discovery

async def main():
    brightness = 0
    brightness_increment = 10

    bulbs = await discovery.find_wizlights()
    print(bulbs)

    ip = bulbs[0].__dict__['ip_address']
    light = wizlight(f"{ip}")

    while (brightness + brightness_increment) < 255:
        brightness += brightness_increment
        print("Brightness: " + str(brightness))
        try:
            await asyncio.wait_for(light.turn_on(PilotBuilder(rgb = (brightness, 0, 0))), 1.5)
        except asyncio.TimeoutError:
            continue

    await light.turn_off()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())