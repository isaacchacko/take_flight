import pygame_template as template

game = template.Game((1000,1000), 'Explore', (50,50), ('grass','dirt'), 'map', 2, bg = 'sky')

while game.main:
	game.blit()
	game.mainloop()

pygame.quit()