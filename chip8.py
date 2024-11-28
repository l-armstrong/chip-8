"""
Chip-8 is a interpreted programming language. 
- takes up 512 bytes of memory
"""
from enum import Enum

max_memory = (1 << 12)
memory = [b''] * (max_memory)  # 4096 addresses 
                                # index regs and pc can only address 12 bits
stack = [0]*16
sp = -1 # Possible change to 0?
pc = 512
register = [0]*16 # Vx where x is a hexadecimal digit
VF = 0 # Flag register?

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

# """
# return (OPCODE, [NONE | ....])
# """
# def decode_instruction(instruction: str):
#     if instruction.startswith("0"):
#         if instruction.endswith("0"):
#             return (OP.CLS, None) # Clear the display
#         elif instruction.endswith("E"):
#             return (OP.RET, None)
#         else:
#             return (OP.SYS, instruction[1:]) # nnn variable := instruction[1:]
#     elif instruction.startswith("1"):
#         return (OP.JP, instruction[1:])
#     elif instruction.startswith("2"):
#         return (OP.CALL, instruction[1:])
#     elif instruction.startswith("3"):
#         return (OP.SE, instruction[1:])
#     elif instruction.startswith("4"):
#         return (OP.SNE, instruction[1:])
#     elif instruction.startswith("5"):
#         return (OP.SE_XY, instruction[1:])
#     elif instruction.startswith("6"):
#         return (OP.LD, instruction[1:])
#     elif instruction.startswith("7"): 
#         return (OP.ADD, instruction[1:])
#     elif instruction.startswith("8"):
#         print(instruction)
#     return (None, None)

# def execute_instruction(opcode, args): 
#     global pc
#     global stack
#     if opcode == OP.CLS:
#         print("Clear Display")
#     elif opcode == OP.RET:
#         print("Return from subroutine.")
#     elif opcode == OP.JP: 
#         old_pc = pc
#         pc = int(args, 16)
#         print("JUMP TO: ",pc)
#         pc = old_pc # TODO: delete
#     elif opcode == OP.CALL:
#         sp += 1
#         print('set sp to ',sp)
#         stack = pc
#         pc = args
#         print('set pc to ', args)
#         pc = old_pc # TODO: delete
#     elif opcode == OP.SE:
#         x, kk = args[0], args[1:]
#         if register[int(x, 16)] == int(kk, 16):
#             old_pc = pc
#             pc += 2
#             print('OP-SE: incrementing to', pc)
#             pc = old_pc # TODO: delete
#     elif op_code == OP.SNE:
#         x, kk = args[0], args[1:]
#         if register[int(x, 16)] != int(kk, 16):
#             old_pc = pc
#             pc += 2
#             print('OP-SNE: incrementing to', pc)
#             pc = old_pc # TODO: delete
#     elif op_code == OP.SE_XY:
#         print("SE XY, args: ", args)
#         # TODO: compack to implement
#     elif op_code == OP.LD:
#         x, kk = args[0], args[1:]
#         register[int(x, 16)] = int(kk, 16)
#     elif op_code == OP.ADD:
#         x, k = int(args[0], 16), int(args[1:], 16)
#         register[x] += k
    
"""
return (OPCODE, [NONE | ....])
"""
def decode_instruction(instruction):
    global VF
    first_nibble = (0xF000 & instruction) >> 12
    second_nibble = (0x0F00 & instruction) >> 8
    third_nibble = (0x00F0 & instruction) >> 4
    fourth_nibble = (0x000F & instruction) 
    nibbles = (first_nibble, second_nibble, third_nibble, fourth_nibble)
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
            register[second_nibble] = register[third_nibble]
        elif fourth_nibble == 0x1:
            print("0x8_1:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            register[second_nibble] = register[second_nibble] | register[third_nibble]
        elif fourth_nibble == 0x2:
            print("0x8_2:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            register[second_nibble] = register[second_nibble] & register[third_nibble]     
        elif fourth_nibble == 0x3:
            print("0x8_3:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            register[second_nibble] = register[second_nibble] ^ register[third_nibble]  
        elif fourth_nibble == 0x4:
            print("0x8_4:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            vx, vy = register[second_nibble], register[third_nibble]
            _sum = vx + vy
            if (_sum > 255): VF = 1
            else: VF = 0
            register[second_nibble] = 0x0FF & _sum # only lowest 8 bits (1 byte) are kept
        elif fourth_nibble == 0x5:
            print("0x8_5:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            vx, vy = register[second_nibble], register[third_nibble]
            difference = vx - vy
            if (vx > vy): VF = 1
            else: VF = 0
            register[second_nibble] = difference
        elif fourth_nibble == 0x6:
            print("0x8_6:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            if (second_nibble & 0x01): VF = 1
            else: VF = 0
            register[second_nibble] = register[second_nibble] >> 1
        elif fourth_nibble == 0x7:
            print("0x8_7:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            vx, vy = register[second_nibble], register[third_nibble]
            difference = vy - vx
            if (vy > vx): VF = 1
            else: VF = 0
            register[second_nibble] = difference
        elif fourth_nibble == 0xE:
            print("0x8_E:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
            if (second_nibble & 0x01): VF = 1
            else: VF = 0
            register[second_nibble] = register[second_nibble] << 1
    elif first_nibble == 0x9:
        print("0x9:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.SNE_XY, nibbles)
        if register[second_nibble] != register[third_nibble]: pc += 2
    elif first_nibble == 0xA:
        print("0xA:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.LD_IA, nibbles)
    elif first_nibble == 0xB:
        print("0xB:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.JP_VA, nibbles)
    elif first_nibble == 0xC:
        print("0xC:", first_nibble, second_nibble, third_nibble, fourth_nibble, instruction)
        return (OP.RND, nibbles)
    return (None, None)

def execute_instruction(opcode, args): 
    global pc
    global stack
    if opcode == OP.CLS:
        print("Clear Display")
    elif opcode == OP.RET:
        print("Return from subroutine.")
    elif opcode == OP.JP: 
        old_pc = pc
        pc = int(args, 16)
        print("JUMP TO: ",pc)
        pc = old_pc # TODO: delete
    elif opcode == OP.CALL:
        sp += 1
        print('set sp to ',sp)
        stack = pc
        pc = args
        print('set pc to ', args)
        pc = old_pc # TODO: delete
    elif opcode == OP.SE:
        x, kk = args[0], args[1:]
        if register[int(x, 16)] == int(kk, 16):
            old_pc = pc
            pc += 2
            print('OP-SE: incrementing to', pc)
            pc = old_pc # TODO: delete
    elif opcode == OP.SNE:
        x, kk = args[0], args[1:]
        if register[int(x, 16)] != int(kk, 16):
            old_pc = pc
            pc += 2
            print('OP-SNE: incrementing to', pc)
            pc = old_pc # TODO: delete
    elif opcode == OP.SE_XY:
        print("SE XY, args: ", args)
        # TODO: compack to implement
    elif opcode == OP.LD:
        x, kk = args[0], args[1:]
        register[int(x, 16)] = int(kk, 16)
    elif opcode == OP.ADD:
        x, k = int(args[0], 16), int(args[1:], 16)
        register[x] += k

with open("IBM.ch8", "rb") as f:
    i = 512
    while (byte := f.read(1)):
        memory[i] = byte
        i += 1

while pc < len(memory):
    instuction = memory[pc:pc+2]
    pc += 2
    # print(instuction)
    if instuction == [b'', b'']: break

    # current_instuction = b"".join(instuction).hex()
    # op_code, args = decode_instruction(current_instuction)
    # execute_instruction(op_code, args)

    processed_instruction = int.from_bytes(b"".join(instuction), byteorder='big')
    op_code, args = decode_instruction(processed_instruction)
    # print(op_code, args)
    # execute_instruction(op_code, args)