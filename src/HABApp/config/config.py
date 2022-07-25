from easyconfig import create_app_config
from .models import ApplicationConfig

CONFIG: ApplicationConfig = create_app_config(ApplicationConfig())
