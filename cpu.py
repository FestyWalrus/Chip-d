'''
	Chip8 CPU Core
	by Riley Knybel
	5/28/2020


	Memory map:
		0x000-0x1FF - Chip8 interpreter
		0x050-0x0A0 - Built in font (0-F)
		0x200-0xFFF - Program ROM and work RAM
'''

import numpy as np
import random
import pygame
import sys
import pickle #for save/load state

class chip8:
	def __init__(self):
		#0-F in numerical order, not how they appear on the keypad
		self.kbKeys = [pygame.K_x, pygame.K_1, pygame.K_2, pygame.K_3,
					pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_a,
					pygame.K_s, pygame.K_d, pygame.K_z, pygame.K_c,
					pygame.K_4, pygame.K_r, pygame.K_f, pygame.K_v]

		self.tone = pygame.mixer.Sound("assets/tone.wav")

		self.screen_update = False

		self.paused = False

		self.blocked = False #for 0xFX0A to wait for keypress
		self.keyRegister = -1

		self.opcode = bytearray(2)
		self.opcode[0] = 0x00	#initialized to 0
		self.opcode[1] = 0x00
		
		self.memory = bytearray(4096)
		for i in range(0, len(self.memory)):
			self.memory[i] = 0

		self.registers = bytearray(16)
		for i in range(0, len(self.registers)):
			self.registers[i] = 0

		self.delay_timer = 0
		self.sound_timer = 0
		self.index = 0
		self.pc = 0x200 #program counter

		self.stack = np.zeros(16, dtype='int')
		for i in range(0, 16):
			self.stack[i] = 0

		self.keys = np.zeros(16, dtype='bool')
		for i in range(0, 16):
			self.keys[i] = False

		self.sp = 0 #stack pointer

		#load fontset

		#start with a black display
		self.display = np.zeros((32, 64), dtype='bool')

		with open("assets/font", "rb") as font:
			byte = font.read(1)
			memIndex = 0x0

			while byte:
				self.memory[memIndex] = byte[0]
				memIndex += 1
				byte = font.read(1)

	def load_rom(self, filename):
		#fill up the memory

		with open(filename, "rb") as rom:
			byte = rom.read(1)
			memIndex = 0x200 #512

			while byte:
				self.memory[memIndex] = byte[0]
				memIndex += 1
				byte = rom.read(1)


	def emu_cycle(self):

		#Step 1: Fetch!
		self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1];
		#print("Opcode: " + str(hex(self.opcode)) + " PC: " + str(hex(self.pc)))

		#Step 2: Decode and Execute!

		decoding = True
		while decoding:
			#F000 Opcode mask
			cmd = self.opcode & 0xF000

			if cmd == 0x1000:	#1NNN: Jumps to address NNN
				self.pc = self.opcode & 0x0FFF #set program counter to NNN
				break

			if cmd == 0x2000:	#2NNN: calls subroutine at NNN
				self.stack[self.sp] = self.pc + 2 #store current address + 2 in stack
				self.sp += 1 #increment stack counter
				if self.sp > 15:
					print("E: The stack got smashed!")
					self.sp = 15
				self.pc = self.opcode & 0x0FFF #set program counter to NNN
				break

			if cmd == 0x3000:	#3XNN: skips next instruction if VX == NN
				if self.registers[(self.opcode & 0x0F00) // 0x100] == self.opcode & 0x00FF:
					self.pc += 4
				else:
					self.pc += 2
				break

			if cmd == 0x4000:	#0x4XNN: skips next instruction if VX != NN
				if self.registers[(self.opcode & 0x0F00) // 0x100] != self.opcode & 0x00FF:
					self.pc += 4
				else:
					self.pc += 2
				break

			if cmd == 0x6000:	#0x6XNN: Sets VX to NN
				self.registers[(self.opcode & 0x0F00) // 0x100] = self.opcode & 0x00FF
				self.pc += 2
				break

			if cmd == 0x7000:	#0x7XNN: Adds NN to VX (don't change carry flag)
				if (self.registers[(self.opcode & 0x0F00) // 0x100] + self.opcode & 0x00FF) > 255:
					self.registers[(self.opcode & 0x0F00) // 0x100] = (self.registers[(self.opcode & 0x0F00) // 0x100] + self.opcode & 0x00FF) - 256
				else:
					self.registers[(self.opcode & 0x0F00) // 0x100] = self.registers[(self.opcode & 0x0F00) // 0x100] + self.opcode & 0x00FF
				self.pc += 2
				break

			if cmd == 0xA000:	#ANNN: Sets index to the address NNN
				self.index = self.opcode & 0x0FFF #set index to NNN
				self.pc += 2 #advance program counter by 2
				break

			if cmd == 0xB000:	#BNNN: Jumps to NNN + V0
				self.pc = (self.opcode & 0x0FFF) + self.registers[0]
				break

			if cmd == 0xC000:	#CXNN: Set VX to random number AND NN
				self.registers[(self.opcode & 0x0F00) // 0x100] = (random.randint(0, 255) & (self.opcode & 0x00FF))
				self.pc += 2
				break

			if cmd == 0xD000:	#DXYN: Draw sprite on screen, read from index
				self.screen_update = True
				xPos = int(self.registers[(self.opcode & 0x0F00) // 0x100])
				yPos = int(self.registers[(self.opcode & 0x00F0) // 0x10])
				height = self.opcode & 0x000F
				self.registers[0xF] = 0

				byteOffset = 0

				for i in range(0, height):
					#print(str(hex(self.index + byteOffset)) + " " + hex(self.memory[self.index + byteOffset]))
					bitRow = self.bits(self.memory[self.index + byteOffset])
					
					
					for count, bit in enumerate(bitRow):

						if bit:
							if yPos + i > 31: #wrap around
								i -= 32 * ((yPos + i) // 32)
							if xPos + count > 63: #wrap around
								count -= 64 * ((xPos + count) // 64)
								
							if self.display[yPos + i][xPos + count] == True:
								self.registers[0xF] = 1
								
							self.display[yPos + i][xPos + count] = not self.display[yPos + i][xPos + count]
					byteOffset += 1

				self.pc += 2
				break

			#F00F Opcode mask
			cmd = self.opcode & 0xF00F

			if cmd == 0x5000:	#5XY0: Skips next instruction if VX == VY
				if self.registers[(self.opcode & 0x0F00) // 0x100] == self.registers[(self.opcode & 0x00F0) // 0x10]:
					self.pc += 4
				else:
					self.pc += 2
				break

			if cmd == 0x8000:	#8XY0: Sets VX to the value of VY
				self.registers[(self.opcode & 0x0F00) // 0x100] = self.registers[(self.opcode & 0x00F0) // 0x10]
				self.pc += 2
				break

			if cmd == 0x8001:	#8XY1: Sets VX to VX OR VY
				self.registers[(self.opcode & 0x0F00) // 0x100] = self.registers[(self.opcode & 0x0F00) // 0x100] | self.registers[(self.opcode & 0x00F0) // 0x10]
				self.pc += 2
				break

			if cmd == 0x8002:	#8XY2: Sets VX to VX AND VY
				self.registers[(self.opcode & 0x0F00) // 0x100] = self.registers[(self.opcode & 0x0F00) // 0x100] & self.registers[(self.opcode & 0x00F0) // 0x10]
				self.pc += 2
				break

			if cmd == 0x8003:	#8XY3: Sets VX to VX XOR VY
				self.registers[(self.opcode & 0x0F00) // 0x100] = self.registers[(self.opcode & 0x0F00) // 0x100] ^ self.registers[(self.opcode & 0x00F0) // 0x10]
				self.pc += 2
				break

			if cmd == 0x8004:	#8XY4: Adds VY to VX, sets VF (carry) if necessary
				if (self.registers[(self.opcode & 0x0F00) // 0x100] + self.registers[(self.opcode & 0x00F0) // 0x10]) > 255:
					self.registers[(self.opcode & 0x0F00) // 0x100] = (self.registers[(self.opcode & 0x0F00) // 0x100] + self.registers[(self.opcode & 0x00F0) // 0x10]) - 256
					self.registers[15] = 1
				else:
					self.registers[(self.opcode & 0x0F00) // 0x100] = self.registers[(self.opcode & 0x0F00) // 0x100] + self.registers[(self.opcode & 0x00F0) // 0x10]
				self.pc += 2
				break

			if cmd == 0x8005:	#8XY5: Subtracts VY from VX, sets VF if there's no borrow
				# https://github.com/JamesGriffin/CHIP-8-Emulator/blob/d1870538c009d3d76bd5d91319560edc58d16eae/src/chip8.cpp
				if self.registers[(self.opcode & 0x00F0) >> 4] > self.registers[(self.opcode & 0x0F00) >> 8]:
					self.registers[15] = 0 #there is a borrow
					self.registers[(self.opcode & 0x0F00) >> 8] = (self.registers[(self.opcode & 0x0F00) >> 8] - self.registers[(self.opcode & 0x00F0) >> 4]) + 256
				else:
					self.registers[15] = 1
					self.registers[(self.opcode & 0x0F00) >> 8] -= self.registers[(self.opcode & 0x00F0) >> 4]
				self.pc += 2
				break

			if cmd == 0x8006:	#8XY6: Stores LSB of VX in VF and shifts VX right by 1
				self.registers[15] = self.registers[(self.opcode & 0x0F00) // 0x100] & 0b1
				self.registers[(self.opcode & 0x0F00) // 0x100] = self.registers[(self.opcode & 0x0F00) // 0x100] >> 1
				self.pc += 2
				break

			if cmd == 0x8007:	#8XY7: Sets VX to VY-VX, VF 0 if borrow, 1 if no borrow
				# https://github.com/JamesGriffin/CHIP-8-Emulator/blob/d1870538c009d3d76bd5d91319560edc58d16eae/src/chip8.cpp
				if self.registers[(opcode & 0x0F00) >> 8] > self.registers[(opcode & 0x00F0) >> 4]:	# VY-VX
					self.registers[15] = 0 # there is a borrow
				else:
					self.registers[15] = 1
				self.registers[(opcode & 0x0F00) >> 8] = self.registers[(opcode & 0x00F0) >> 4] - self.registers[(opcode & 0x0F00) >> 8]
				self.pc += 2
				break

			if cmd == 0x800E:	#8XYE: Stores MSB of VX in VF and shifts VX left by 1
				self.registers[15] = (self.registers[(self.opcode & 0x0F00) // 0x100] & 0b1000000) >> 6
				self.registers[(self.opcode & 0x0F00) // 0x100] = (self.registers[(self.opcode & 0x0F00) // 0x100] << 1) & 255
				self.pc += 2
				break

			if cmd == 0x9000:	#9XY0: Skips next instruction if VX != VY
				if self.registers[(self.opcode & 0x0F00) // 0x100] != self.registers[(self.opcode & 0x00F0) // 0x10]:
					self.pc += 4
				else:
					self.pc += 2
				break

			#F0FF Opcode mask
			cmd = self.opcode & 0xF0FF

			if cmd == 0xE09E:	#EX9E: Skips next instruction if key in VX is pressed
				if self.keys[self.registers[(self.opcode & 0x0F00) // 0x100]]:
					self.pc += 4
				else:
					self.pc += 2
				break

			if cmd == 0xE0A1:	#EXA1: Skips next instruction if key in VX is not pressed
				if not self.keys[self.registers[(self.opcode & 0x0F00) // 0x100]]:
					self.pc += 4
				else:
					self.pc += 2
				break

			if cmd == 0xF007:	#FX07: Sets VX to value of delay timer
				self.registers[(self.opcode & 0x0F00) // 0x100] = self.delay_timer
				self.pc += 2
				break

			if cmd == 0xF00A:	#FX0A: Wait for keypress and store key in VX
				self.blocked = True
				self.keyRegister = (self.opcode & 0x0F00) // 0x100
				break

			if cmd == 0xF015:	#FX15: Sets delay timer to VX
				self.delay_timer = self.registers[(self.opcode & 0x0F00) // 0x100]
				self.pc += 2
				break

			if cmd == 0xF018:	#FX18: Sets sound timer to VX
				self.sound_timer = self.registers[(self.opcode & 0x0F00) // 0x100]
				self.pc += 2
				break

			if cmd == 0xF01E:	#FX1E: Adds VX to I without changing VF
				self.index += self.registers[(self.opcode & 0x0F00) // 0x100]
				self.pc += 2
				break

			if cmd == 0xF029:	#FX29: Sets I to the location of sprite for character in VX
				self.index = self.registers[(self.opcode & 0x0F00) // 0x100] * 5	#each character is 5 bytes tall
				self.pc += 2
				break

			if cmd == 0xF033:	#FX33: Stores binary-coded decimal of VX across 3 memory locations
				num = self.registers[(self.opcode & 0x0F00) // 0x100]
				num = str(num)

				while(len(num) < 3): #make sure that the number is 3 digits
					num = '0' + num

				self.memory[self.index] = int(num[0])
				self.memory[self.index + 1] = int(num[1])
				self.memory[self.index + 2] = int(num[2])

				self.pc += 2
				break

			if cmd == 0xF055:	#FX55: Stores V0 to VX inclusive in memory starting at I, don't change I
				for offset in range(0, ((self.opcode & 0x0F00) // 0x100) + 1):
					self.memory[self.index + offset] = self.registers[offset]
				self.pc += 2
				break

			if cmd == 0xF065:	#FX65: Loads V0 to VX inclusive from memory starting at I, don't change I
				for offset in range(0, ((self.opcode & 0x0F00) // 0x100) + 1):
					self.registers[offset] = self.memory[self.index + offset]
				self.pc += 2
				break

			#FFFF Opcode mask
			cmd = self.opcode & 0xFFFF

			if cmd == 0x00E0:	#00E0: Clears the display
				self.display = np.zeros((32, 64), dtype='bool')
				self.pc += 2
				break

			if cmd == 0x00EE:	#00EE: Returns from a subroutine
				self.sp -= 1
				self.pc = self.stack[self.sp]
				break

			print("Opcode not found: " + hex(self.opcode))

		#Step 3: Update Timers!
		if self.delay_timer > 0:
			self.delay_timer -= 1

		if self.sound_timer > 0:
			pygame.mixer.Sound.play(self.tone)
			self.sound_timer -= 1

	def get_screen(self):
		return self.display

	def bits(self, n):
		bitString = bin(n)[2:]
		bList = list()

		if len(bList) != 8:
			diff = 8 - len(bitString)
			for i in range(0, diff):
				bList.insert(0, False)

		for pos, c in enumerate(bitString):
			if c == '1':
				bList.append(True)
			else:
				bList.append(False)

		return bList

	def press_key(self, index):
		self.keys[index] = True

		if self.blocked:
			self.registers[self.keyRegister] = index
			self.keyRegister = -1
			self.blocked = False
			self.pc += 2

	def release_key(self, index):
		self.keys[index] = False

	def reset(self, rom = "null"):
		#reset opcode
		self.opcode = [0x00, 0x00]

		#wipe ram above 512 bytes
		for i in range(0x200, len(self.memory)):
			self.memory[i] = 0

		#clear registers
		for i in range(0, len(self.registers)):
			self.registers[i] = 0

		#reset these vars
		self.delay_timer = 0
		self.sound_timer = 0
		self.index = 0
		self.pc = 0x200 #program counter
		self.sp = 0 #stack pointer

		#clear the stack
		for i in range(0, 16):
			self.stack[i] = 0

		#clear the display
		self.display = np.zeros((32, 64), dtype='bool')
		self.screen_update = True

		self.blocked = False
		self.paused = False

		if rom != "null":
			#load the rom into memory
			with open(rom, "rb") as rom_file:
				byte = rom_file.read(1)
				memIndex = 0x200 #512

				while byte:
					self.memory[memIndex] = byte[0]
					memIndex += 1
					byte = rom_file.read(1)

	def save_state(self, filename):
		rom_name = slice(filename.rfind('/'), len(filename), 1)
		with open("savestates/" + filename[rom_name] + ".pickle", "wb") as f:
			pickle.dump([self.opcode, self.memory, self.registers, self.delay_timer, self.sound_timer, self.index, self.pc, self.sp, self.stack, self.display, self.screen_update, self.blocked, self.paused], f)

	def load_state(self, filename):
		rom_name = slice(filename.rfind('/'), len(filename), 1)
		try:
			with open("savestates" + filename[rom_name] + ".pickle", "rb") as f:
				self.opcode, self.memory, self.registers, self.delay_timer, self.sound_timer, self.index, self.pc, self.sp, self.stack, self.display, self.screen_update, self.blocked, self.paused = pickle.load(f)
		except:
			print("Save file does not exist!")