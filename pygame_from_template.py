import pygame_template as template

game = template.Game(size = (1000,1000),
					 title = 'Take Flight!',
					 block_size = (50,50),
					 terrain_filenames = ('grass', 'dirt'),
					 map_name = 'map',
					 tick_speed = 10,
					 bg = 'sky')

while game.main:
	game.blit()
	game.mainloop()

pygame.quit()