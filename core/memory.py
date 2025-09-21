# Memory Map:
# +---------------+= 0xFFF (4095) End of Chip-8 RAM
# |               |
# |               |
# |               |
# |               |
# |               |
# | 0x200 to 0xFFF|
# |     Chip-8    |
# | Program / Data|
# |     Space     |
# |               |
# |               |
# |               |
# +- - - - - - - -+= 0x600 (1536) Start of ETI 660 Chip-8 programs
# |               |
# |               |
# |               |
# +---------------+= 0x200 (512) Start of most Chip-8 programs
# | 0x000 to 0x1FF|
# | Reserved for  |
# |  interpreter  |
# +---------------+= 0x000 (0) Start of Chip-8 RAM

class Memory:
    __CHAR_CONTANTS = [
        # 0
        0XF0, # 1111 0000
        0X90, # 1001 0000
        0X90, # 1001 0000
        0X90, # 1001 0000
        0XF0, # 1111 0000
        # 1
        0X20, # 0010 0000
        0X60, # 0110 0000
        0X20, # 0010 0000
        0X20, # 0010 0000
        0X70, # 0111 0000
        # 2
        0XF0, # 1111 0000
        0X10, # 0001 0000
        0XF0, # 1111 0000
        0X80, # 1000 0000
        0XF0, # 1111 0000
        # 3
        0XF0, # 1111 0000
        0X10, # 0001 0000
        0XF0, # 1111 0000
        0X10, # 0001 0000
        0XF0, # 1111 0000
        # 4
        0X90, # 1001 0000
        0X90, # 1001 0000
        0XF0, # 1111 0000
        0X10, # 0001 0000
        0X10, # 0001 0000
        # 5
        0XF0, # 1111 0000
        0X80, # 1000 0000
        0XF0, # 1111 0000
        0X10, # 0001 0000
        0XF0, # 1111 0000
        # 6
        0XF0, # 1111 0000
        0X80, # 1000 0000
        0XF0, # 1111 0000
        0X90, # 1001 0000
        0XF0, # 1111 0000
        # 7
        0XF0, # 1111 0000
        0X10, # 0001 0000
        0X20, # 0010 0000
        0X40, # 0100 0000
        0X40, # 0100 0000
        # 8
        0XF0, # 1111 0000
        0X90, # 1001 0000
        0XF0, # 1111 0000
        0X90, # 1001 0000
        0XF0, # 1111 0000
        # 9
        0XF0, # 1111 0000
        0X90, # 1001 0000
        0XF0, # 1111 0000
        0X10, # 0001 0000
        0XF0, # 1111 0000
        # A
        0XF0, # 1111 0000
        0X90, # 1OO1 0000
        0XF0, # 1111 0000
        0X90, # 1001 0000
        0X90, # 1001 0000
        # B
        0XE0, # 1110 0000
        0X90, # 1001 0000
        0XE0, # 1110 0000
        0X90, # 1001 0000
        0XE0, # 1110 0000
        # C,
        0XF0, # 1111 0000
        0X80, # 1000 0000
        0X80, # 1000 0000
        0X80, # 1000 0000
        0XF0, # 1111 0000
        # D
        0XE0, # 1110 0000
        0X90, # 1001 0000
        0X90, # 1001 0000
        0X90, # 1001 0000
        0XE0, # 1110 0000
        # E
        0XF0, # 1111 0000
        0X80, # 1000 0000
        0XF0, # 1111 0000
        0X80, # 1000 0000
        0XF0, # 1111 0000
        # F
        0XF0, # 1111 0000
        0X80, # 1000 0000
        0XF0, # 1111 0000
        0X80, # 1000 0000
        0X80, # 1000 0000
    ]

    def __init__(self) -> None:
        self.__memory = bytearray(4096)
        self.__init_default_sprite()

    def __len__(self) -> int:
        return len(self.__memory)

    def __init_default_sprite(self) -> None:
        location = 0X0 # Most emulator start in 0x050 for the default sprite. 
        for char_sprite in self.__CHAR_CONTANTS:
            self.__memory[location] = char_sprite
            location += 1

    def __getitem__(self, key: slice | int) -> list:
        if isinstance(key, slice):
            return self.__memory[key]
        elif isinstance(key, int):
            return self.__memory[key]

        raise TypeError(
            f"Memory indices must be integers or slices, not {type(key).__name__}"
        )

    def __setitem__(self, location: int, data: int) -> None:
        self.__memory[location] = data
    
    def __repr__(self) -> str:
        return f"Type={type(self.__memory).__name__}  size={len(self.__memory)}"
    
    def clear(self) -> None:
        self.__memory = bytearray(len(self.__memory))

    
