import pygame
from states import StateManager, Farm
from assets import AssetManager
from player import Player

class Game:
	def __init__(self, fps=30, title='Untitled'):
		pygame.init()
		self.__fps = fps
		self.__width, self.__height, self.__scale = 640, 480, 2
		self.__screen = pygame.Surface(
			(self.__width//self.__scale, self.__height//self.__scale)
		)
		self.__display = pygame.display.set_mode((self.__width, self.__height))
		pygame.display.set_caption(title)

		self.__running = False

		# Keyboards
		self.__keys = [False for i in range(256)]

		# Loading assets
		assets = AssetManager()
		assets.load_spritesheets('./data/sheets')
		assets.load_maps('./data/tiles')
		self.__assets = assets

		# Creating player
		self.__player = Player(self)

		# Creating state manager and set initial state
		self.__sm = StateManager(self)
		self.__sm.push(Farm)

		# pygame.display.toggle_fullscreen()
	@property
	def width(self): return self.__width
	@property
	def height(self): return self.__height
	@property
	def scale(self): return self.__scale
	@property
	def screen(self): return self.__screen
	@property
	def keys(self): return self.__keys
	@property
	def assets(self): return self.__assets
	@property
	def player(self): return self.__player
	def start(self):
		if self.__running: return
		self.__running = True
		fps_clock = pygame.time.Clock()
		dt_clock = pygame.time.Clock()

		BLACK = pygame.Color(0, 0, 0)

		while self.__running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					self.__running = False
					return
				if event.type == pygame.KEYUP:
					self.__keys[event.key] = False
					self.__sm.keyup(event.key)
					if event.key in [pygame.K_a, pygame.K_d]:
						self.player.move(dx=0)
					if event.key in [pygame.K_w, pygame.K_s]:
						self.player.move(dy=0)
				if event.type == pygame.KEYDOWN:
					self.__keys[event.key] = True
					self.__sm.keydown(event.key)

			# Clears the screen (Temporary)
			self.__screen.fill(BLACK)

			# Updating
			dt = dt_clock.tick(0)
			self.__sm.update(dt)
			self.player.update(dt)

			# Drawing
			self.__sm.draw(self)
			self.player.draw(self)
			
			# Blitting to display with a scale
			self.__display.blit(
				pygame.transform.scale(self.__screen, (self.width, self.height)), 
				dest=(0, 0)
			)

			# Update the display and simulate ticking
			pygame.display.update()
			fps_clock.tick(self.__fps)

if __name__ == '__main__':
	game = Game()
	game.start()