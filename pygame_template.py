import pygame, sys, os

class Meter():
	def __init__(self, pos):
		self.max_amt = 100
		self.amt = 100
		self.border = pygame.Rect(pos[0], pos[1], 50, -200)
		self.meter = pygame.Rect(pos[0], pos[1], 50, -200)
		self.timer = 0
class Player():
	def __init__(self, image_folders):
		self.rect = pygame.Rect(175,-20,30,36)
		self.imgs = {}
		self.img_action = 'run' # corresponding to the folder
		self.face = 'R'
		self.action_time = 0
		self.vel = [0,0]
		self.max = [[-10,10],[-10,15]]
		self.max_air = [-20,20]
		self.grounded = False
		self.boosting = False
		self.boost_time = 100
		self.boost_meter = Meter((50,400))
		for image_folder in image_folders:
			with os.scandir(image_folder) as folder:
				imgs = []
				for file in folder:
					imgs.append(pygame.transform.scale(pygame.image.load(image_folder + '/' + file.name), (self.rect.width, self.rect.height)))
			self.imgs[image_folder] = imgs

	def physics(self, keys, terrain_hitboxes):
		# KEY PRESSES ----------------------------------
		if 'a' in keys:
			self.vel[0] -= 2
		if 'w' in keys and self.boost_time > 0:
			self.boosting = True
			self.grounded = False
			self.vel[1] -= 2
			self.boost_time -= 1
			if 'a' in keys or 'd' in keys:
				self.boost_time -= 1
		else:
			self.boosting = False
		if 'd' in keys:	
			self.vel[0] += 2

		# GRAVITY --------------------------------------
		if not self.grounded and not self.boosting:
			self.vel[1] += 2

		# X-ENTROPY ------------------------------------
		if self.vel[0] > 0:
			self.vel[0] -= 1
		if self.vel[0] < 0:
			self.vel[0] += 1

		# TERMINAL VEL -------------------------------
		for index, num in enumerate(self.vel):
			if not self.grounded and index == 0:
				if num < self.max_air[0]:
					self.vel[index] = self.max_air[0]
				if num > self.max_air[1]:
					self.vel[index] = self.max_air[1]
			else:
				if num < self.max[index][0]:
					self.vel[index] = self.max[index][0]
				if num > self.max[index][1]:
					self.vel[index] = self.max[index][1]


		# COLLISION ----------------------------------
		def find_collided_terrain(terrain_hitboxes): # function to return the specific terrain that the player collided with
			collided_terrain = []
			for terrain in terrain_hitboxes:
				if self.rect.colliderect(terrain):
					collided_terrain.append(terrain)
			return collided_terrain

		self.collisions = {'top':False, # reset the collisions
						  'bottom':False,
						  'left':False,
						  'right':False, 
						  'elevator':False}

		self.rect.x += self.vel[0] # move the player on the x-axis

		collided_terrain = find_collided_terrain(terrain_hitboxes) # pull the collided terrain
	
		for tile in collided_terrain:
			if self.vel[0] > 0:
				self.rect.right = tile.left
				self.collisions['right'] = True
			elif self.vel[0] < 0:
				self.rect.left = tile.right
				self.collisions['left'] = True

		self.rect.y += self.vel[1] # move the player on the y-axis

		collided_terrain = find_collided_terrain(terrain_hitboxes) # pull the collided terrain

		for tile in collided_terrain:
			if self.vel[1] > 0:
				self.rect.bottom = tile.top
				self.collisions['bottom'] = True
				self.grounded = True
				tmp = self.boost_time + 1
				self.boost_time = tmp if self.boost_time < 100 else self.boost_time
				self.vel[1] = 0
			elif self.vel[1] < 0:
				self.rect.top = tile.bottom
				self.collisions['top'] = True
		
		if not self.collisions['bottom']:
			self.grounded = False
class Game():
	def __init__(self, size, title, block_size, terrain_filenames, map_name, tick_speed, bg):
		pygame.init()
		self.win = Screen(size, title, block_size, terrain_filenames, map_name, bg)
		self.main = True
		self.tick = tick_speed
		self.size = size
		self.player = Player(['run', 'idle'])
		self.keys = []
		self.true_scroll = [0,0]
		self.scroll = [0,0]
	def mainloop(self):
		for event in pygame.event.get(): # event loop
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_d:
					self.keys.append('d')
				if event.key == pygame.K_a:
					self.keys.append('a')
				if event.key == pygame.K_w:
					self.keys.append('w')
			if event.type == pygame.KEYUP:	
				if event.key == pygame.K_d and 'd' in self.keys:
					self.keys.remove('d')
				if event.key == pygame.K_a and 'a' in self.keys:
					self.keys.remove('a')
				if event.key == pygame.K_w and 'w' in self.keys:
					self.keys.remove('w')

		pygame.display.update()
		# self.player.physics(self.keys, self.win.terrain_collision_rects)
		half_width = int(self.size[0] / 2)
		half_height = int(self.size[1] / 2)
		# self.true_scroll[0] += (self.player.rect.x-self.true_scroll[0]-half_width)/20
		self.true_scroll[0] += (self.player.rect.x-self.true_scroll[0] - half_width)/10
		self.true_scroll[1] += (self.player.rect.y-self.true_scroll[1]-half_height)/10
		self.scroll = self.true_scroll.copy()
		self.scroll[0] = int(self.scroll[0])
		self.scroll[1] = int(self.scroll[1])
		pygame.time.delay(self.tick)
	def blit(self):
		# blit bg
		self.win.actual.blit(self.win.bg, (0,0))

		# blit terrain
		self.win.terrain_collision_rects = []
		y = 0
		for row in self.win.map:
			x = 0
			for tile in row:
				if tile != '0':
					self.win.actual.blit(self.win.terrain.imgs[int(tile) - 1],(x*self.win.block_size[0] - self.scroll[0],y*self.win.block_size[1] - self.scroll[1]))
					self.win.terrain_collision_rects.append(pygame.Rect(x*self.win.block_size[0],y*self.win.block_size[1],self.win.block_size[0],self.win.block_size[1]))
				x += 1
			y += 1

		# blit player
		self.player.physics(self.keys, self.win.terrain_collision_rects)
		pygame.draw.rect(self.win.actual, (0,0,255), (self.player.rect.x - self.scroll[0], self.player.rect.y - self.scroll[1], self.player.rect.width, self.player.rect.height))
		# if self.player.img_action == 'run':
		# 	if self.player.face == 'R':
		# 		try:
		# 			self.win.actual.blit(self.player.imgs[self.player.img_action][self.player.action_time], (self.player.rect.x - self.scroll[0], self.player.rect.y - self.scroll[1]))
		# 		except IndexError:
		# 			self.player.action_time = 0
		# 			self.win.actual.blit(self.player.imgs[self.player.img_action][self.player.action_time], (self.player.rect.x - self.scroll[0], self.player.rect.y - self.scroll[1]))
		# 		self.player.action_time += 1
		# 	if self.player.face == 'L':
		# 		try:
		# 			self.win.actual.blit(pygame.transform.flip(self.player.imgs[self.player.img_action][self.player.action_time], True, False), (self.player.rect.x - self.scroll[0], self.player.rect.y - self.scroll[1]))
		# 		except IndexError:
		# 			self.player.action_time = 0
		# 			self.win.actual.blit(pygame.transform.flip(self.player.imgs[self.player.img_action][self.player.action_time], True, False), (self.player.rect.x - self.scroll[0], self.player.rect.y - self.scroll[1]))
		# 		self.player.action_time += 1
		# else:
		# 	try:
		# 		self.win.actual.blit(self.player.imgs[self.player.img_action][int(self.player.action_time/2)], (self.player.rect.x - self.scroll[0], self.player.rect.y - self.scroll[1]))
		# 	except IndexError:
		# 			self.player.action_time = 0
		# 			self.win.actual.blit(self.player.imgs[self.player.img_action][int(self.player.action_time/2)], (self.player.rect.x - self.scroll[0], self.player.rect.y - self.scroll[1]))
		# 	self.player.action_time += 1

		# draw meter
		if self.player.boost_time > 0:
			border_color = (0,0,0)
			self.player.boost_meter.timer = 0
		else:
			if self.player.boost_meter.timer < 6:
				border_color = (255,0,0) 
				self.player.boost_meter.timer += 1
			else:
				if self.player.boost_meter.timer < 12:
					border_color = (0,0,0) 
					self.player.boost_meter.timer += 1
				else:
					self.player.boost_meter.timer = 0
					border_color = (0,0,0)

		self.player.boost_meter.meter.height = self.player.boost_time * -2
		pygame.draw.rect(self.win.actual, (0,255,0), self.player.boost_meter.meter)
		pygame.draw.rect(self.win.actual, border_color, self.player.boost_meter.border, 5)
class Screen():
	def __init__(self, size, title, block_size, terrain_filenames, map_name, bg):
		self.width, self.height = size
		self.size = size
		self.actual = pygame.display.set_mode(self.size)
		pygame.display.set_caption(title)
		with open(map_name + '.txt', 'r') as f:
			f = f.read()
			f = f.split('\n')
			assert type(f) == list
			for line in f:
				line = line.split()
			self.map = f
		self.block_size = block_size
		self.terrain = Terrain(terrain_filenames)
		self.bg = pygame.image.load(bg + '.png')
	# def blit(self):	
	# 	# blit bg
	# 	self.actual.blit(self.bg, (0,0))

	# 	# blit terrain
	# 	self.terrain_collision_rects = []
	# 	y = 0
	# 	for row in self.map:
	# 		x = 0
	# 		for tile in row:
	# 			if tile != '0':
	# 				self.actual.blit(self.terrain.imgs[int(tile) - 1],(x*self.block_size[0],y*self.block_size[1]))
	# 				self.terrain_collision_rects.append(pygame.Rect(x*self.block_size[0],y*self.block_size[1],self.block_size[0],self.block_size[1]))
	# 			x += 1
	# 		y += 1

		
class Terrain():
	def __init__(self, filenames):
		self.imgs = []
		for name in filenames:
			self.imgs.append(pygame.image.load(name + '.png'))
		
class Animation():
	def __init__(self, filenames):
		self.imgs = []
		for name, time in filenames:
			for i in range(time):
				self.imgs.append(name)
