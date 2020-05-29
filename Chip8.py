'''
	Chip8 Emulator
	by Riley Knybel
	5/28/2020
'''

import cpu
#import pygame

chip = cpu.chip8()

chip.load_rom("test")

print("Done loading\nExecuting one cycle")

chip.emu_cycle()
