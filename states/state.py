_UNIMPLEMENTED_ERROR = Exception('Failed to execute abstract method!')

class _State:
	def __init__(self, sm):
		self.__sm = sm
	@property
	def game(self): return self.__sm.game
	def update(self, dt): raise _UNIMPLEMENTED_ERROR
	def draw(self, game): raise _UNIMPLEMENTED_ERROR
	def keyup(self, key): pass
	def keydown(self, key): pass
	def dispose(self): pass

class StateManager:
	def __init__(self, game):
		self.__game = game
		self.__states = []
		self.__keys = [False for i in range(256)]
	@property
	def game(self): return self.__game
	@property
	def current(self):
		return None if len(self.__states) == 0 else self.__states[-1]
	@property
	def keys(self): 
		return self.__keys
	def push(self, State):
		if not (State and issubclass(State, _State)): 
			return print('Warning: Trying to push a non State object!')
		self.__states.append(State(self))
	def pop(self):
		if len(__states) == 0: 
			return print('Warning: Trying to pop state when there is no state!')
		*self.__states, state = self.__states
		state.dispose()
	def set(self, state):
		self.pop()
		self.push()
	def update(self, dt):
		if len(self.__states) == 0: return
		self.current.update(dt)
	def draw(self, game):
		if len(self.__states) == 0: return
		self.current.draw(game)
	def keyup(self, key):
		self.__keys[key] = False
		if len(self.__states) == 0: return
		self.current.keyup(key)
	def keydown(self, key):
		self.__keys[key] = True
		if len(self.__states) == 0: return
		self.current.keydown(key)