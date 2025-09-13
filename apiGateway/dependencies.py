from typing import Annotated

from config import Settings, get_settings
from fastapi import Depends

SettingsDep = Annotated[Settings, Depends(get_settings)]
