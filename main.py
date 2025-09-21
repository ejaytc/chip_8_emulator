#!/usr/bin python3
from pyray import (
    init_window,
    begin_drawing,
    window_should_close,
    close_window,
    clear_background,
    end_drawing,
    set_target_fps,
    draw_rectangle_lines_ex,
    draw_text,
    Rectangle,
    BLACK,
    GREEN,
    RED
)

from core.memory import Memory
from core.decoder import Decoder
from core.core import Core
from peripherals.display import Display
from peripherals.keyboard import Keyboard

MAIN_DISPLAY_W = 644
MAIN_DISPLAY_H = 720
MAX_FRAME_BUFFER_W = 640
MAX_FRAME_BUFFER_H = 360
DEFAULT_FRAME_W = 64
DEFAULT_FRAME_H = 32

# --- New constants for decoupling ---
TARGET_FPS = 60
CHIP8_CLOCK_HZ = 500
CYCLES_PER_FRAME = CHIP8_CLOCK_HZ // TARGET_FPS

def main():
    w_ratio = MAX_FRAME_BUFFER_W // DEFAULT_FRAME_W
    h_ratio = MAX_FRAME_BUFFER_H // DEFAULT_FRAME_H
    s_ratio = min(w_ratio, h_ratio)

    init_window(MAIN_DISPLAY_W, MAIN_DISPLAY_H, "Chip 8 Emulator")
    set_target_fps(TARGET_FPS)
    display = Display(DEFAULT_FRAME_W, DEFAULT_FRAME_H, s_ratio, GREEN)
    memory = Memory()
    decoder = Decoder()
    keyboard = Keyboard()
    core = Core(memory, decoder, keyboard, display)
    roms, str_len = core.read_rom()
    core_frame = Rectangle(1, 1, MAX_FRAME_BUFFER_W + 2, MAX_FRAME_BUFFER_H + 2)
    info_frame = Rectangle(1, 364, MAX_FRAME_BUFFER_W + 2, MAX_FRAME_BUFFER_H - 5)

    pos_x = 0
    pos_y = 0
    is_pause = False  
    while not window_should_close():
        keyboard.update_key_state()
        if not is_pause and keyboard.is_just_pressed(0x12):
            print("Pause")
            is_pause = True
        elif is_pause and keyboard.is_just_pressed(0x12):
            print("True")
            is_pause = False

        if not core._is_rom_loaded:
            if keyboard.is_just_pressed(0x5):
                if pos_y >= 0:
                    pos_y -= 1
                if pos_y < 0:
                    pos_y = len(roms) - 1
            elif keyboard.is_just_pressed(0x8):
                if pos_y <= len(roms) -1:
                    pos_y += 1
                if pos_y > len(roms) -1:
                    pos_y = 0
            elif keyboard.is_just_pressed(0x7):
                if pos_x >= 0:
                    pos_x -= 1
                if pos_x < 0:
                    pos_x = len(roms[pos_y]) - 1
            elif keyboard.is_just_pressed(0x9):
                if pos_x <= len(roms[pos_y]) - 1:
                    pos_x += 1
                if pos_x > len(roms[pos_y]) - 1:
                    pos_x = 0
            elif keyboard.is_just_pressed(0xb):
                core.write_rom(roms[pos_y][pos_x])
                core._is_rom_loaded = True
                display.clear_screen()
                continue
            display.render_selection(roms, str_len, pos_x, pos_y)
        else:
            if keyboard.is_just_pressed(0x10):
                core.reset()
                memory.clear()
                display.clear_screen()

            # --- The Decoupling Loop ---
            if not core._is_exceptions:
                if core._is_waiting_key:
                    pressed_key = keyboard.get_held_down_value()
                    if pressed_key is not None:
                        core._v[core._pressed_key] = pressed_key
                        core._is_waiting_key = False
                        core._pc += 2
                else:
                    for _ in range(CYCLES_PER_FRAME):
                        if not is_pause:
                            core.cycle()
                            core.update_timer()
        
        begin_drawing()
        clear_background(BLACK)
        draw_rectangle_lines_ex(core_frame, 1.0, GREEN)
        draw_rectangle_lines_ex(info_frame, 1.0, GREEN)

        if core._is_rom_loaded:
            display.render()
            if core._is_exceptions:
                draw_text("An Error Occured:", 10, 400, 20, RED)
                draw_text(f"{core._exceptions}", 10, 420, 20, RED)
                draw_text("Pressed C to Continue")

            else:
                display.render_info(core)
                display.render_opcode_history(core)
        end_drawing()
    close_window()


if __name__ == "__main__":
    main()
