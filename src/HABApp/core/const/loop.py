import asyncio

loop = asyncio.get_event_loop_policy().get_event_loop()
loop.set_debug(True)
loop.slow_callback_duration = 0.03
