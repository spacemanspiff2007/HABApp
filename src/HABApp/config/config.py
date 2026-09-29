from easyconfig import create_async_app_config

from .models import ApplicationConfig


CONFIG: ApplicationConfig = create_async_app_config(ApplicationConfig())
