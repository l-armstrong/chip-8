from enum import Enum
import pygame

class Config(object):
    def __init__(self, window_width, window_height, fg_color, bg_color, scale_factor, pixel_outlines):
        self.window_width = window_width
        self.window_height = window_height
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.scale_factor = scale_factor
        self.pixel_outlines - pixel_outlines

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
    def __init__(self, state, pc, rom_name, inst):
        self.state = state
        self.ram = [0] * (4096)
        self.display = [0] * (64*32)
        self.stack = [0] * (12)
        self.stack_ptr = 0
        self.V = [0] * (16)
        self.PC = pc
        self.delay_timer = 0
        self.sound_timer = 0
        self.keypad = [0] * (16)
        self.rom_name = rom_name
        self.inst = inst

