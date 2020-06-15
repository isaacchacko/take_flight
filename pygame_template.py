import pygame, os, sys, random

class Enemy():
	def __init__(self, rect, damage = None):
		self.rect = pygame.Rect(rect)
		if damage != None:
			self.dmg = damage
		else:
			self.dmg = 1
class Particle():
	def __init__(self, color, rect):
		self.rect = pygame.Rect(rect)
		self.alive = True
		self.color = color
		self.lifetime = 0
		self.vel = [0,1]
	def moveToAir(self, terrain_hitboxes):
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

		collided_terrain = find_collided_terrain(terrain_hitboxes) # pull the collided terrain
	
		for tile in collided_terrain:
			if self.vel[0] > 0:
				self.rect.right = tile.left
				self.collisions['right'] = True
			elif self.vel[0] < 0:
				self.rect.left = tile.right
				self.collisions['left'] = True
			if self.vel[1] > 0:
				self.rect.bottom = tile.top
				self.collisions['bottom'] = True
				self.vel[1] = 0
			elif self.vel[1] < 0:
				self.rect.top = tile.bottom
				self.collisions['top'] = True	

class StatusBar():
	def __init__(self):
		self.img = pygame.image.load('status_bar.png')
		self.img = pygame.transform.scale(self.img, (280, 100))

class Meter():
	def __init__(self, pos, flashing_color = (255,0,0), normal_color = (0,0,0), actual_meter_color = (0,255,0)):
		self.border = pygame.Rect(pos[0], pos[1], 200, 25)
		self.meter = pygame.Rect(pos[0], pos[1], 200, 25)
		self.flashing_timer = 0
		self.flashing_color = flashing_color
		self.normal_color = normal_color
		self.meter_color = actual_meter_color
		self.border_color = (0,0,0)
		self.threshold_reached = False
		self.max = 200
	def set_border_color(self, trackedVar, threshold, lowerHigher):
		# THRESHOLD CHECK
		if lowerHigher == 'higher':
			if trackedVar > threshold:
				self.border_color = self.normal_color
				self.flashing_timer = 0
				self.threshold_reached = False
			else: # once threshold has been reached
				self.threshold_reached = True
		else:
			if trackedVar < threshold:
				self.border_color = self.normal_color
				self.flashing_timer = 0
				self.threshold_reached = False
			else: # once threshold has been reached
				self.threshold_reached = True

		# FLASHING
		if self.threshold_reached:
			if self.flashing_timer < 6: # flashing cycle
				self.border_color = self.flashing_color
				self.flashing_timer += 1
			else:
				if self.flashing_timer < 12: # normal cycle
					self.border_color = self.normal_color
					self.flashing_timer += 1
				else:
					self.flashing_timer = 0
					self.border_color = self.normal_color
		
class Action():
	def __init__(self):
		pass

class Player():
	def __init__(self):
		self.rect = pygame.Rect(175,-20,30,36)
		self.vel = [0,0]
		self.abs_loc = 'air'
		self.max = {'air': [[-20,20],[-10,30]], 'ground': [[-10,10],[-10,30]]}

		self.boost = Action()
		self.boost.glyph = pygame.transform.scale(pygame.image.load('wind_glyph.png'), (30,30))
		self.boost.ing = False
		self.boost.charge = 100
		self.boost.charge_rate = 4
		self.boost.meter = Meter((60,45))
		self.boost.particles = []
		self.boost.particle_colors = [(194, 194, 194), (209, 209, 209), (143, 143, 143)]

		self.health = Action()
		self.health.glyph = pygame.transform.scale(pygame.image.load('heart_glyph.png'), (30,30))
		self.health.max = 10
		self.health.now = 10
		self.health.meter = Meter((60, 10), actual_meter_color = (217, 82, 82))
	def createBoostParticle(self, keys):
		top = None
		if 'w' in keys and len(keys) == 1:
			top = self.rect.bottom
			bottom = self.rect.bottom + 50
			left = self.rect.left - 10
			right = self.rect.right
		if 'w' in keys and 'a' in keys and len(keys) == 2:
			top = self.rect.bottom
			bottom = self.rect.bottom + 50
			left = self.rect.left - self.rect.width - 10
			right = self.rect.left
		if 'w' in keys and 'd' in keys and len(keys) == 2:
			top = self.rect.bottom
			bottom = self.rect.bottom + 50
			left = self.rect.right - 10
			right = self.rect.right + self.rect.width
		widthheight = random.randint(5,30)

		if top != None:
			self.boost.particles.append(Particle(random.choice(self.boost.particle_colors),
					     						 (random.randint(left, right),
												 random.randint(top, bottom),
												 widthheight,
												 widthheight)))

	def physics(self, keys, terrain_hitboxes):
		if self.boost.ing and len(self.boost.particles) < 40:
			self.createBoostParticle(keys)
		for particle in self.boost.particles:
			particle.moveToAir(terrain_hitboxes)
			particle.lifetime += 1
			if particle.lifetime > 10:
				particle.alive = False
				self.boost.particles.remove(particle)
		# KEY PRESSES ----------------------------------
		if 'a' in keys:
			self.vel[0] -= 2
		if 'w' in keys and self.boost.charge > 0:
			self.boost.ing = True
			self.vel[1] -= 2
			self.boost.charge -= 1
			if 'a' in keys or 'd' in keys:
				self.boost.charge -= 1
		else:
			self.boost.ing = False
		if 'd' in keys:	
			self.vel[0] += 2

		# GRAVITY --------------------------------------
		if self.abs_loc != 'ground' and not self.boost.ing:
			self.vel[1] += 2

		# X-ENTROPY ------------------------------------
		if self.vel[0] > 0:
			self.vel[0] -= 1
		if self.vel[0] < 0:
			self.vel[0] += 1

		# TERMINAL VEL -------------------------------
		for index, num in enumerate(self.vel):
			if num < self.max[self.abs_loc][index][0]:
					self.vel[index] = self.max[self.abs_loc][index][0]
			if num > self.max[self.abs_loc][index][1]:
				self.vel[index] = self.max[self.abs_loc][index][1]


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
				self.vel[1] = 0
			elif self.vel[1] < 0:
				self.rect.top = tile.bottom
				self.collisions['top'] = True
		
		if self.collisions['bottom']:
			self.abs_loc = 'ground'
			tmp = self.boost.charge + self.boost.charge_rate
			self.boost.charge = tmp if self.boost.charge < 100 else self.boost.charge
		else:
			self.abs_loc = 'air'

class Game():
	def __init__(self, size = (1000,1000),
					   title = 'Unnamed Platformer',
					   block_size = (50,50),
					   terrain_filenames = ('grass'),
					   map_name = 'map',
					   tick_speed = 10,
					   bg = 'sky'):
		pygame.init()
		self.win = Screen(size, title, block_size, terrain_filenames, map_name, bg)
		self.status_bar = StatusBar()
		self.main = True
		self.tick = tick_speed
		self.size = size
		self.player = Player()
		self.keys = []
		self.true_scroll = [0,0]
		self.scroll = [0,0]
	def mainloop(self):
		print(f'Health Bar Width: ({self.player.health.meter.meter.width}) because {self.player.health.now} * 20 is {self.player.health.meter.meter.width}')
	
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

		# SCROLL ----------------------------------------------------
		half_width = int(self.size[0] / 2)
		half_height = int(self.size[1] / 2)
		self.true_scroll[0] += (self.player.rect.x-self.true_scroll[0] - half_width)/10
		self.true_scroll[1] += (self.player.rect.y-self.true_scroll[1]-half_height)/10
		self.scroll = self.true_scroll.copy()
		self.scroll[0] = int(self.scroll[0])
		self.scroll[1] = int(self.scroll[1])

		# GENERAL --------------------------------------------------
		pygame.display.update()
		pygame.time.delay(self.tick)

	def blit(self):
		# BG ---------------------------------------------------------
		self.win.actual.blit(self.win.bg, (0,0))

		# TERRAIN ----------------------------------------------------
		self.win.terrain_collision_rects = []
		y = 0
		for row in self.win.map:
			x = 0
			for tile in row:
				if tile != '0':
					self.win.actual.blit(self.win.terrain.imgs[int(tile) - 1], # image
										(x*self.win.block_size[0] - self.scroll[0],  # coords, x
										 y*self.win.block_size[1] - self.scroll[1])) # y
					self.win.terrain_collision_rects.append(pygame.Rect(x*self.win.block_size[0], # x
																		y*self.win.block_size[1], # y
																		self.win.block_size[0], # width
																		self.win.block_size[1])) # height
				x += 1 # increase x and y each row/column
			y += 1

		# PLAYER -------------------------------------------------------
		self.player.physics(self.keys, self.win.terrain_collision_rects)
		pygame.draw.rect(self.win.actual, # draw location
						 (0,0,255), # color (blue)
						 (self.player.rect.x - self.scroll[0], # rect, x
						  self.player.rect.y - self.scroll[1], # y
						  self.player.rect.width, # width
						  self.player.rect.height)) # height

		# BOOST PARTICLES ----------------------------------------------
		for particle in self.player.boost.particles:
			pygame.draw.ellipse(self.win.actual, particle.color, (particle.rect.x - self.scroll[0], particle.rect.y - self.scroll[1], particle.rect.width, particle.rect.height))

		# STATUS BAR
		self.win.actual.blit(self.status_bar.img, (0,0))

		# BOOST METER --------------------------------------------------------
		self.win.actual.blit(self.player.boost.glyph,(15,41))
		self.player.boost.meter.set_border_color(trackedVar = self.player.boost.charge, threshold = 0, lowerHigher = 'higher')
		self.player.boost.meter.meter.width = self.player.boost.charge * 2
		self.player.boost.meter.meter.width = self.player.boost.meter.max if self.player.boost.meter.meter.width > self.player.boost.meter.max else self.player.boost.meter.meter.width
		pygame.draw.rect(self.win.actual, self.player.boost.meter.meter_color, self.player.boost.meter.meter)
		pygame.draw.rect(self.win.actual, self.player.boost.meter.border_color, self.player.boost.meter.border, 5)

		# HEALTH METER --------------------------------------------------------
		self.win.actual.blit(self.player.health.glyph,(15,6))
		self.player.health.meter.set_border_color(trackedVar = self.player.health.now, threshold = 2, lowerHigher = 'higher')
		self.player.health.meter.meter.width = self.player.health.now * 20
		self.player.health.meter.meter.width = self.player.health.meter.max if self.player.health.meter.meter.width > self.player.health.meter.max else self.player.health.meter.meter.width
		pygame.draw.rect(self.win.actual, self.player.health.meter.meter_color, self.player.health.meter.meter)
		pygame.draw.rect(self.win.actual, self.player.health.meter.border_color, self.player.health.meter.border, 5)

class Terrain():
	def __init__(self, filenames):
		self.imgs = []
		for name in filenames:
			self.imgs.append(pygame.image.load(name + '.png'))

class Screen():
	def __init__(self, size, title, block_size, terrain_filenames, map_name, bg):
		self.width, self.width = size
		self.size = size
		self.actual = pygame.display.set_mode(self.size)
		pygame.display.set_caption(title)
		with open(map_name + '.txt', 'r') as f:
			f = f.read()
			f = f.split('\n')
			for line in f:
				line = line.split()
			self.map = f
		self.block_size = block_size
		self.terrain = Terrain(terrain_filenames)
		self.bg = pygame.image.load(bg + '.png')
		