from os import walk
import pygame
import json

class Animation():
	def __init__(self, speed):
		self.__speed = speed
		self.__timer = 0
		self.__frames = []
		self.__index = 0
	@property
	def length(self): return len(self.__frames)
	@property
	def image(self):
		return None if self.length == 0 else self.__frames[self.__index]
	def add_frame(self, frame):
		self.__frames.append(frame)
	def update(self, dt):
		if len(self.__frames) <= 1: return
		self.__timer += self.__speed
		if self.__timer >= 1:
			self.__index = (self.__index + 1) % self.length
			self.__timer = 0

class Tile():
	def __init__(self, image, solid):
		self.__image = image
		self.__solid = solid
	def collides(self, other):
		if not self.__solid: return False
		pass # TODO: Fix later
	def draw(self, screen, x, y):
		screen.blit(self.__image, dest=(x, y))

class TileSet():
	def __init__(self):
		self.__tiles = []
	def __getitem__(self, idx):
		return self.__tiles[idx]
	def add_tile(self, tile):
		if not isinstance(tile, Tile): return
		self.__tiles.append(tile)

class TileMap():
	def __init__(self, tiles, _map):
		self.__tiles = tiles
		self.__map = _map
	def draw(self, screen):
		for row, cols in enumerate(self.__map):
			for col, tile in enumerate(cols):
				tile = self.__tiles[tile]
				tile.draw(screen, col*16, row*16)

class AssetManager():
	def __init__(self):
		self.__frames = {}
		self.__animations = {}
		self.__maps = {}
	def get_image(self, key):
		if key in self.__frames: return self.__frames[key]
	def get_animation(self, key):
		if key in self.__animations: return self.__animations[key]
	def get_map(self, key):
		if key in self.__maps: return self.__maps[key]
	def __load_spritesheet(self, config):
		for prop in ['image', 'frames', 'animations']:
			if prop not in config: 
				raise Exception(f'"{prop}" property not found in spritesheet!')
		image = pygame.image.load(config['image'])
		image.set_colorkey(pygame.color.Color('#a34d4d'))
		for name, rect in config['frames'].items():
			subimage = pygame.Surface(rect[2:])
			subimage.set_colorkey((0, 0, 0))
			subimage.blit(image, area=rect, dest=(0,0))
			self.__frames[name] = subimage

			# Create a mirror for all left sprites
			if 'left' in name:
				name = name.replace('left', 'right')
				subimage = pygame.Surface(rect[2:])
				subimage.set_colorkey((0, 0, 0))
				subimage.blit(image, area=rect, dest=(0,0))
				self.__frames[name] = pygame.transform.flip(subimage, True, False)
		for name, anim in config['animations'].items():
			speed = anim['speed'] if 'speed' in anim else 0.16
			if 'frames' not in anim: 
				print(f'Warning: Skipping "{name}" animation because it\'s missing "frames" property!')
				del speed
				continue
			animation = Animation(speed)
			for frame in anim['frames']:
				if frame not in self.__frames: continue
				animation.add_frame(self.__frames[frame])
			if animation.length == 0:
				print(f'Warning: No frames in animation! Skipping "{name}"...')
				del animation
				continue
			self.__animations[name] = animation

			# Create a mirror for all left animations
			if 'left' in name:
				name = name.replace('left', 'right')
				animation = Animation(speed)
				for frame in anim['frames']:
					if 'left' in frame: frame = frame.replace('left', 'right')
					if frame not in self.__frames: continue
					animation.add_frame(self.__frames[frame])
				if animation.length == 0:
					print(f'Warning: No frames in animation! Skipping "{name}"...')
					del animation
					continue
				self.__animations[name] = animation
	def __load_map(self, tilesheet, path):
		with open(path) as file:
			config = json.load(file)
		for prop in ['name', 'rows', 'cols', 'map']:
			if prop not in config:
				raise Exception(f'Error: "{prop}" does not exist in tileset config!')
		rows, cols = config['rows'], config['cols']
		*paths, name = path.split('/')
		paths = '/'.join(paths)
		name = name.split('.')[0]

		solids = []
		if 'solid' in config:
			for item in config['solid']:
				if type(item) == int: solids.append(item)
				elif type(item) == list and len(item) == 2:
					solids = [*solids, *range(*item, 1)]

		tileset = TileSet()
		w, h = tilesheet.get_size()
		tile_id = 0
		for y in range(0, h, 16):
			for x in range(0, w, 16):
				surface = pygame.Surface((16, 16))
				surface.blit(tilesheet, dest=(0, 0), area=(x, y, 16, 16))
				tile = Tile(surface, tile_id in solids)
				tileset.add_tile(tile)
				tile_id += 1

		ncols = w // 16
		w, h = cols * 16, rows * 16
		MAP = []
		with open(f'{paths}/{name}.map', 'rb') as f:
			for row in range(rows):
				columns = []
				y = row * 16
				for col in range(cols):
					x = col * 16
					tile = int.from_bytes(f.read(2), 'big')
					columns.append(tile)
				MAP.append(columns)

		self.__maps[config['name']] = TileMap(tileset, MAP)
	def load_spritesheets(self, path):
		for _, __, files in walk(path):
			for file in files:
				name = file.split('.')[0]
				with open(f'{path}/{file}') as file:
					self.__load_spritesheet(json.load(file))
	def load_maps(self, path):
		tilesheet = pygame.image.load('./data/tiles/sheet.png')
		for _, __, files in walk(path):
			for file in files:
				if file[-5:] != '.json': continue
				name = file.split('.')[0]
				self.__load_map(tilesheet, f'{path}/{file}')

if __name__ == '__main__':
	m = AssetManager()
	m.load_spritesheets('./data/sheets')
	m.load_maps('./data/tiles')
	
	pygame.init()
	_map = m.get_map('farm_winter')
	_map.draw(pygame.display.set_mode((1024, 1024)))
	pygame.display.update()

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
