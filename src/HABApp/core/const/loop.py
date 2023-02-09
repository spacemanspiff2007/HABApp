import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

loop.set_debug(True)
loop.slow_callback_duration = 0.02
