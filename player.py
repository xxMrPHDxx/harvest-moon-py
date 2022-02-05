import pygame
import re

class Player():
	def __init__(self, game, x=10, y=10):
		self.__game = game
		self.__pos = pygame.math.Vector2(x, y)
		self.__dir = pygame.math.Vector2()
		self.__speed = 3
		self.__lastdir = 'down'
	@property
	def status(self):
		if self.__dir.x != 0:
			return 'walk-left' if self.__dir.x < 0 else 'walk-right'
		if self.__dir.y != 0:
			return 'walk-up' if self.__dir.y < 0 else 'walk-down'
		return f'idle-{self.__lastdir}'
	@property
	def animation(self):
		return self.__game.assets.get_animation(self.status)
	def move(self, dx=None, dy=None):
		if dx in [-1,0,1]: self.__dir.x = dx
		if dy in [-1,0,1]: self.__dir.y = dy
	def update(self, dt):
		self.__pos += self.__dir * self.__speed

		# Movement
		if any([self.__game.keys[pygame.K_a], self.__game.keys[pygame.K_d]]):
			if self.__game.keys[pygame.K_a]: self.__dir.x = -1
			elif self.__game.keys[pygame.K_d]: self.__dir.x = 1
			self.__dir.y = 0
		else: self.__dir.x = 0
		if any([self.__game.keys[pygame.K_w], self.__game.keys[pygame.K_s]]):
			if self.__game.keys[pygame.K_w]: self.__dir.y = -1
			elif self.__game.keys[pygame.K_s]: self.__dir.y = 1
			self.__dir.x = 0
		else: self.__dir.y = 0

		self.animation.update(dt)
	def draw(self, game):
		self.__lastdir = re.search(r'(left|right|up|down)', self.status).groups()[0]
		game.screen.blit(self.animation.image, self.__pos)