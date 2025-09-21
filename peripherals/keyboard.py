import time
import numpy as np
from pyray import (
    is_key_down,
    KeyboardKey
)


class Keyboard:
    def __init__(self) -> None:
        """
            Layout:
            1: 0X1 | 2: 0X2 | 3: 0X3 | 4: 0XC
            ---------------------------------
            Q: 0X4 | W: 0X5 | E: 0X6 | R: 0XD
            ---------------------------------
            A: 0X7 | S: 0X8 | 9: 0XD | F: 0XE
            ---------------------------------
            Z: 0XA | X: 0X0 | C: 0XB | V: 0XF 
        """
        self.keys: np = np.array([False] * 19, dtype=np.uint8)
        self.previous_keys = self.keys.copy()
        self.just_pressed = self.keys.copy()
        self.last_press_time = {key: 0.0 for key in range(19)}
        self.press_delay = 0.2  # 200 milliseconds
        self.key_map = {
            KeyboardKey.KEY_ONE: 0x1,
            KeyboardKey.KEY_TWO: 0x2, 
            KeyboardKey.KEY_THREE: 0x3,
            KeyboardKey.KEY_FOUR: 0xc,
            KeyboardKey.KEY_Q: 0x4, 
            KeyboardKey.KEY_W: 0x5, 
            KeyboardKey.KEY_E: 0x6, 
            KeyboardKey.KEY_R: 0xd,
            KeyboardKey.KEY_A: 0X7, 
            KeyboardKey.KEY_S: 0X8, 
            KeyboardKey.KEY_D: 0x9, 
            KeyboardKey.KEY_F: 0xe,
            KeyboardKey.KEY_Z: 0xa, 
            KeyboardKey.KEY_X: 0x0, 
            KeyboardKey.KEY_C: 0xb, 
            KeyboardKey.KEY_V: 0xf,
            KeyboardKey.KEY_FIVE: 0X10,
            KeyboardKey.KEY_B: 0X11,

            # DEBUG KEY
            KeyboardKey.KEY_LEFT_SHIFT: 0X12
        }

    def is_pressed(self, key_value: int) -> bool:
        """Updates the state of the CHIP-8 keys based on physical input."""
        return self.keys[key_value]

    def is_just_pressed(self, key_value: int) -> bool:
        """Returns True if the key was just pressed this frame."""
        return self.just_pressed[key_value]
    
    def update_key_state(self) -> None:
        """
        Updates the state of the CHIP-8 keys based on physical input.
        Step 1: Store the current state as the previous state.
        Step 2: Get the new current state.
        Step 3: A key is "just pressed" if it is currently down AND was NOT down previously
        """
        self.previous_keys = self.keys.copy()
        for physical_key, chip8_key in self.key_map.items():
            self.keys[chip8_key] = is_key_down(physical_key)
        self.just_pressed = self.keys & (self.previous_keys == False)

    def get_held_down_value(self) -> int | None:
        """
        Returns the value of the first key pressed, or None.
        Add  Debounce logic to lessen the sensitivity.
        """
        current_time = time.time()
        for key_value in range(16):
            if self.keys[key_value]:
                if (current_time - self.last_press_time[key_value]) > self.press_delay:
                    self.last_press_time[key_value] = current_time
                    return key_value
        return None
