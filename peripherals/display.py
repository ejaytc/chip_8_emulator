from pyray import draw_rectangle, draw_text, YELLOW, Rectangle, draw_rectangle_lines_ex
import numpy as np

class Display:
    # TODO: Make the resolution adjust base on window size
    def __init__(self, x_axis: int, y_axis: int, aspect_ratio: int, color: tuple):
        self.s_ratio = aspect_ratio
        self.color: tuple = color
        self.x_axis: int  = x_axis
        self.y_axis: int = y_axis
        self.pixels: np.ndarray = np.zeros((x_axis, y_axis), dtype=bool)
        self.keys = {
            0X1:   1, 0X2:   2, 0X3:   3, 0XC: "4",
            0X4: "Q", 0X5: "W", 0X6: "E", 0XD: "R",
            0X7: "A", 0X8: "S", 0X9: "D", 0XE: "F",
            0XA: "Z", 0X0: "X", 0XB: "C", 0XF: "V"
        }

    def set_pixel(self, x: int, y: int) -> None:
      x = (x % self.x_axis)
      y = y % self.y_axis
      
      collision = self.pixels[x, y]
      self.pixels[x,  y] = not self.pixels[x, y]
      return collision and not self.pixels[x, y]
    
    def clear_screen(self):
        self.pixels.fill(False)

    def render(self) -> None:
        padding_x = 5
        padding_y = 10
        for x in range(self.x_axis):
            for y in range(self.y_axis):
                if self.pixels[x, y]:
                    draw_rectangle(
                        x * self.s_ratio  + padding_x, 
                        y * self.s_ratio + padding_y, 
                        self.s_ratio, 
                        self.s_ratio, 
                        self.color
                    )
    
    def render_info(self, core: object) -> None:
        y_pos = self.y_axis * self.s_ratio + 50
        x_pos = 5
        fontsize = 16
        for i in range(16):
            if i == 1:
                draw_text(f"V{i:X}:  {core._v[i]:02X}", x_pos, y_pos + i * 20, fontsize, self.color)
                continue
            draw_text(f"V{i:X}: {core._v[i]:02X}", x_pos, y_pos + i * 20, fontsize, self.color)

        x_pos = 80
        text_y_pos = y_pos + 240
        draw_text(f"PC: {core._pc:04X}", x_pos, text_y_pos, fontsize, self.color)
        draw_text(f"I:    {core._i:04X}", x_pos, text_y_pos + 20, fontsize, self.color)
        draw_text(f"DT: {core._dt:02X}", x_pos, text_y_pos + 40, fontsize, self.color)
        draw_text(f"ST: {core._st:02X}", x_pos, text_y_pos + 60, fontsize, self.color)
        draw_text(f"SP: {core._sp:02X}", x_pos, text_y_pos + 80, fontsize, self.color)


        x_pos = 180
        draw_text("Esc: Exit Emulator", x_pos + 120, y_pos, fontsize, self.color)
        draw_text("Key 5: Reselect Game", x_pos + 120, y_pos + 20, fontsize, self.color)
        for row in range(16):
            if row == core._sp:
                draw_text(
                    f">S{row:02X}: {core._stack[core._sp]:04X}", 
                    x_pos , 
                    (y_pos + (20 * row)), 
                    fontsize, 
                    YELLOW
                )
                continue
            draw_text(
                f" S{row:02X}: {core._stack[row]:03X}", 
                x_pos , 
                (y_pos + (20 * row)), 
                fontsize, 
                self.color
            )
        
        self.render_key_info()



    def render_key_info(self) -> None:
        y_pos = self.y_axis * self.s_ratio + 50
        x_pos = 185
        pos = 0
        key = tuple(self.keys.keys())
        for y in range(4):
            for x in range(4):
                size = 70

                info_frame = Rectangle(
                    (x_pos + 120) + (x * size), 
                    (y_pos + 50) + (y * size),
                    size, 
                    size
                )
                draw_rectangle_lines_ex(info_frame, 1.0, self.color)
                draw_text(
                    f"{key[pos]:02X} | {self.keys.get(key[pos])}", 
                    (x_pos + 135) + (x * size),
                    (y_pos + 80) + (y * size), 
                    16, 
                    self.color
                )
                pos += 1
    
    def render_opcode_history(self, core: object) -> None:
        y_pos = self.y_axis * self.s_ratio + 50
        x_pos = 70
        history = core._opcode_history
        for i, opcode in enumerate(history):
            text_y_pos = y_pos + i * 20
            if i == 0:
                draw_text(f"> {opcode:04X}", x_pos, text_y_pos, 20, YELLOW)
                continue
            draw_text(f"  {opcode:04X}", x_pos, text_y_pos + 20, 16, self.color)

    def render_selection(self, roms: list, str_len: int, row: int, col: int) -> None:
        starting_x = 5
        row_height = 20
        column_width = 90
        text_x_pos = 50
        text_y_pos = self.y_axis * self.s_ratio + 70
        for y in range(0, len(roms)):
            rom_value = roms[y]
            for x in range(0, len(rom_value)):
                x_pos = (starting_x + (str_len * 2)) + (x * column_width)
                y_pos = 20 + (y * row_height)
                if y == col and x == row:
                    draw_text(f">{rom_value[x]}", x_pos, y_pos, 14, YELLOW)
                    continue
                draw_text(f" {rom_value[x]}", x_pos, y_pos, 14, self.color)
        
        draw_text("CHIP 8 Emulator", 320, text_y_pos - 20, 30, self.color)
        draw_text("UP:       W", text_x_pos, text_y_pos + 30, 20, self.color)
        draw_text("DOWN:   S", text_x_pos, text_y_pos + 60, 20, self.color)
        draw_text("LEFT:   A", text_x_pos, text_y_pos + 90, 20, self.color)
        draw_text("RIGHT:  D", text_x_pos, text_y_pos + 120, 20, self.color)
        draw_text("PlAY:    C", text_x_pos, text_y_pos + 150, 20, self.color)
        draw_text("ESC: Exit Emulator", text_x_pos, text_y_pos + 280, 20, self.color)
        self.render_key_info()


