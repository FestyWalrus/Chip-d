'''
	Chip8 Emulator
	by Riley Knybel
	5/28/2020
'''

import cpu
import os
import sys
import time
import numpy as np
import pygame
from tkinter import Tk
from tkinter.filedialog import askopenfilename

Tk().withdraw() #Don't need a full GUI so close it

CPS = 500 #cycles per second
pygame.init()
clock = pygame.time.Clock()
cycle = 0

scale = 3
window = pygame.display.set_mode((64 * scale, 32 * scale))
pygame.display.set_caption("Chip-8")


black = (0, 0, 0)
white = (255, 255, 255)

chip = cpu.chip8()

chose_rom = False


print("Done loading\n")

while True:
	clock.tick(CPS)

	#get input
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit(0)

		if event.type == pygame.KEYDOWN:
			if event.key in chip.kbKeys:
				chip.press_key(chip.kbKeys.index(event.key))

		if event.type == pygame.KEYUP:
			if event.key in chip.kbKeys:
				chip.release_key(chip.kbKeys.index(event.key))

		if event.type == pygame.MOUSEBUTTONUP:
			if not chose_rom:
				filename = askopenfilename()
				chip.load_rom(filename)
				chose_rom = True


	#think

	if chose_rom:
		#print("fps: " + str(clock.get_fps()))
		#print(str(cycle), end=" ")
		cycle += 1
		chip.emu_cycle()

		#render
		if chip.screen_update:
			window.fill(black)
			screen = chip.get_screen()
			for xPos, x in enumerate(screen):
				for yPos, y in enumerate(x):
					if y == True:
						pygame.draw.rect(window, white, (yPos * scale, xPos * scale, scale, scale))
			pygame.display.update()
			chip.screen_update = False

	
