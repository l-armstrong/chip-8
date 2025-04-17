# Chip-8 Emulator


The [CHIP-8](https://en.wikipedia.org/wiki/CHIP-8) emulator/vm/interpreter was created by developed by Joseph Weisbecker for the COSMAC VIP microcomputer. The emulator is designed to run simple video games on early microcomputers. With a relatively small [instruction set](https://en.wikipedia.org/wiki/Instruction_set_architecture), the emulator is easy to understand, and a complete joy to implement. 

Games available to play in the browser using this emulator: 
- [tetris](https://larmstrong.itch.io/tetris)
- [pong](https://larmstrong.itch.io/pong)
- [breakout](https://larmstrong.itch.io/breakout)


## Table of Contents
- [Dependencies](#Dependencies)
- [Usage](#Usage)
- [Key Mapping](#KeyMapping)
- [Virtual Machine Spec](#Spec)
- [Credits](#Credits)
- [License](#License)


## Dependencies
dependencies: [pygame](https://pypi.org/project/pygame/)
```console
pip install pygame
```

## Usage
```console
python3 chip8.py <rom path>
```

## Key Mapping 

| | | | |
|:--|:--|:--|:--|
|1	|2	|3	|4|
|q	|w	|e	|r|
|a	|s	|d	|f|
|z	|x	|c	|v|

Restart Game: ENTER  
Decrease Volume: O 
Increase Volume: P  


## Virtual Machine Spec

Memory  

CHIP-8 can address up to 4KB(4096 bytes) of RAM from location 0x000 to 0xFFF.

The first 512 bytes, 0x000-0x1FF, should not be used by programs.


Registers  

|Register| Size|Description|
|:-------|:-------|:-------|
|V[16]	|byte|	|General purpose|
|I	|short	|General purpose|
|PC	|short	|Program counter|
|SP	|byte	|Stack pointer|
|DT	|byte	|Delay timer|
|ST	|byte	|Sound timer|


CHIP-8 Key Mapping              
| | | | |               
|:--|:--|:--|:--|      
|1	|2	|3	|C|      
|4	|5	|6	|D|        
|7	|8	|9	|E|         
|A	|0	|B	|F|         


Screen  

64x32-pixel monochrome display.
Programs can also refer to sprites representing the hexadecimal digits 0-F.
The sprites are 5 bytes, or 8x5 pixels, which should be stored in the memory area of 0x000-0x1FF.


Instructions  

CHIP-8 instructions are always 2 bytes long in big-endian order. The original CHIP-8 includes 35 opcodes.
See [Opcode Table](https://en.wikipedia.org/wiki/CHIP-8#Opcode_table).


## Credits
This project would not have have been possible without the following resource: 
- [Cowgod's Chip-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM)

