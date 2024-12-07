"""
Chip-8 is a interpreted programming language. 
- takes up 512 bytes of memory
"""
from enum import Enum
import random
import tkinter as tk

max_memory = (1 << 12)
memory = [b''] * (max_memory)  # 4096 addresses 
                                # index regs and pc can only address 12 bits
stack = [0]*16
sp = -1 # Possible change to 0?
pc = 512
register = [0]*16 # Vx where x is a hexadecimal digit
i_register = 0 # register I; store memory addresses; right most 12 bits are used
VF = 0 # Flag register?
delay_timer = 0
sound_timer = 0
screen = [0] * (64 * 32) 
# convention is 0x050–0x09F for font_start
# font_start = 200
font_start = 0x050
keys = [False] * 16
current_down_key = None
"""
Key layout
1	2	3	C
4	5	6	D
7	8	9	E
A	0	B	F

use keyboard scancodes rather than key string constants
"""
window = tk.Tk()
canvas = tk.Canvas(window, width=64*16, height=32*16)
canvas.pack()

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

class OP(Enum):
    SYS     = 0  # SYS addr
    CLS     = 1
    RET     = 2
    JP      = 3
    CALL    = 4
    SE      = 5
    SNE     = 6 
    SE_XY   = 7 # SE Vx, Xy
    LD      = 8    # LD Vx, byte
    ADD     = 9   # ADD Vx, byte
    LD_XY   = 10 # LD Vx, Vy
    OR_XY   = 11 # OR Vx, Vy
    AND_XY  = 12 # AND Vx, Vy
    XOR_XY  = 13 # XOR XY
    ADD_XY  = 14 # ADD Vx, Vy
    SUB_XY  = 15
    SHR     = 16
    SUBN    = 17
    SHL     = 18
    SNE_XY  = 19
    LD_IA   = 20
    JP_VA   = 21
    RND     = 22
    DRW     = 23
    SKP     = 24
    SKNP    = 25
    LD_XDT  = 26
    LD_XKEY = 27
    LD_DTX  = 28
    LD_STVX = 29
    ADD_IX  = 30
    LD_FX   = 31
    LD_BX   = 32
    LD_IX   = 33 # LD [I], Vx
    LD_XI   = 34 # LD Vx, [I]

def view_screen(): 
    for i in range(32):
        print("".join(map(lambda x: '.' if x == 0 else '*', (screen[i*64: (i + 1) * 64]))))

def decode_instruction(instruction):
    first_nibble = (0xF000 & instruction) >> 12
    second_nibble = (0x0F00 & instruction) >> 8
    third_nibble = (0x00F0 & instruction) >> 4
    fourth_nibble = (0x000F & instruction) 
    nibbles = (first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
    if first_nibble == 0x0:
        if fourth_nibble == 0x0:
            return (OP.CLS, None) # Clear the display
        elif fourth_nibble == 0xE: # Return
            return (OP.RET, None)
        else:
            return (OP.SYS, nibbles) # nnn variable := instruction[1:]
    elif first_nibble == 0x01:
        return (OP.JP, nibbles)
    elif first_nibble == 0x2:
        return (OP.CALL, nibbles)
    elif first_nibble == 0x3:
        return (OP.SE, nibbles)
    elif first_nibble == 0x4:
        return (OP.SNE, nibbles)
    elif first_nibble == 0x5:
        return (OP.SE_XY, nibbles)
    elif first_nibble == 0x6:
        return (OP.LD, nibbles)
    elif first_nibble == 0x7: 
        return (OP.ADD, nibbles)
    elif first_nibble == 0x8:
        if fourth_nibble == 0x0:
            return (OP.LD_XY, nibbles)
        elif fourth_nibble == 0x1:
            return (OP.OR_XY, nibbles)
        elif fourth_nibble == 0x2:
            return (OP.AND_XY, nibbles)    
        elif fourth_nibble == 0x3:
            return (OP.XOR_XY, nibbles)
        elif fourth_nibble == 0x4:
            return (OP.ADD_XY, nibbles)
        elif fourth_nibble == 0x5:
            return (OP.SUB_XY, nibbles)
        elif fourth_nibble == 0x6:
            return (OP.SHR, nibbles)
        elif fourth_nibble == 0x7:
            return (OP.SUBN, nibbles)
        elif fourth_nibble == 0xE:
            return (OP.SHL, nibbles)
    elif first_nibble == 0x9:
        return (OP.SNE_XY, nibbles)
    elif first_nibble == 0xA:
        return (OP.LD_IA, nibbles)
    elif first_nibble == 0xB:
        return (OP.JP_VA, nibbles)
    elif first_nibble == 0xC:
        return (OP.RND, nibbles)
    elif first_nibble == 0xD:
        return (OP.DRW, nibbles)
    elif first_nibble == 0xE: 
        if fourth_nibble == 0xE:
            return (OP.SKP, nibbles)
        elif fourth_nibble == 0x1:
            return (OP.SKNP, nibbles)
    elif first_nibble == 0xF:
        if fourth_nibble == 0x7:
            return (OP.LD_XDT, nibbles)
        elif fourth_nibble == 0xA:
            return (OP.LD_XKEY, nibbles)
        elif third_nibble == 0x1 and fourth_nibble == 0x5:
            return (OP.LD_DTX, nibbles)
        elif fourth_nibble == 0x8:
            return (OP.LD_STVX, nibbles)
        elif fourth_nibble == 0xE:
            return (OP.ADD_IX, nibbles)
        elif fourth_nibble == 0x9:
            return (OP.LD_FX, nibbles)
        elif fourth_nibble == 0x3:
            return (OP.LD_BX, nibbles)
        elif third_nibble == 0x5 and fourth_nibble == 0x5:
            return (OP.LD_IX, nibbles)
        elif third_nibble == 0x6 and fourth_nibble == 0x5:
            return (OP.LD_XI, nibbles)
    # return (None, None)
    raise NotImplementedError(f"Instruction unknown: {instruction}")

def execute_instruction(opcode, args): 
    global pc
    global stack
    global sp
    global VF
    global i_register 
    global delay_timer
    global sound_timer
    global screen

    if args and len(args) == 5:
        first_nibble, second_nibble, third_nibble, fourth_nibble, instruction = args
    if opcode == OP.SYS:
        print("SYS")
    elif opcode == OP.CLS:
        screen = [0] * (64 * 32) 
        draw_screen()
    elif opcode == OP.RET:
        pc = stack[sp]
        sp = sp - 1
    elif opcode == OP.JP: 
        instruction = args[-1]
        pc = instruction & 0x0FFF
    elif opcode == OP.CALL:
        sp += 1
        stack[sp] = pc
        pc = instruction & 0x0FFF
    elif opcode == OP.SE:
        vx = register[second_nibble]
        if vx == (instruction & 0x0FF): pc += 2
    elif opcode == OP.SNE:
        vx = register[second_nibble]
        if vx != (instruction & 0x0FF): pc += 2
    elif opcode == OP.SE_XY:
        vx = register[second_nibble]
        vy = register[third_nibble]
        if (vx == vy): pc += 2
    elif opcode == OP.LD:
        register[second_nibble] = instruction & 0x0FF
    elif opcode == OP.ADD:
        # TODO, possible change this?
        register[second_nibble] = (register[second_nibble] + (instruction & 0x0FF)) % 256
    elif opcode == OP.LD_XY: 
        register[second_nibble] = register[third_nibble]
    elif opcode == OP.OR_XY: 
        register[second_nibble] = register[second_nibble] | register[third_nibble]
    elif opcode == OP.AND_XY:
        register[second_nibble] = register[second_nibble] & register[third_nibble]
    elif opcode == OP.XOR_XY:
        register[second_nibble] = register[second_nibble] ^ register[third_nibble]  
    elif opcode == OP.ADD_XY:
        vx, vy = register[second_nibble], register[third_nibble]
        _sum = vx + vy
        if (_sum > 255): VF = 1
        else: VF = 0
        register[second_nibble] = 0x0FF & _sum # only lowest 8 bits (1 byte) are kept
    elif opcode == OP.SUB_XY:
        vx, vy = register[second_nibble], register[third_nibble]
        difference = vx - vy
        if (vx > vy): VF = 1
        else: VF = 0
        register[second_nibble] = difference
    elif opcode == OP.SHR:
        # TODO: maybe could lead to errors
        # if (second_nibble & 0x01): VF = 1
        # else: VF = 0
        # register[second_nibble] = register[second_nibble] >> 1
        register[second_nibble] = register[third_nibble]
        if register[second_nibble] & 0x01: VF = 1
        else: VF = 0
        register[second_nibble] = register[second_nibble] >> 1
    elif opcode == OP.SUBN:
        vx, vy = register[second_nibble], register[third_nibble]
        difference = vy - vx
        if (vy > vx): VF = 1
        else: VF = 0
        register[second_nibble] = difference
    elif opcode == OP.SHL:
        # TODO: maybe could lead to errors
        # if (second_nibble & 0x01): VF = 1
        # else: VF = 0
        # register[second_nibble] = register[second_nibble] << 1
        register[second_nibble] = register[third_nibble]
        if register[second_nibble] & 0x01: VF = 1
        else: VF = 0
        register[second_nibble] = register[second_nibble] << 1
    elif opcode == OP.SNE_XY:
        vx = register[second_nibble]
        vy = register[third_nibble]
        if vx != vy: pc += 2
    elif opcode == OP.LD_IA:
        i_register = (0x0FFF & instruction)
    elif opcode == OP.JP_VA:
        pc = register[0] + (0x0FFF & instruction)
    elif opcode == OP.RND:
        register[second_nibble] = (random.randint(0, 255) & (instruction & 0x0FF))
    elif opcode == OP.DRW: 
        Vx, Vy = register[second_nibble] % 64, register[third_nibble] % 32
        n = fourth_nibble
        sprite_data = [bin(int(data.hex() if data else b'0x00', base=16))[2:].zfill(8) for data in memory[i_register: i_register + n]]
        sprite = [list(map(int, row)) for row in sprite_data]
        draw_sprite(Vx, Vy, sprite)
        draw_screen()
        # view_screen() # TODO: remove; for debugging
    elif opcode == OP.SKP:
        # TODO: change? possible off by one?
        # key_pressed = keys[register[second_nibble] - 1]
        key_pressed = keys[register[second_nibble] - 1]
        if key_pressed: pc += 2
    elif opcode == OP.SKNP:
        # TODO: change? possible off by one?
        # key_pressed = keys[register[second_nibble] - 1]
        key_pressed = keys[register[second_nibble] - 1]
        if not key_pressed: pc += 2
    elif opcode == OP.LD_XDT:
        register[second_nibble] = delay_timer
    elif opcode == OP.LD_XKEY:
        if not any(keys):
            pc -= 2
        else:
            for i, k in enumerate(keys):
                if k:
                    register[second_nibble] = i
    elif opcode == OP.LD_DTX:
        delay_timer = register[second_nibble]
    elif opcode == OP.LD_STVX:
        sound_timer = register[second_nibble]
    elif opcode == OP.ADD_IX:
        i_register = i_register + register[second_nibble]
    elif opcode == OP.LD_FX:
        i_register = font_start + (register[second_nibble] * 5)
    elif opcode == OP.LD_BX:
        Vx = register[second_nibble]
        memory[i_register] = (Vx // 100) % 10 
        memory[i_register + 1] = (Vx // 10) % 10
        memory[i_register + 2] = Vx % 10
    elif opcode == OP.LD_IX:
        for i in range(second_nibble):
            memory[i_register + i] = register[i].to_bytes(1, 'big')
        i_register = i_register + second_nibble + 1
    elif opcode == OP.LD_XI:
        for i in range(second_nibble):
            element = memory[i_register + i]
            register[i] = element if isinstance(element, int) else int.from_bytes(element, 'big')
        i_register = i_register + second_nibble + 1
    else: raise NotImplementedError(f"Opcode {opcode} not implemented")

with open("PONG.ch8", "rb") as f:
    f_start = font_start
    for i, char in enumerate(font):
        memory[font_start + i] = char.to_bytes(1, 'big')
    i = 512
    while (byte := f.read(1)):
        memory[i] = byte
        i += 1


def set_pixel(x, y, state):
    global VF
    current_value = screen[(y * 64) + x]
    if current_value and state:
        screen[(y* 64) + x] = 0
        VF = 1
    else:
        screen[(y * 64) + x] = state
        VF = 0

def draw_row(start_x, start_y, row):
    for i, x in enumerate(row): 
        set_pixel(start_x + i, start_y, x)

# def draw_row_n(start_x, start_y, n, row):
#     for i in range(n):
#         draw_row(start_x, start_y + i, row)

def draw_sprite(start_x, start_y, sprite):
    for i, row in enumerate(sprite):
        draw_row(start_x, start_y + i, row)

def set_key(index, is_down):
    keys[index] = is_down

ran = False
def step():
    global pc
    global ran

    print("running step: ", pc)
    instruction = memory[pc:pc+2]
    pc += 2
    print("instruction:",instruction)

    processed_instruction = int.from_bytes(b"".join(instruction), byteorder='big')
    print("[DEBUG] processed_instruction:", processed_instruction)
    op_code, args = decode_instruction(processed_instruction)
    execute_instruction(op_code, args)
    if not ran: draw_screen(); ran = True
    window.after(1, step)

def draw_screen():
    canvas.delete("all")
    for x in range(64):
        for y in range(32):
            if screen[(y * 64) + x] == 1:
                canvas.create_rectangle(x*16, y*16, (x+1)*16, (y+1)*16, outline='white', fill='white')

def decrease_time():
    global delay_timer
    global sound_timer
    if delay_timer > 0: delay_timer -= 1
    if sound_timer > 0: sound_timer -= 1
    window.after(16, decrease_time)


def handle_keypress(e):
    if e.keysym == 'x':
        keys[0] = True
    elif e.keysym == '1':
        keys[1] = True
    elif e.keysym == '2':
        keys[2] = True
    elif e.keysym == '3':
        keys[3] = True
    elif e.keysym == 'q':
        keys[4] = True
    elif e.keysym == 'w':
        keys[5] = True
    elif e.keysym == 'e':
        keys[6] = True
    elif e.keysym == 'a':
        keys[7] = True
    elif e.keysym == 's':
        keys[8] = True
    elif e.keysym == 'd':
        keys[9] = True
    elif e.keysym == 'z':
        keys[10] = True
    elif e.keysym == 'c':
        keys[11] = True
    elif e.keysym == '4':
        keys[12] = True
    elif e.keysym == 'r':
        keys[13] = True
    elif e.keysym == 'f':
        keys[14] = True
    elif e.keysym == 'v':
        keys[15] = True
    print("[DEBUG]: keys", keys)
    print("[DEBUG]: event", e)

def handle_keyrelease(e):
    if e.keysym == 'x':
        keys[0] = False
    elif e.keysym == '1':
        keys[1] = False
    elif e.keysym == '2':
        keys[2] = False
    elif e.keysym == '3':
        keys[3] = False
    elif e.keysym == 'q':
        keys[4] = False
    elif e.keysym == 'w':
        keys[5] = False
    elif e.keysym == 'e':
        keys[6] = False
    elif e.keysym == 'a':
        keys[7] = False
    elif e.keysym == 's':
        keys[8] = False
    elif e.keysym == 'd':
        keys[9] = False
    elif e.keysym == 'z':
        keys[10] = False
    elif e.keysym == 'c':
        keys[11] = False
    elif e.keysym == '4':
        keys[12] = False
    elif e.keysym == 'r':
        keys[13] = False
    elif e.keysym == 'f':
        keys[14] = False
    elif e.keysym == 'v':
        keys[15] = False
    print("[DEBUG]: keys", keys)
    print("[DEBUG]: event", e)

window.after(16, decrease_time)       
window.after(1, step)  
window.bind("<Key>", handle_keypress)        
window.bind("<KeyRelease>", handle_keyrelease)
window.mainloop()