import asyncio

loop = asyncio.get_event_loop_policy().new_event_loop()
loop.set_debug(True)
loop.slow_callback_duration = 0.02
