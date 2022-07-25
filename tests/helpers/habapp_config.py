import HABApp
import HABApp.config.models


def get_dummy_cfg():
    cfg = HABApp.config.models.ApplicationConfig()
    cfg.location.latitude = 52.5185537
    cfg.location.longitude = 13.3758636
    cfg.location.elevation = 43

    return cfg
