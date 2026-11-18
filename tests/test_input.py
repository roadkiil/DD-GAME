"""Controller/keyboard mapping, exercised with synthetic SDL events.

This verifies the hub's mapping logic. It does NOT verify a physical controller: SDL device
handling and controller databases must be checked on real hardware.
"""

import pygame
import pytest

from ddhub.settings import DEFAULTS
from ddhub.ui.input import InputMapper


@pytest.fixture(scope="module", autouse=True)
def pg():
    pygame.init()
    yield
    pygame.quit()


def ev(t, **kw):
    return pygame.event.Event(t, **kw)


def test_controller_buttons_map_to_actions():
    m = InputMapper(DEFAULTS["controls"])
    cb = pygame.CONTROLLERBUTTONDOWN
    assert m.handle(ev(cb, button=pygame.CONTROLLER_BUTTON_A, instance_id=0)) == "accept"
    assert m.handle(ev(cb, button=pygame.CONTROLLER_BUTTON_B, instance_id=0)) == "back"
    assert m.handle(ev(cb, button=pygame.CONTROLLER_BUTTON_Y, instance_id=0)) == "search"
    assert m.handle(ev(cb, button=pygame.CONTROLLER_BUTTON_RIGHTSHOULDER, instance_id=0)) == "next_tab"
    assert m.handle(ev(cb, button=pygame.CONTROLLER_BUTTON_DPAD_DOWN, instance_id=0)) == "down"


def test_stick_with_deadzone_and_repeat():
    m = InputMapper(DEFAULTS["controls"])
    am = pygame.CONTROLLERAXISMOTION
    assert m.handle(ev(am, axis=pygame.CONTROLLER_AXIS_LEFTX, value=8000, instance_id=0), now=0) is None
    assert m.handle(ev(am, axis=pygame.CONTROLLER_AXIS_LEFTX, value=30000, instance_id=0), now=0) == "right"
    assert m.repeat(now=0.1) is None          # before repeat delay
    assert m.repeat(now=0.5) == "right"       # held -> repeats
    m.handle(ev(am, axis=pygame.CONTROLLER_AXIS_LEFTX, value=0, instance_id=0), now=0.6)
    assert m.repeat(now=1.5) is None          # released -> stops


def test_remapping_from_settings():
    controls = {**DEFAULTS["controls"], "accept": {"buttons": ["b"], "keys": ["k"]},
                "back": {"buttons": ["a"], "keys": ["escape"]}}
    m = InputMapper(controls)
    assert m.handle(ev(pygame.CONTROLLERBUTTONDOWN, button=pygame.CONTROLLER_BUTTON_B, instance_id=0)) == "accept"
    assert m.handle(ev(pygame.KEYDOWN, key=pygame.K_k, mod=0, unicode="k", scancode=0)) == "accept"


def test_disconnect_message_and_keyboard_fallback():
    m = InputMapper(DEFAULTS["controls"])
    m.controllers[7] = object()
    m.handle(ev(pygame.CONTROLLERDEVICEREMOVED, instance_id=7))
    assert 7 not in m.controllers and any("disconnected" in s for s in m.messages)
    assert m.handle(ev(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r", scancode=0)) == "accept"
