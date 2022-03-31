from easyconfig import create_app_config
from .models import HABAppConfig

CONFIG: HABAppConfig = create_app_config(HABAppConfig())
