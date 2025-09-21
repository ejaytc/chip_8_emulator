# nnn or addr - A 12-bit value, the lowest 12 bits of the instruction
# n or nibble - A 4-bit value, the lowest 4 bits of the instruction
# x - A 4-bit value, the lower 4 bits of the high byte of the instruction
# y - A 4-bit value, the upper 4 bits of the low byte of the instruction
# kk or byte - An 8-bit value, the lowest 8 bits of the instruction

class Decoder:
    def _addr(self, instruction: int) -> int:
        return instruction & 0X0FFF

    def _nibble(self, instruction: int) -> int:
        return instruction >> 12
    
    def _x(self, instruction: int) -> int:
        return instruction >> 8 & 0X0F
    
    
    def _y(self, instruction: int) -> int:
        return instruction >> 4 & 0X0F

    def _kk(self, instruction: int) -> int:
        return instruction & 0x00FF
    
    def _n(self, instruction: int) -> int:
        return instruction & 0X000F