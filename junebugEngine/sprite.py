import pygame
import json
import os.path
import enum

# TODO: consider defining this elsewhere
class Orientation:
	LEFT = -2
	RIGHT = 2

class Alignment(enum.IntEnum):
	CENTER = 0
	LEFT = 1
	RIGHT = 2
	TOP = 4
	BOTTOM = 8
	TOP_LEFT = 5
	TOP_RIGHT = 6
	BOTTOM_LEFT = 9
	BOTTOM_RIGHT = 10

class AnimSprite(pygame.sprite.Sprite):
	typeName = None

	def __init__(self, json_file, layer, position, mirror_h, alignment = Alignment.BOTTOM_LEFT):
		super().__init__()

		self.layer = layer
		layer.entities.add(self)

		data = json.load(open(json_file))

		folder = os.path.dirname(json_file) + os.sep

		image = pygame.image.load(folder + data['meta']['image']).convert()
		image.set_colorkey((255,0,255))

		self.x = position[0]
		self.y = position[1] - image.get_size()[1] 


		allFramesRight = []
		allFramesLeft = []

		for frame in data['frames']:
			x = frame['frame']['x']
			y = frame['frame']['y']
			w = frame['frame']['w']
			h = frame['frame']['h']

			rect = pygame.Rect(x,y,w,h)
			self.size = (int(w), int(h))
			frameImg = pygame.transform.scale(image.subsurface(rect),self.size)
			duration = frame['duration']

			allFramesRight.append((frameImg,duration))
			allFramesLeft.append((pygame.transform.flip(frameImg, True, False),duration))

		self.animations = {
			Orientation.LEFT: {},
			Orientation.RIGHT: {}
		}

		for animation in data['meta']['frameTags']:
			name = animation['name']
			first = animation['from']
			last = animation['to']
			direction = animation['direction']

			framesRight = allFramesRight[first:last+1]
			framesLeft = allFramesLeft[first:last+1]

			self.animations[Orientation.RIGHT][name]=(framesRight,direction)
			self.animations[Orientation.LEFT][name]=(framesLeft,direction)

		# adjust position to alignment

		if alignment & Alignment.TOP:
			self.y += self.size[1]
		elif not (alignment & Alignment.BOTTOM):
			self.y += self.size[1] / 2
		if alignment & Alignment.RIGHT:
			self.x -= self.size[0]
		elif not (alignment & Alignment.LEFT):
			self.x -= self.size[0] / 2


		self.setPosition((int(self.x), int(self.y)))

		if mirror_h:
			self.orientation = Orientation.LEFT
		else:
			self.orientation = Orientation.RIGHT
		self.setAnimation(data['meta']['frameTags'][0]['name'])

	def setProperties(self, properties):
		self.properties = properties

	def die(self):
		if not self.setAnimation('die'):
			self.kill()
		self.on_death()
	
	def on_death(self):
		pass

	def on_screen_exit(self):
		pass

	def on_screen_enter(self):
		pass

	def setAnimation(self,animation):
		if animation in self.animations[self.orientation]:
			self.currentAnimationName = animation
			self.currentAnimation = self.animations[self.orientation][animation]

			if(self.currentAnimation[1] == 'reverse'):
				self.frameNo = len(self.currentAnimation[0]) - 1
			else:
				self.frameNo = 0

			self.frameTime = 0
			self.direction = self.currentAnimation[1]
			self.image = self.currentAnimation[0][self.frameNo][0]
			return True
	
	def animationDuration(self, animation):
		return sum([frame[1] for frame in self.animations[self.orientation].get(animation, [])[0]])

	def setPosition(self, position):
		self.rect = pygame.Rect(position, self.size)

	def on_animationFinished(self):
		if self.currentAnimationName == "die":
			self.kill()

	def update(self, ms):
		self.frameTime = self.frameTime + ms
		curr = self.currentAnimation[0][self.frameNo]
		direction = self.currentAnimation[1]
		if self.frameTime > curr[1]:
			self.frameTime = self.frameTime - curr[1]
			if self.direction == 'pingpong':
				self.frameNo = self.frameNo + 1
				if self.frameNo == len(self.currentAnimation[0]) - 1:
					self.direction = 'pingpong_r'
			elif self.direction == 'pingpong_r':
				self.frameNo = self.frameNo - 1
				if self.frameNo == 0:
					self.direction = 'pingpong'
			elif self.direction == 'reverse':
				self.frameNo = (self.frameNo - 1) % len(self.currentAnimation[0])
				if (self.frameNo == len(self.currentAnimation[0]) - 1):
					self.on_animationFinished()
			else:
				self.frameNo = (self.frameNo + 1) % len(self.currentAnimation[0])
				if self.frameNo == 0:
					self.on_animationFinished()
		self.image = self.currentAnimation[0][self.frameNo][0]
