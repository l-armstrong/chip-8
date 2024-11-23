"""
Chip-8 is a interpreted programming language. 
- takes up 512 bytes of memory
"""
from enum import Enum

max_memory = (1 << 12)
memory = [b''] * (max_memory)  # 4096 addresses 
                                # index regs and pc can only address 12 bits
pc = 512

class OP(Enum):
    SYS = 0  # SYS addr
    CLS = 1
    RET = 2
    JP  = 3

"""
return (OPCODE, [NONE | ....])
"""
def decode_instruction(instruction):
    if instruction.startswith("0"):
        if instruction.endswith("0"):
            return (OP.CLS, None) # Clear the display
        elif instruction.endswith("E"):
            return (OP.RET, None)
        else:
            return (OP.SYS, instruction[1:]) # nnn variable := instruction[1:]
    elif instruction.startswith("1"):
        return (OP.JP, instruction[1:])
    return (None, None)

def execute_instruction(opcode, args): 
    global pc
    if opcode == OP.CLS:
        print("Clear Display")
    elif opcode == OP.RET:
        print("Return from subroutine.")
    elif opcode == OP.JP: 
        old_pc = pc
        pc = int(args, 16)
        print("JUMP TO: ",pc)
        pc = old_pc

with open("IBM.ch8", "rb") as f:
    i = 512
    while (byte := f.read(1)):
        memory[i] = byte
        i += 1

while pc < len(memory):
    instuction = memory[pc:pc+2]
    pc += 2
    if instuction == [b'', b'']: break
    current_instuction = b"".join(instuction).hex()
    op_code, args = decode_instruction(current_instuction)
    execute_instruction(op_code, args)