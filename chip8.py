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
font_start = 200
keys = [False] * 16
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
    SYS = 0  # SYS addr
    CLS = 1
    RET = 2
    JP  = 3
    CALL = 4
    SE = 5
    SNE = 6 
    SE_XY = 7 # SE Vx, Xy
    LD = 8    # LD Vx, byte
    ADD = 9   # ADD Vx, byte
    LD_XY = 10 # LD Vx, Vy
    OR_XY = 11 # OR Vx, Vy
    AND_XY = 12 # AND Vx, Vy
    XOR_XY = 13 # XOR XY
    ADD_XY = 14 # ADD Vx, Vy
    SUB_XY = 15
    SHR = 16
    SUBN = 17
    SHL = 18
    SNE_XY = 19
    LD_IA = 20
    JP_VA = 21
    RND = 22
    DRW = 23
    SKP = 24
    SKNP = 25
    LD_XDT = 26
    LD_XKEY = 27
    LD_DTX = 28
    LD_STVX = 29
    ADD_IX = 30
    LD_FX = 31
    LD_BX = 32
    LD_IX = 33 # LD [I], Vx
    LD_XI = 34 # LD Vx, [I]

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
        print("0x0:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        if fourth_nibble == 0x0:
            return (OP.CLS, None) # Clear the display
        elif fourth_nibble == 0xE: # Return
            return (OP.RET, None)
        else:
            return (OP.SYS, nibbles) # nnn variable := instruction[1:]
    elif first_nibble == 0x01:
        print("0x1:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.JP, nibbles)
    elif first_nibble == 0x2:
        print("0x2:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.CALL, nibbles)
    elif first_nibble == 0x3:
        print("0x3:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.SE, nibbles)
    elif first_nibble == 0x4:
        print("0x4:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.SNE, nibbles)
    elif first_nibble == 0x5:
        print("0x5:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.SE_XY, nibbles)
    elif first_nibble == 0x6:
        print("0x6:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.LD, nibbles)
    elif first_nibble == 0x7: 
        print("0x7:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.ADD, nibbles)
    elif first_nibble == 0x8:
        if fourth_nibble == 0x0:
            print("0x8_0:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.LD_XY, nibbles)
        elif fourth_nibble == 0x1:
            print("0x8_1:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.OR_XY, nibbles)
        elif fourth_nibble == 0x2:
            print("0x8_2:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.AND_XY, nibbles)    
        elif fourth_nibble == 0x3:
            print("0x8_3:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.XOR_XY, nibbles)
        elif fourth_nibble == 0x4:
            print("0x8_4:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.ADD_XY, nibbles)
        elif fourth_nibble == 0x5:
            print("0x8_5:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.SUB_XY, nibbles)
        elif fourth_nibble == 0x6:
            print("0x8_6:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.SHR, nibbles)
        elif fourth_nibble == 0x7:
            print("0x8_7:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.SUBN, nibbles)
        elif fourth_nibble == 0xE:
            return (OP.SHL, nibbles)
    elif first_nibble == 0x9:
        print("0x9:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.SNE_XY, nibbles)
    elif first_nibble == 0xA:
        print("0xA:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.LD_IA, nibbles)
    elif first_nibble == 0xB:
        print("0xB:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.JP_VA, nibbles)
    elif first_nibble == 0xC:
        print("0xC:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.RND, nibbles)
    elif first_nibble == 0xD:
        print("0xD:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.DRW, nibbles)
    elif first_nibble == 0xE: 
        if fourth_nibble == 0xE:
            print("0xEx9E:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.SKP, nibbles)
        elif fourth_nibble == 0x1:
            print("0xExA1:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.SKNP, nibbles)
    elif first_nibble == 0xF:
        if fourth_nibble == 0x7:
            print("0xF07", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.LD_XDT, nibbles)
        elif fourth_nibble == 0xA:
            print("0xFx0A:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.LD_XKEY, nibbles)
        elif third_nibble == 0x1 and fourth_nibble == 0x5:
            print("0xFx15:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.LD_DTX, nibbles)
        elif fourth_nibble == 0x8:
            print("0xFx18:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.LD_STVX, nibbles)
        elif fourth_nibble == 0xE:
            print("0xFx1E:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.ADD_IX, nibbles)
        elif fourth_nibble == 0x9:
            print("0xFx29:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.LD_FX, nibbles)
        elif fourth_nibble == 0x3:
            print("0xFx33:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.LD_BX, nibbles)
        elif third_nibble == 0x5 and fourth_nibble == 0x5:
            print("0xFx55:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.LD_IX, nibbles)
        elif third_nibble == 0x6 and fourth_nibble == 0x5:
            print("0xFx65:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            return (OP.LD_XI, nibbles)
    return (None, None)

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
        print("Clear Display")
        screen = [0] * (64 * 32) 
        draw_screen()
    elif opcode == OP.RET:
        print("Return from subroutine.")
        pc = stack[sp]
        sp = sp - 1
    elif opcode == OP.JP: 
        instruction = args[-1]
        print("Jump to location", instruction & 0x0FFF)
        pc = instruction & 0x0FFF
    elif opcode == OP.CALL:
        print("Call subroutine")
        sp += 1
        stack[sp] = pc
        pc = instruction & 0x0FFF
    elif opcode == OP.SE:
        print("Skip next instruciton if Vx = kk")
        # vx = register[args[1]]
        vx = register[second_nibble]
        if vx == (instruction & 0x0FF): pc += 2
    elif opcode == OP.SNE:
        print("Skip next instruciton if Vx != kk")
        # vx = register[args[1]]
        vx = register[second_nibble]
        if vx != (instruction & 0x0FF): pc += 2
    elif opcode == OP.SE_XY:
        print("Skip next instruciton if Vx = Vy")
        # vx = register[args[1]]
        # vy = register[args[2]]
        vx = register[second_nibble]
        vy = register[third_nibble]
        if (vx == vy): pc += 2
    elif opcode == OP.LD:
        print("Set Vx = kk")
        # register[args[1]] = instruction & 0x0FF
        register[second_nibble] = instruction & 0x0FF
    elif opcode == OP.ADD:
        print("Set Vx = Vx + kk")
        # register[args[1]] = register[args[1]] + (instruction & 0x0FF)
        print("register[second_nibble] + (instruction & 0x0FF) ==", register[second_nibble] + (instruction & 0x0FF))
        register[second_nibble] = (register[second_nibble] + (instruction & 0x0FF)) 
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
        # if register[second_nibble] != register[third_nibble]: pc += 2
        if vx != vy: pc += 2
    elif opcode == OP.LD_IA:
        i_register = (0x0FFF & instruction)
        print("0xA", i_register)
    elif opcode == OP.JP_VA:
        pc = register[0] + (0x0FFF & instruction)
    elif opcode == OP.RND:
        # register[args[1]] = (random.randint(0, 255) & (instruction & 0x0FF))
        register[second_nibble] = (random.randint(0, 255) & (instruction & 0x0FF))
    elif opcode == OP.DRW: 
        Vx, Vy = register[second_nibble] % 64, register[third_nibble] % 32
        n = fourth_nibble
        sprite_data = [bin(int(data.hex() if data else b'0x00', base=16))[2:].zfill(8) for data in memory[i_register: i_register + n]]
        #sprite_data = [bin(data)[2:].zfill(8) for data in font[5:10]]
        #sprite_data = [bin(int(data.hex(), base=16))[2:].zfill(8) for data in font[i_register: i_register + n]]
        print("[DEBUG] n, Vx, Vy:", n, Vx, Vy)
        print("[DEBUG] sprite_data:", sprite_data)
        sprite = [list(map(int, row)) for row in sprite_data]
        # print("sprite", sprite)
        # sprite = [int(d, 2) for d in sprite_data] #new  
        print("[DEBUG] SPRITE",sprite)
        # #new
        # print("[DEBUG] bin", sprite)
        # print("[DEBUG] bin",[bin(x)[2:] for x in sprite])
        # sprite = [list(map(int, row)) for row in [bin(int(print(x), 2))[2:] for x in sprite]]
        # sprite = [list(map(int, row)) for row in [bin(x)[2:] for x in sprite]]
        if Vy >= 200: print("Hello Vy, ", Vy); exit(1)
        draw_sprite(Vx, Vy, sprite)
        draw_screen()
        # view_screen() # TODO: remove; for debugging
    elif opcode == OP.SKP:
        print("register[second_nibble]", register[second_nibble])
        print("register", register)
        key_pressed = keys[register[second_nibble] - 1]
        if key_pressed: pc += 2
    elif opcode == OP.SKNP:
        key_pressed = keys[register[second_nibble] - 1]
        if not key_pressed: pc += 2
    elif opcode == OP.LD_XDT:
        register[second_nibble] = delay_timer
    elif opcode == OP.LD_XKEY:
        pass
    elif opcode == OP.LD_DTX:
        delay_timer = register[second_nibble]
    elif opcode == OP.LD_STVX:
        sound_timer = register[second_nibble]
    elif opcode == OP.ADD_IX:
        print("[DEBUG] i_register", i_register)
        print("[DEBUG] register[second_nibble]", register[second_nibble])
        print("[DEBUG] register", register)
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
            print("memory[i_register + i]", memory[i_register + i])
            print("type: memory[i_register + i]", type(memory[i_register + i]))
            element = memory[i_register + i]
            register[i] = element if isinstance(element, int) else int.from_bytes(element, 'big')
        i_register = i_register + second_nibble + 1
    # else: raise NotImplementedError(f"Opcode {opcode} not implemented")
    # if 17 in register:
    #     print("opcode:",opcode)
    #     print("register:", register)
    #     exit(1)


with open("keypad-test.ch8", "rb") as f:
    # font_start = 200
    for char in font:
        memory[font_start] = chr(char)
        font_start += 1
    i = 512
    while (byte := f.read(1)):
        memory[i] = byte
        i += 1

ex_data = [1, 0, 0, 1, 1, 0, 0, 1]
ex_sprite = [[1, 1, 0, 1, 0, 0, 0, 1], [1, 0, 0, 1, 1, 0, 0, 1]]
R = [[1, 1, 1, 0, 0, 0, 0, 0], 
     [1, 0, 0, 1, 0, 0, 0, 0], 
     [1, 1, 1, 0, 0, 0, 0, 0], 
     [1, 0, 0, 1, 0, 0, 0, 0],
     [1, 0, 0, 1, 0, 0, 0, 0]]

def set_pixel(x, y, state):
    print("y", y)
    print("x", x)
    print("(y * 64) + x", (y * 64) + x)
    print("len screen:", len(screen))
    screen[(y * 64) + x] = state

def draw_row(start_x, start_y, row):
    for i, x in enumerate(row): 
        set_pixel(start_x + i, start_y, x)

def draw_row_n(start_x, start_y, n, row):
    for i in range(n):
        draw_row(start_x, start_y + i, row)

def draw_sprite(start_x, start_y, sprite):
    for i, row in enumerate(sprite):
        draw_row(start_x, start_y + i, row)

# set_pixel(0, 0, 1)
# set_pixel(63, 0, 1)
# set_pixel(0, 31, 1)

# draw_row(0, 0, ex_data)
# draw_row(0, 1, ex_data)

# draw_sprite(0, 0, ex_sprite)
# draw_sprite(0, 0, R)
# draw_sprite(15, 8, R)
ran = False
def step():
    global pc
    global ran
    # while pc < len(memory):
    #     instruction = memory[pc:pc+2]
    #     pc += 2
    #     # print(instuction)
    #     if instruction == [b'', b'']: break

    #     # current_instuction = b"".join(instuction).hex()
    #     # op_code, args = decode_instruction(current_instuction)
    #     # execute_instruction(op_code, args)

    #     processed_instruction = int.from_bytes(b"".join(instruction), byteorder='big')
    #     op_code, args = decode_instruction(processed_instruction)
    #     # print(instruction)
    #     # print(op_code, args)
    #     execute_instruction(op_code, args)
    #     if instruction == [b'\x12', b'(']: break
    #     # if instruction == [b'\x13', b'I']: break
    print("running step: ", pc)
    instruction = memory[pc:pc+2]
    pc += 2
    print("instruction:",instruction)
    # if instruction == [b'', b'']: break

    # current_instuction = b"".join(instuction).hex()
    # op_code, args = decode_instruction(current_instuction)
    # execute_instruction(op_code, args)

    processed_instruction = int.from_bytes(b"".join(instruction), byteorder='big')
    op_code, args = decode_instruction(processed_instruction)
    # print(instruction)
    # print(op_code, args)
    execute_instruction(op_code, args)
    # if instruction == [b'\x12', b'(']: break
    # if instruction == [b'\x13', b'I']: break
    if not ran: draw_screen(); ran = True
    # draw_screen()
    # decrease_time()
    # 16.67 ms ?
    # window.after(2, step)
    window.after(16, step)

def draw_screen():
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
# capture keyboard events
# deal with sound 

 # 16.67 ms ?
# window.after(2, step)     

window.after(16, decrease_time)       
window.after(16, step)    
window.bind("<Key>", lambda e: print("[KEYPRESS DEBUG]",e.keysym))        
window.mainloop()