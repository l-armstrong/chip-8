# chip-8


CHIP-8 was created by developed by Joseph Weisbecker for the COSMAC VIP microcomputer.

dependencies; [pygame](https://pypi.org/project/pygame/)
```console
pip install pygame
```

usage
```console
python3 chip8.py <rom path>
```

Virtual Machine Spec

Registers

|Register| Size|Description|
|:-------|:-------|:-------|
|V[16]	|byte|	|General purpose|
|I	|short	|General purpose|
|PC	|short	|Program counter|
|SP	|byte	|Stack pointer|
|DT	|byte	|Delay timer|
|ST	|byte	|Sound timer|
