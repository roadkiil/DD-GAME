"""Turn keyboard / game controller events into hub actions, with key-repeat and hot-plug."""

from __future__ import annotations

import time

import pygame

try:
    from pygame._sdl2 import controller as sdl_controller
except ImportError:  # pragma: no cover - very old pygame
    sdl_controller = None

DIRECTIONS = ("up", "down", "left", "right")

BUTTON_NAMES = {}
for _name in ("a", "b", "x", "y", "back", "guide", "start", "leftstick", "rightstick",
              "leftshoulder", "rightshoulder", "dpad_up", "dpad_down", "dpad_left", "dpad_right"):
    _const = getattr(pygame, "CONTROLLER_BUTTON_" + _name.upper(), None)
    if _const is not None:
        BUTTON_NAMES[_const] = _name.replace("dpad_", "dp")

DPAD = {"dpup": "up", "dpdown": "down", "dpleft": "left", "dpright": "right"}
KEY_DIRS = {pygame.K_UP: "up", pygame.K_DOWN: "down", pygame.K_LEFT: "left", pygame.K_RIGHT: "right"}

REPEAT_DELAY = 0.35
REPEAT_RATE = 0.08
AXIS_THRESHOLD = 16000


class InputMapper:
    def __init__(self, controls: dict):
        self.controls = controls
        self.controllers: dict[int, object] = {}  # instance_id -> Controller
        self.held_dir: str | None = None
        self.held_since = 0.0
        self.last_repeat = 0.0
        self.axis_dir: dict[int, str | None] = {}
        self.messages: list[str] = []  # hot-plug notices for the UI
        if sdl_controller:
            sdl_controller.init()
            for i in range(sdl_controller.get_count()):
                self._open(i)

    # --- devices -----------------------------------------------------------
    def _open(self, device_index: int) -> None:
        if not sdl_controller or not sdl_controller.is_controller(device_index):
            return
        try:
            c = sdl_controller.Controller(device_index)
            jid = c.as_joystick().get_instance_id()
            self.controllers[jid] = c
            self.messages.append(f"Controller connected: {c.name}")
        except pygame.error:
            pass

    def held_buttons(self) -> set[str]:
        """Buttons currently held on any controller (works while the hub is in the background
        because SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS is set before pygame starts)."""
        held = set()
        for c in list(self.controllers.values()):
            try:
                for const, name in BUTTON_NAMES.items():
                    if c.get_button(const):
                        held.add(name)
            except pygame.error:
                continue
        return held

    # --- mapping -----------------------------------------------------------
    def _action_for_button(self, name: str) -> str | None:
        if name in DPAD:
            return DPAD[name]
        for action, spec in self.controls.items():
            if name in spec.get("buttons", []):
                return action
        return None

    def _action_for_key(self, key: int) -> str | None:
        if key in KEY_DIRS:
            return KEY_DIRS[key]
        kname = pygame.key.name(key)
        for action, spec in self.controls.items():
            if kname in spec.get("keys", []):
                return action
        return None

    def _press_dir(self, d: str, now: float) -> str:
        self.held_dir, self.held_since, self.last_repeat = d, now, now
        return d

    def handle(self, ev: pygame.event.Event, now: float | None = None) -> str | None:
        now = time.monotonic() if now is None else now
        t = ev.type
        if t == getattr(pygame, "CONTROLLERDEVICEADDED", -1):
            self._open(ev.device_index)
            return None
        if t == getattr(pygame, "CONTROLLERDEVICEREMOVED", -1):
            c = self.controllers.pop(ev.instance_id, None)
            if c is not None:
                self.messages.append("Controller disconnected - keyboard still works.")
                self.held_dir = None
            return None
        if t == getattr(pygame, "CONTROLLERBUTTONDOWN", -1):
            name = BUTTON_NAMES.get(ev.button)
            action = self._action_for_button(name) if name else None
            if action in DIRECTIONS:
                return self._press_dir(action, now)
            return action
        if t == getattr(pygame, "CONTROLLERBUTTONUP", -1):
            name = BUTTON_NAMES.get(ev.button)
            if name in DPAD and DPAD[name] == self.held_dir:
                self.held_dir = None
            return None
        if t == getattr(pygame, "CONTROLLERAXISMOTION", -1):
            if ev.axis not in (pygame.CONTROLLER_AXIS_LEFTX, pygame.CONTROLLER_AXIS_LEFTY):
                return None
            horiz = ev.axis == pygame.CONTROLLER_AXIS_LEFTX
            d = None
            if ev.value <= -AXIS_THRESHOLD:
                d = "left" if horiz else "up"
            elif ev.value >= AXIS_THRESHOLD:
                d = "right" if horiz else "down"
            prev = self.axis_dir.get(ev.axis)
            self.axis_dir[ev.axis] = d
            if d and d != prev:
                return self._press_dir(d, now)
            if d is None and prev == self.held_dir:
                self.held_dir = None
            return None
        if t == pygame.KEYDOWN:
            action = self._action_for_key(ev.key)
            if action in DIRECTIONS:
                return self._press_dir(action, now)
            return action
        if t == pygame.KEYUP:
            if KEY_DIRS.get(ev.key) == self.held_dir:
                self.held_dir = None
            return None
        return None

    def repeat(self, now: float | None = None) -> str | None:
        """Call once per frame: emits repeated directions while a direction is held."""
        now = time.monotonic() if now is None else now
        if self.held_dir and now - self.held_since > REPEAT_DELAY and now - self.last_repeat > REPEAT_RATE:
            self.last_repeat = now
            return self.held_dir
        return None
