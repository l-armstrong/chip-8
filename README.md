# chip-8


CHIP-8 was created by developed by Joseph Weisbecker for the COSMAC VIP microcomputer.

deployed: 
- [tetris](https://larmstrong.itch.io/tetris)
- [pong](https://larmstrong.itch.io/pong)
- [breakout](https://larmstrong.itch.io/breakout)

dependencies: [pygame](https://pypi.org/project/pygame/)
```console
pip install pygame
```

usage
```console
python3 chip8.py <rom path>
```

My Key Mapping (QWERTY)          
| | | | |
|:--|:--|:--|:--|
|1	|2	|3	|4|
|q	|w	|e	|r|
|a	|s	|d	|f|
|z	|x	|c	|v|

RESTART game: <Enter>
Decrease Volume: <o>
Increase Volume: <p>


Virtual Machine Spec


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


CHIP-8 Key Mapping      My Key Mapping (QWERTY)          
| | | | |               | | | | |
|:--|:--|:--|:--|       |:--|:--|:--|:--|
|1	|2	|3	|C|         |1	|2	|3	|4|
|4	|5	|6	|D|         |q	|w	|e	|r|
|7	|8	|9	|E|         |a	|s	|d	|f|
|A	|0	|B	|F|         |z	|x	|c	|v|


Screen

64x32-pixel monochrome display.
Programs can also refer to sprites representing the hexadecimal digits 0-F.
The sprites are 5 bytes, or 8x5 pixels, which should be stored in the memory area of 0x000-0x1FF.


Instructions

CHIP-8 instructions are always 2 bytes long in big-endian order. The original CHIP-8 includes 35 opcodes.
See [Opcode Table](https://en.wikipedia.org/wiki/CHIP-8#Opcode_table).