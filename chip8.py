from enum import Enum
import pygame
import sys

class Config(object):
    def __init__(self, window_width, window_height, fg_color, bg_color, scale_factor, pixel_outlines=True):
        self.window_width = window_width
        self.window_height = window_height
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.scale_factor = scale_factor
        self.pixel_outlines = pixel_outlines

class Emulator_State(Enum):
    QUIT = 0
    RUNNING = 1
    PAUSED = 2

class Instruction(object):
    def __init__(self, opcode, nnn, nn, n, x, y):
        self.opcode = opcode
        self.nnn = nnn
        self.nn = nn
        self.n = n
        self.x = x
        self.y = y

class Chip8(object):
    def __init__(self, state, pc, rom_name):
        self.state = state
        self.ram = [0] * (4096)
        self.display = [0] * (64*32)
        self.stack = [0] * (12)
        self.stack_ptr = 0
        self.V = [0] * (16)
        self.I = 0
        self.PC = pc
        self.delay_timer = 0
        self.sound_timer = 0
        self.keypad = [0] * (16)
        self.rom_name = rom_name
        self.inst = Instruction(None, None, None, None, None, None)

def init_chip8(rom_name):
    rom_entry = 0x200
    chip8 = Chip8(state=Emulator_State.RUNNING, pc=rom_entry, rom_name=rom_name)
    font = [
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
    ]
    # Load font in RAM
    for i, byte in enumerate(font):
        chip8.ram[i] = byte

    # rom = open(rom_name, "rb")
    # for i, byte in enumerate(rom.read()):
    #     chip8.ram[rom_entry + i] = byte
    # Close ROM stream
    # rom.close()

    # Load ROM in RAM from ROM entry point
    i = 0
    with open(rom_name, "rb") as f:
        while (byte := f.read(1)):
            chip8.ram[rom_entry + i] = int.from_bytes(byte, byteorder="big")
            i += 1
    return chip8

def handle_input(chip8: Chip8):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            chip8.state = Emulator_State.QUIT

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                chip8.state = Emulator_State.QUIT
            
def run_instruction(chip8: Chip8, config: Config): 
    # get current opcode to run
    chip8.inst.opcode = (chip8.ram[chip8.PC] << 8) | (chip8.ram[chip8.PC+1])
    chip8.inst.nnn, chip8.inst.nn, chip8.inst.n = (chip8.inst.opcode & 0x0FFF), (chip8.inst.opcode & 0x0FF), (chip8.inst.opcode & 0x0F)
    chip8.inst.x = (chip8.inst.opcode >> 8) & 0x0F
    chip8.inst.y = (chip8.inst.opcode >> 4) & 0x0F
    # increment PC for next opcode
    chip8.PC += 2

    match ((chip8.inst.opcode >> 12) & 0x0F): 
        case 0x0:
            if chip8.inst.nn == 0xE0:
                # 0x00E0: Clear screen
                chip8.display = [0] * len(chip8.display)
            elif chip8.inst.nn == 0xEE:
                # 0x00EE: Return from subroutine
                chip8.stack_ptr -= 1 # pop off address from stack
                chip8.PC =  chip8.stack[chip8.stack_ptr]
        case 0x1:
            # 0x1NNN: Jump to address NNN 
            chip8.PC = chip8.inst.nnn
        case 0x02:
            # 0x2NNN: Call subroutine
            chip8.stack[chip8.stack_ptr] = chip8.PC # store current address on stack
            chip8.stack_ptr += 1
            chip8.PC = chip8.inst.nnn # manipulate PC to call subroutine
        case 0x03:
            # 0x3XNN: Check if VX == NN, if so, skip the next instruction
            if chip8.V[chip8.inst.x] == chip8.inst.nn:
                chip8.PC += 2   # Skip next opcode
        case 0x04:
            # 0x4XNN: Check if VX != NN, if so, skip next instruction
            if chip8.V[chip8.inst.x] != chip8.inst.nn:
                chip8.PC += 2   # Skip next opcode
        case 0x05:
            # 0x5XY0: Check if VX == VY, if so, skip next instruction
            if chip8.V[chip8.inst.x] == chip8.V[chip8.inst.y]:
                chip8.PC += 2   # Skip next opcode
        case 0x6:
            # 0x6XNN: Set register VX to NN
            chip8.V[chip8.inst.x] = chip8.inst.nn
        case 0x7:
            # 0x7XNN: Set register VX += NN
            chip8.V[chip8.inst.x] += chip8.inst.nn
        case 0x08:
            # ALU OP codes
            match chip8.inst.n:
                case 0x0:
                    # 0x8XY0: Set register VX = VY
                    chip8.V[chip8.inst.x] = chip8.V[chip8.inst.y]
                case 0x1:
                    # 0x8XY1: Set register VX |= VY
                    chip8.V[chip8.inst.x] |= chip8.V[chip8.inst.y]
                case 0x2:
                    # 0x8XY2: Set register VX &= VY
                    chip8.V[chip8.inst.x] &= chip8.V[chip8.inst.y]
                case 0x3:
                    # 0x8XY3: Set register VX ^= VY
                    chip8.V[chip8.inst.x] ^= chip8.V[chip8.inst.y]
                case 0x4:
                    # 0x8XY4: Set register VX += VY, set VF to 1 if carry
                    if (chip8.V[chip8.inst.x] + chip8.V[chip8.y]) > 255:
                        chip8.V[0xF] = 1
                    chip8.V[chip8.inst.x] += chip8.v[chip8.inst.y]
                case 0x5:
                    # 0x8XY5: Set register VX -= 1, set VF to 1 if result is positive
                    chip8.V[0xF] = chip8.V[chip8.inst.y] <= chip8.v[chip8.inst.x]
                    chip8.V[chip8.inst.x] -= chip8.V[chip8.inst.y]
                case 0x6:
                    # 0x8XY6: Set register VX >> 1, Store shifted off but in VF
                    chip8.V[0xF] = chip8.V[chip8.inst.x] & 1
                    chip8.V[chip8.inst.x] >>= 1
                case 0x7:
                    # 0x8XY7: Set register VX = VY - VX, set VF to 1 if result is positive
                    chip8.V[0xF] = chip8.V[chip8.inst.x] <= chip8.v[chip8.inst.y]
                    chip8.V[chip8.inst.x] = chip8.v[chip8.inst.y] - chip8.V[chip8.inst.x]
                case 0xE:
                    # 0x8XYE: Set register VX << 1, store shifted off bit in VF
                    chip8.V[0xF] = (chip8.V[chip8.inst.x] & 0x80) >> 7
                    chip8.V[chip8.inst.x] <<= 1
                
        case 0xA:
            # 0xANNN: Set index register I to NNN
            chip8.I = chip8.inst.nnn
        case 0xD:
            # 0xDXYN: Draw N-height sprite at coords (x, y)
            # Read from memory location I;
            x = chip8.V[chip8.inst.x] % config.window_width
            y = chip8.V[chip8.inst.y] % config.window_height
            orig_x = x
            # Initialize carry flag to 0
            chip8.V[0xF] = 0

            for i in range(chip8.inst.n):
                # get next byte of sprite data
                sprite_data = chip8.ram[chip8.I + i]
                x = orig_x  # reset x
                # from most significant to least significant bit 
                for j in range(7, -1, -1):
                    pixel = chip8.display[y * config.window_width + x]
                    sprite_bit = (sprite_data & (1 << j))

                    # if current pixel is on and the current sprite bit is on 
                    # set VF to 1
                    if sprite_bit and pixel: chip8.V[0xF] = 1

                    # store new state to display in memory
                    chip8.display[y * config.window_width + x] ^= sprite_bit
                    x += 1

                    # if reach right edge of screen, stop drawing
                    if x >= config.window_width: break
                y += 1
                # stop drawing if reach bottom edge of screen
                if  y >= config.window_height: break

def update_screen(chip8: Chip8, config: Config): 
    rect = pygame.Rect(0, 0, config.scale_factor, config.scale_factor)

    fg_r = (config.fg_color >> 24) & 0xFF
    fg_g = (config.fg_color >> 16) & 0xFF
    fg_b = (config.fg_color >>  8) & 0xFF
    fg_a = (config.fg_color >>  0) & 0xFF

    bg_r = (config.bg_color >> 24) & 0xFF
    bg_g = (config.bg_color >> 16) & 0xFF
    bg_b = (config.bg_color >>  8) & 0xFF
    bg_a = (config.bg_color >>  0) & 0xFF

    for i in range(len(chip8.display)):
        rect.x = (i % config.window_width) * config.scale_factor
        rect.y = (i // config.window_width) * config.scale_factor

        if (chip8.display[i]): pygame.draw.rect(screen, (fg_r, fg_g, fg_b, fg_a), rect)
        else: pygame.draw.rect(screen, (bg_r, bg_g, bg_b, bg_a), rect)


if __name__ == '__main__': 
    # if len(sys.argv) < 2:
    #     print(f"Usage: {sys.argv[0]} <rom_name>")
    #     exit(1)
    config = Config(64, 32, 0xFFFFFFFF, 0x00000000, 20)
    pygame.init()
    screen = pygame.display.set_mode((config.window_width*config.scale_factor, config.window_height*config.scale_factor))
    clock = pygame.time.Clock()
    chip8 = init_chip8("test_opcode.ch8")

    while chip8.state != Emulator_State.QUIT:
        handle_input(chip8)
        run_instruction(chip8, config)
        update_screen(chip8, config)
        pygame.display.flip()
        clock.tick(60)

