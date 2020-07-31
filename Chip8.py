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

Tk().withdraw() #Don't need a full TK GUI so close it

base_speed = 60
CPS = 60 #cycles per second
speed_mult_index = 0
speed_mults = [1, 2, 4, 8, 16, 32]
pygame.init()
clock = pygame.time.Clock()
cycle = 0
filename = "null" #filename of ROM

scale = 4
window = pygame.display.set_mode((64 * scale, 64 * scale))


title_img = pygame.image.load('assets/titlescreen.png')
title_img = pygame.transform.scale(title_img, (64 * scale, 32 * scale))

winicon_img = pygame.image.load('assets/windowicon.png')

pygame.display.set_caption("Chip'd")
pygame.display.set_icon(winicon_img)

selected_pallate = 0
pallates = [[(0,0,0), (255,255,255)],#white on black
			[(255,255,255), (0,0,0)],#black on white
			[(20,0,0), (255, 0, 0)],#red
			[(20,10,0), (255, 127, 0)],#orange
			[(20,20,0), (255, 255, 0)],#yellow
			[(0,20,0), (0, 255, 0)],#green
			[(0,15,20), (0, 200, 255)],#cyan
			[(0,0,20), (0, 0, 255)],#blue
			[(15,0,20), (200, 0, 255)]#purple
			]

black = pallates[selected_pallate][0]
white = pallates[selected_pallate][1]
grey = (45, 45, 45)



window.fill(black)

chip = cpu.chip8()

chose_rom = False


print("Done loading\n")

#buttons/ui
window.blit(title_img, (0, 0))
pygame.draw.rect(window, grey, (0, scale * 32, scale * 64, scale * 32)) #button background


btn_shade = pygame.Surface((12 * scale, 12 * scale))
btn_shade.set_alpha(128)
btn_shade.fill((0, 0, 0))

wide_btn_shade = pygame.Surface((27 * scale, 12 * scale))
wide_btn_shade.set_alpha(128)
wide_btn_shade.fill((0, 0, 0))

#open button
open_btn_img = pygame.image.load('assets/open_btn.png')
open_btn_img = pygame.transform.scale(open_btn_img, (12 * scale, 12 * scale))
open_btn = window.blit(open_btn_img, (scale * 3, scale * 34))

#pause button
pause_btn_img = pygame.image.load('assets/pause_btn.png')
play_btn_img = pygame.image.load('assets/play_btn.png')
pause_btn_img = pygame.transform.scale(pause_btn_img, (12 * scale, 12 * scale))
play_btn_img = pygame.transform.scale(play_btn_img, (12 * scale, 12 * scale))
pause_btn = window.blit(pause_btn_img, (scale * 18, scale * 34))

#reset button
reset_btn_img = pygame.image.load('assets/reset_btn.png')
reset_btn_img = pygame.transform.scale(reset_btn_img, (12 * scale, 12 * scale))
reset_btn = window.blit(reset_btn_img, (scale * 33, scale * 34))

#speed changer button
speed_btn_imgs = [pygame.image.load('assets/1x_btn.png'), pygame.image.load('assets/2x_btn.png'), pygame.image.load('assets/4x_btn.png'), pygame.image.load('assets/8x_btn.png'), pygame.image.load('assets/16x_btn.png'), pygame.image.load('assets/32x_btn.png')]
for i in range(0, len(speed_btn_imgs)):
	speed_btn_imgs[i] = pygame.transform.scale(speed_btn_imgs[i], (12 * scale, 12 * scale))
speed_btn_img = speed_btn_imgs[speed_mult_index]
speed_btn = window.blit(speed_btn_img, (scale * 48, scale * 34))

#save state button
save_btn_img = pygame.image.load('assets/save_btn.png')
save_btn_img = pygame.transform.scale(save_btn_img, (12 * scale, 12 * scale))
save_btn = window.blit(save_btn_img, (scale * 3, scale * 49))

#load state button
load_btn_img = pygame.image.load('assets/load_btn.png')
load_btn_img = pygame.transform.scale(load_btn_img, (12 * scale, 12 * scale))
load_btn = window.blit(load_btn_img, (scale * 18, scale * 49))

#color change button
color_btn_img = pygame.image.load('assets/color_btn.png')
color_btn_img = pygame.transform.scale(color_btn_img, (27 * scale, 12 * scale))
color_btn = window.blit(color_btn_img, (scale * 33, scale * 49))

pygame.display.update()

def draw_screen():
	screen = chip.get_screen()
	for xPos, x in enumerate(screen):
		for yPos, y in enumerate(x):
			if y == True:
				pygame.draw.rect(window, white, (yPos * scale, xPos * scale, scale, scale))
			else:
				pygame.draw.rect(window, black, (yPos * scale, xPos * scale, scale, scale))
	pygame.display.update()

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
				break

		if event.type == pygame.KEYUP:
			if event.key in chip.kbKeys:
				chip.release_key(chip.kbKeys.index(event.key))
				break

		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			pos = pygame.mouse.get_pos()
			if open_btn.collidepoint(pos):
				window.blit(btn_shade, (scale * 3, scale * 34))
				pygame.display.update()
				break
			if speed_btn.collidepoint(pos):
				window.blit(btn_shade, (scale * 48, scale * 34))
				pygame.display.update()
				break
			if pause_btn.collidepoint(pos):
				window.blit(btn_shade, (scale * 18, scale * 34))
				pygame.display.update()
				break
			if save_btn.collidepoint(pos):
				window.blit(btn_shade, (scale * 3, scale * 49))
				pygame.display.update()
				break
			if load_btn.collidepoint(pos):
				window.blit(btn_shade, (scale * 18, scale * 49))
				pygame.display.update()
				break
			if reset_btn.collidepoint(pos):
				window.blit(btn_shade, (scale * 33, scale * 34))
				pygame.display.update()
				break
			if reset_btn.collidepoint(pos):
				window.blit(wide_btn_shade, (scale * 33, scale * 49))
				pygame.display.update()
				break

		if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
			pos = pygame.mouse.get_pos()
			if open_btn.collidepoint(pos):
				open_btn = window.blit(open_btn_img, (scale * 3, scale * 34))
				pygame.display.update()
				filename = askopenfilename()
				chip.reset()
				chip.load_rom(filename)
				chose_rom = True
				break

			if speed_btn.collidepoint(pos):
				
				if speed_mult_index >= len(speed_mults) - 1:
					speed_mult_index = 0
					CPS = base_speed * speed_mults[speed_mult_index]
				else:
					speed_mult_index += 1
					CPS = base_speed * speed_mults[speed_mult_index]

				print(str(speed_mults[speed_mult_index]) + "x speed")

				speed_btn = window.blit(speed_btn_imgs[speed_mult_index], (scale * 48, scale * 34))
				pygame.display.update()
				break

			if color_btn.collidepoint(pos):
				
				if selected_pallate >= len(pallates) - 1:
					selected_pallate = 0
					black = pallates[selected_pallate][0]
					white = pallates[selected_pallate][1]
					
				else:
					selected_pallate += 1
					black = pallates[selected_pallate][0]
					white = pallates[selected_pallate][1]

				draw_screen()

				color_btn = window.blit(color_btn_img, (scale * 33, scale * 49))
				pygame.display.update()
				break

			if pause_btn.collidepoint(pos):
				chip.paused = not chip.paused

				if chip.paused:
					pause_btn = window.blit(play_btn_img, (scale * 18, scale * 34))
				else:
					pause_btn = window.blit(pause_btn_img, (scale * 18, scale * 34))
				pygame.display.update()
				break


			if save_btn.collidepoint(pos):
				chip.save_state(filename)
				save_btn = window.blit(save_btn_img, (scale * 3, scale * 49))
				break

			if load_btn.collidepoint(pos):
				chip.load_state(filename)
				load_btn = window.blit(load_btn_img, (scale * 18, scale * 49))


				#fixes the play/pause button
				if chip.paused:
					pause_btn = window.blit(play_btn_img, (scale * 18, scale * 34))
				else:
					pause_btn = window.blit(pause_btn_img, (scale * 18, scale * 34))
				pygame.display.update()

				break

			if reset_btn.collidepoint(pos):
				chip.reset(rom = filename)
				reset_btn = window.blit(reset_btn_img, (scale * 33, scale * 34))
				break

	#think

	if not chip.blocked and chose_rom and not chip.paused:
		#print("fps: " + str(clock.get_fps()))
		#print(str(cycle), end=" ")
		cycle += 1
		print("Cycle " + str(cycle))
		chip.emu_cycle()

		#render
		if chip.screen_update:
			draw_screen()
			chip.screen_update = False

	
