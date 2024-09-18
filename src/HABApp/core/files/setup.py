from .manager import setup_file_manager


async def setup() -> None:
    await setup_file_manager()
