"""Shutter platform for inels."""
import logging

from pyinels.device.pyShutter import pyShutter
from pyinels.pyTimer import TimerError

from homeassistant.components.cover import CoverEntity

from custom_components.inels_rpc.const import (
    CLASS_SHUTTER,
    DOMAIN,
    DOMAIN_DATA,
    ICON_SHUTTER_CLOSED,
    ICON_SHUTTER_OPENED,
)

from custom_components.inels_rpc.entity import InelsEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup shutter platform."""

    _LOGGER.info("Setting up shutters")

    entities = hass.data[DOMAIN][DOMAIN_DATA]
    coordinator = hass.data[DOMAIN][entry.entry_id]

    shutters = [pyShutter(dev) for dev in entities if dev.type == CLASS_SHUTTER]

    await coordinator.async_refresh()

    if shutters:
        async_add_devices(
            [InelsShutter(coordinator, shutter) for shutter in shutters],
            True,
        )


class InelsShutter(InelsEntity, CoverEntity):
    """Inels shutter class."""

    _attr_assumed_state = True

    def __init__(self, coordinator, shutter):
        """Initialization of the InelsShutter."""
        super().__init__(coordinator, shutter)
        self._shutter = shutter
        self._coordinator = coordinator

    @property
    def name(self):
        """Device name."""
        return self._shutter.name

    @property
    def icon(self):
        """Return the icon of this shutter."""
        pos = self.current_cover_position
        return ICON_SHUTTER_CLOSED if pos == 0 else ICON_SHUTTER_OPENED

    @property
    def is_opening(self):
        """Shutter is opening."""
        return False

    @property
    def is_closing(self):
        """Shutter is closing."""
        return False

    @property
    def is_closed(self):
        """Unknown real closed/open state."""
        return None

    @property
    def current_cover_position(self):
        """Real position is unknown."""
        return None

    @property
    def device_class(self):
        """Shutter device class."""
        return CLASS_SHUTTER

    async def async_open_cover(self, **kwargs):
        """Open the shutter."""
        await self.hass.async_add_executor_job(self._shutter.pull_up)
        await self._coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs):
        """Close shutter."""
        await self.hass.async_add_executor_job(self._shutter.pull_down)
        await self._coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs):
        """Stop the shutter."""
        try:
            await self.hass.async_add_executor_job(self._shutter.stop)
            await self._coordinator.async_request_refresh()
        except TimerError:
            pass
