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

class chip8:
	def __init__(self):
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

		self.stack = bytearray(16)
		for i in range(0, len(self.stack)):
			self.stack[i] = 0

		self.sp = 0 #stack pointer

		#load fontset

		#start with a black display
		self.display = np.array((64, 32), dtype=bool)
		self.display.fill(False)

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
		print("Opcode: " + str(hex(self.opcode)))

		#Step 2: Decode and Execute!
		cmd = self.opcode & 0xF000

		if cmd == 0xA000:	#ANNN: Sets I to the address NNN
			self.index = self.opcode & 0x0FFF #set index to NNN
			print("Updated index to " + str(hex(self.index)));
			self.pc += 2 #advance program counter by 2

		#Step 3: Update Timers!
		if self.delay_timer > 0:
			self.delay_timer -= 1

		if self.sound_timer > 0:
			printf("Beep!");
			self.sound_timer -= 1
