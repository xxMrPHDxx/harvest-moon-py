from . import _State

class Farm(_State):
	def __init__(self, sm):
		super().__init__(sm)
	@property
	def player(self): return self.__player
	def update(self, dt):
		pass
	def draw(self, game):
		game.assets.get_map('farm-winter').draw(game.screen)
