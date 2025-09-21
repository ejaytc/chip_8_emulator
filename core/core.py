import os
import binascii
import random

import numpy as np


class Core:
    def __init__(self, memory: object, decoder: object, keyboard: object, display: object) -> None:
        # initialize
        # Usually from  0X000 to 0X1FF Reserved for interpreter but not for this one.
        # 0X050 to 0X0A0 for builtin characters from 0 to F
        # 0X200 to 0XFFF for Instructions
        self._v: np.ndarray = np.array([0] * 16,dtype=np.uint8)  # initial 16 8-bit registers from V0 to VF
        self._pc: int = 0X200 # Program counter start at the address off 0X200, 16-bit register.
        self._i: np.uint16 = 0x0 # 12-bit index register
        self._stack: np.ndarray = np.array([0] * 16, dtype=np.uint16) # 16 level of stack
        self._sp: int = -1 # stack pointer 0XFF
        self._dt: np.uint8 = 0x0 # 8-bit register delay timer
        self._st: np.uint8  = 0x0 # 8-bit register sound timer
        self.memory: object = memory
        self.decoder: object = decoder
        self.keyboard: object = keyboard
        self.display: object = display
        self._is_waiting_key: bool = False
        self._pressed_key: int = 0
        self._exceptions: str = ""
        self._is_exceptions: bool = False
        self._opcode_history: list = []
        self.MAX_HISTORY_LENGTH: int = 10
        self._is_rom_loaded: int = False
        self.MAX_STACK_DEPTH = 15
        
        # CHIP-48 Mode
        self.shift_use_vy: bool = False # default False
        self.increment_i: bool = False # default False

        # SCHIP
        # TODO: Add variables to handle SCHIP later


    def reset(self) -> None:
        self._v: np.ndarray = np.array([0] * 16,dtype=np.uint8)
        self._pc: int = 0X200 
        self._i: np.uint16 = 0x0
        self._stack: np.ndarray = np.array([0] * 16, dtype=np.uint16) 
        self._sp: int = -1 
        self._dt: np.uint8 = 0x0 
        self._st: np.uint8  = 0x0
        self._is_waiting_key: bool = False
        self._pressed_key: int = 0
        self._exceptions: str = ""
        self._is_exceptions: bool = False
        self._opcode_history: list = []
        self.MAX_HISTORY_LENGTH: int = 10
        self._is_rom_loaded: int = False
        
    def read_path(self) -> str:
            abspath = os.path.dirname(os.path.abspath(__name__))
            return os.path.join(abspath, "GAMES/")

    def read_rom(self) -> tuple:
        rom_path = self.read_path()
        all_entries = sorted(os.listdir(rom_path))
        roms = []
        for entry in range(0, len(all_entries), 6):
            sub_list = all_entries[entry:entry + 6]
            roms.append(sub_list)
        return roms, len(max(all_entries, key=len))
    
    def write_rom(self, game: str) -> None:
        path = self.read_path()
        with open(os.path.join(path, game), "rb") as file:
            start = self._pc
            _next = 0
            rom = binascii.hexlify(file.read()).decode('utf-8')
            while True:
                if _next >= len(rom):
                    break
                data = f"0x{rom[_next: _next + 2]}"
                self.memory[start] = int(data, 16)
                start += 1 
                _next += 2
        
    def fetch_opcode(self) -> int:
        return self.memory[int(self._pc)] << 8 | self.memory[int(self._pc) + 1]

    def cycle(self):
        opcode = self.fetch_opcode()
        decoder = self.decoder
        msn = decoder._nibble(opcode)
        self._current_opcode = opcode
        self._opcode_history.insert(0, opcode)
        if len(self._opcode_history) > self.MAX_HISTORY_LENGTH:
            self._opcode_history.pop()

        if msn == 0x0:
            if opcode == 0x00e0:
                self._execute_0x00e0_cls()
            elif opcode == 0x00ee:
                self._execute_0x00ee_ret()
            # 0X0NNN (SYS addr) - often ignored in modern emulators
        elif msn == 0x1:
            self._execute_1nnn_jp_addr(decoder._addr(opcode))
        elif msn == 0x2:
            self._execute_2nnn_call_addr(decoder._addr(opcode))
        elif msn == 0x3:
            x_reg = decoder._x(opcode)
            kk = decoder._kk(opcode)
            self._execute_3xkk_se_vx_byte(x_reg, kk)
        elif msn == 0x4:
            x_reg = decoder._x(opcode)
            kk =  decoder._kk(opcode)
            self._execute_4xkk_sne_vx_byte(x_reg, kk)
        elif msn == 0x5:
            x_reg = decoder._x(opcode)
            y_reg = decoder._y(opcode)
            self._execute_5xy0_se_vx_vy(x_reg, y_reg)
        elif msn == 0x6:
            x_reg = decoder._x(opcode)
            kk = decoder._kk(opcode)
            self._execute_6xkk_ld_vx_byte(x_reg, kk)
        elif msn == 0x7:
            x_reg = decoder._x(opcode)
            kk = decoder._kk(opcode)
            self._execute_7xkk_add_vx_byte(x_reg, kk)
        elif msn == 0x8:
            lsn = decoder._n(opcode)
            x_reg = decoder._x(opcode)
            y_reg = decoder._y(opcode)
            if lsn == 0x0:
                self._execute_8xy0_ld_vx_vy(x_reg, y_reg)
            elif lsn == 0x1:
                self._execute_8xy1_or_vx_vy(x_reg, y_reg)
            elif lsn == 0x2:
                self._execute_8xy2_and_vx_vy(x_reg, y_reg)
            elif lsn == 0x3:
                self._execute_8xy3_xor_vx_vy(x_reg, y_reg)
            elif lsn == 0x4:
                self._execute_8xy4_add_vx_vy(x_reg, y_reg)
            elif lsn == 0x5:
                self._execute_8xy5_sub_vx_vy(x_reg, y_reg)
            elif lsn == 0x6:
                self._execute_8xy6_shr_vx_vy(x_reg, y_reg)
            elif lsn == 0x7:
                self._execute_8xy7_subn_vx_vy(x_reg, y_reg)
            elif lsn == 0xe:
                self._execute_8xye_shl_vx_vy(x_reg, y_reg)
            else:
                self._exceptions = f"Unkown 8XYN opcode {opcode:04X}"
                self._is_exceptions = True
        elif msn == 0x9:
            x_reg = decoder._x(opcode)
            y_reg = decoder._y(opcode)
            self._execute_9xy0_sne_vx_vy(x_reg, y_reg)
        elif msn == 0xa:
            self._execute_annn_ld_i_addr(decoder._addr(opcode))
        elif msn == 0xb:
            self._execute_bnnn_jp_v0_addr(decoder._addr(opcode))
        elif msn == 0xc:
            x_reg = decoder._x(opcode)
            kk = decoder._kk(opcode)
            self._execute_cxkk_rnd_vx_byte(x_reg, kk)
        elif msn == 0xd:
            x_reg = decoder._x(opcode)
            y_reg = decoder._y(opcode)
            n_reg = decoder._n(opcode)
            self._execute_dxyn_drw_vx_vy_nibble(x_reg, y_reg, n_reg)
        elif msn == 0xe:
            lkk = decoder._kk(opcode)
            x_reg = decoder._x(opcode)
            if lkk == 0x9e:
                self._execute_ex9e_skp_vx(x_reg)
            elif lkk == 0xa1:
                self._execute_exa1_sknp_vx(x_reg)
            else:
                self._exceptions = f"Unknown EXNN opcode {opcode:04X}"
                self._is_exceptions = True

        elif msn == 0xf:
            lkk = decoder._kk(opcode)
            x_reg = decoder._x(opcode)
            if lkk  == 0x07:
                self._execute_fx07_ld_vx_dt(x_reg)
            elif lkk == 0x0a:
                self._execute_fx0a_ld_vx_k(x_reg)
            elif lkk == 0x15:
                self._execute_fx15_ld_dt_vx(x_reg)
            elif lkk == 0x18:
                self._execute_fx18_ld_st_vx(x_reg)
            elif lkk == 0x1e:
                self._execute_fx1e_add_i_vx(x_reg)
            elif lkk == 0x29:
                self._execute_fx29_ld_f_vx(x_reg)
            elif lkk == 0x33:
                self._execute_fx33_ld_b_vx(x_reg)
            elif lkk == 0x55:
                self._execute_fx55_ld_i_vx(x_reg)
            elif lkk == 0x65:
                self._execute_fx65_ld_vx_i(x_reg)
            else:
                self._exceptions = f"Unknown FXNN opcode {hex(opcode)}"
                self._is_exceptions = True

    def _execute_0x00e0_cls(self):
        """Clear the display."""
        self.display.clear_screen()
        self._pc += 2

    def _execute_0x00ee_ret(self) -> None:
        """Return from a subroutine."""
        
        if self._sp < 0:
            self._exceptions = (
                f"Runtime Error: Stack Underflow! (PC: {hex(self._pc)}, SP: {self._sp})"
            )
            self._is_exceptions = True
            return
        self._pc = self._stack[self._sp]
        self._stack[self._sp] = 0
        self._sp -= 1

    def _execute_1nnn_jp_addr(self, addr: int) -> None:
        """ Jump to location nnn. """
        self._pc = addr
    
    def _execute_2nnn_call_addr(self, addr: int) -> None:
        """Call subroutine at nnn."""
        if self._sp >= self.MAX_STACK_DEPTH:
            self._exceptions = (
                f"Runtime Error: Stack Overflow! (PC: {hex(self._pc)}, SP: {self._sp})"
            )
            self._is_exceptions = True

        self._sp += 1
        self._stack[self._sp] = self._pc
        self._pc = addr

    def _execute_3xkk_se_vx_byte(self, x_reg: int, kk: int) -> None:
        """Skip next instruction if Vx = kk."""
        if self._v[x_reg] == kk:
            self._pc += 4
            return 
        self._pc += 2

    def _execute_4xkk_sne_vx_byte(self, x_reg: int, kk: int) -> None:
        """Skip next instruction if Vx != kk."""
        if self._v[x_reg] != kk:
            self._pc += 4
            return
        self._pc += 2

    def _execute_5xy0_se_vx_vy(self, x_reg: int, y_reg: int) -> None:
        """Skip next instruction if Vx = Vy."""
        if self._v[x_reg] == self._v[y_reg]:
            self._pc += 4
            return 
        self._pc += 2
    
    def _execute_6xkk_ld_vx_byte(self, x_reg: int, kk: int) -> None:
        """Set Vx = kk."""
        self._v[x_reg] = kk
        self._pc += 2
    
    def _execute_7xkk_add_vx_byte(self, x_reg: int, kk: int) -> None:
        """Set Vx = Vx + kk."""
        add = int(self._v[x_reg]) + int(kk)
        self._v[x_reg] = add & 0xff
        self._pc += 2

    def _execute_8xy0_ld_vx_vy(self, x_reg: int, y_reg: int) -> None:
        """Set Vx = Vy."""
        self._v[x_reg] = self._v[y_reg]
        self._pc += 2

    def _execute_8xy1_or_vx_vy(self, x_reg: int, y_reg: int) -> None:
        """Set Vx = Vx OR Vy."""
        self._v[x_reg] = self._v[x_reg] | self._v[y_reg]
        self._pc += 2

    def _execute_8xy2_and_vx_vy(self, x_reg: int, y_reg: int) -> None:
        """Set Vx = Vx AND Vy."""
        self._v[x_reg] = self._v[x_reg] & self._v[y_reg]
        self._pc += 2

    def _execute_8xy3_xor_vx_vy(self, x_reg: int, y_reg: int) -> None:
        """Set Vx = Vx XOR Vy."""
        self._v[x_reg] = self._v[x_reg] ^ self._v[y_reg]
        self._pc += 2

    def _execute_8xy4_add_vx_vy(self, x_reg: int, y_reg: int) -> None:
        """Set Vx = Vx + Vy, set VF = carry."""
        add = self._v[x_reg] + self._v[y_reg]
        self._v[0XF] = 1 if add > 0xff else 0
        self._v[x_reg] = add & 0xff
        self._pc += 2

    def _execute_8xy5_sub_vx_vy(self, x_reg:int , y_reg: int) -> None:
        """Set Vx = Vx - Vy, set VF = NOT borrow. If Vx > Vy, then VF is set to 1, otherwise 0."""
        if self._v[x_reg] >= self._v[y_reg]:
            self._v[0xf] = 1
        else:
            self._v[0xf] = 0
        self._v[x_reg] = int(self._v[x_reg] - self._v[y_reg]) & 0xff
        self._pc += 2

    def _execute_8xy6_shr_vx_vy(self, x_reg: int, y_reg: int) -> None:
        """ Set Vx = Vx SHR 1. 
            If the least-significant bit of Vx is 1, 
            then VF is set to 1, otherwise 0.
            Then Vx is divided by 2.

            y_reg: use for super chip8 later or so
        """
        # self._v[0xf] = self._v[x_reg] & 1
        # self._v[x_reg] = self._v[x_reg] >> 1
        # self._pc += 2
        if self.shift_uses_vy:
            self._v[0xF] = self._v[y_reg] & 1
            self._v[x_reg] = self._v[y_reg] >> 1
        else:
            self._v[0xF] = self._v[x_reg] & 1
            self._v[x_reg] = self._v[x_reg] >> 1
        self._pc += 2

    def _execute_8xy7_subn_vx_vy(self, x_reg: int, y_reg: int) -> None:
        """Set Vx = Vy - Vx, set VF = NOT borrow.
           If Vy > Vx, then VF is set to 1, otherwise 0. 
           Then Vx is subtracted from Vy, and the results stored in Vx.
        """
        if self._v[y_reg] >= self._v[x_reg]:
            self._v[0xf] = 1
        else:
            self._v[0xf] = 0
        
        self._v[x_reg] = np.uint8(self._v[y_reg] - self._v[x_reg])
        self._pc += 2

    def _execute_8xye_shl_vx_vy(self, x_reg: int, y_reg: int) -> None:
        """Set Vx = Vx SHL 1. 
           If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0.
           Then Vx is multiplied by 2.
        """

        if self.shift_uses_vy:
            self._v[0xF] = (self._v[y_reg] & 0x80) >> 7
            self._v[x_reg] = (self._v[y_reg] << 1) & 0xFF
        else:
            self._v[0xF] = (self._v[x_reg] & 0x80) >> 7
            self._v[x_reg] = (self._v[x_reg] << 1) & 0xFF
        self._pc += 2

    def _execute_9xy0_sne_vx_vy(self, x_reg: int, y_reg: int) -> None:
        """Skip next instruction if Vx != Vy."""
        if self._v[x_reg] != self._v[y_reg]:
            self._pc += 4
            return 
        self._pc += 2

    def _execute_annn_ld_i_addr(self, addr: int) -> None:
        """Set I = nnn."""
        self._i = addr
        self._pc += 2

    def _execute_bnnn_jp_v0_addr(self, addr: int) -> None:
        """Jump to location nnn + V0."""
        self._pc = addr + self._v[0x0] 
    
    def _execute_cxkk_rnd_vx_byte(self, x_reg: int, kk:int) -> None:
        """Set Vx = random byte AND kk."""
        self._v[x_reg] = random.randint(0x0, 0xff) & kk
        self._pc += 2
    
    def _execute_dxyn_drw_vx_vy_nibble(self, x_reg: int, y_reg: int, n_height: int) -> None:
        """Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision."""
        x = int(self._v[x_reg])
        y = int(self._v[y_reg])

        self._v[0xf] = 0
        for row in range(n_height):
            sprite_byte = self.memory[int(self._i) + int(row)]
            
            for col in range(8):
                sprite_pixel = (sprite_byte >> (7 - col)) & 1
                if sprite_pixel == 1:
                    if self.display.set_pixel(x + col, y + row):
                        self._v[0xf] = 1
        self._pc += 2

    def _execute_ex9e_skp_vx(self, x_reg: int) -> None:
        """Skip next instruction if key with the value of Vx is pressed.
        Checks the keyboard, and if the key corresponding to the value 
        of Vx is currently in the down position, PC is increased by 2.
        """
        if self.keyboard.is_pressed(self._v[x_reg]):
            self._pc += 4
            return
        self._pc += 2

    def _execute_exa1_sknp_vx(self, x_reg: int) -> None:
        """Skip next instruction if key with the value of Vx is not pressed.
        Checks the keyboard, and if the key corresponding to the value of Vx 
        is currently in the up position, PC is increased by 2.
        """
        if not self.keyboard.is_pressed(self._v[x_reg]):
            self._pc += 4
            return
        self._pc += 2

    def _execute_fx07_ld_vx_dt(self, x_reg: int) -> None:
        """Set Vx = delay timer value."""
        self._v[x_reg] = self._dt
        self._pc += 2
    
    def _execute_fx0a_ld_vx_k(self, x_reg: int) -> None:
        """Wait for a key press, store the value of the key in Vx.
        All execution stops until a key is pressed, then the value of that key is stored in Vx.
        """
        self._is_waiting_key = True
        self._pressed_key = x_reg


    def _execute_fx15_ld_dt_vx(self, x_reg: int) -> None:
        """Set delay timer = Vx.
        DT is set equal to the value of Vx.
        """
        self._dt = self._v[x_reg]
        self._pc += 2

    def _execute_fx18_ld_st_vx(self, x_reg: int) -> None:
        """Set sound timer = Vx.
        ST is set equal to the value of Vx.
        """
        self._st = self._v[x_reg]
        self._pc += 2

    def _execute_fx1e_add_i_vx(self, x_reg: int) -> None:
        """Set I = I + Vx.
        The values of I and Vx are added, and the results are stored in I.
        """
        add = int(self._i) + int(self._v[x_reg])
        self._v[0xF] = 1 if add > 0xFFF else 0
        self._i = add & 0X0FFF
        self._pc += 2

    def _execute_fx29_ld_f_vx(self, x_reg: int) -> None:
        """Set I = location of sprite for digit Vx."""
        i = int(self._v[x_reg]) * 5
        self._i = i & 0X0FFF
        self._pc += 2

    def _execute_fx33_ld_b_vx(self, x_reg: int) -> None:
        """Store BCD representation of Vx in memory locations I, I+1, and I+2.
        The interpreter takes the decimal value of Vx, and places the hundreds digit 
        in memory at location in I, the tens digit at location I+1, and the ones digit
        at location I+2."""
        value = self._v[x_reg]
        self.memory[self._i] = value // 100
        self.memory[self._i + 1] = (value % 100) // 10
        self.memory[self._i + 2] = value % 10
        self._pc += 2

    def _execute_fx55_ld_i_vx(self, x_reg: int) -> None:
        """Store registers V0 through Vx in memory starting at location I.
        The interpreter copies the values of registers V0 through Vx into memory, 
        starting at the address in I."""
        for x in range(x_reg + 1):
            self.memory[self._i + x] = self._v[x]

        if self.increment_i:  # COSMAC VIP style
            self._i += x_reg + 1

        self._pc += 2
    def _execute_fx65_ld_vx_i(self, x_reg: int) -> None:
        """Read registers V0 through Vx from memory starting at location I.
        The interpreter reads values from memory starting at location I 
        into registers V0 through Vx.
        """
        for x in range(x_reg + 1):
            self._v[x] = self.memory[self._i + x]

        if self.increment_i:  # COSMAC VIP style
            self._i += x_reg + 1

        self._pc += 2

    def update_timer(self):
        """Decrements the delay and sound timers."""
        if self._dt > 0:
            self._dt -= 1
        
        if self._st > 0:
            self._st -= 1
            # add sound playing logic here.

