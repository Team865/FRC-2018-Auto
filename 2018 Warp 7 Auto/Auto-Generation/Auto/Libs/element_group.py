from copy import deepcopy
from sys import maxsize as maxInt
#from pygame.image import fromstring as loadImage
from pygame.image import load as loadImage
from pygame.transform import rotate as pyRotate
from functools import partial
from numpy import add as tupleAdd
from PIL import Image
import os

def Create_Element_Group(visible):
	a = deepcopy(elementGroup)
	a.visible = visible
	return a
	
def getColourdImage(src):
	print(src)
	with open(src,'rb') as f:
		byte=b''
		data = b''
		while not byte == b'\x00':
			data += byte
			byte = f.read(1)
			
		mode = data.decode()
		imageOffsets = []
		for data in iter(partial(f.read, 5), b''):	
			positive = '{:08b}'.format(data[-1])[-4:]
			tup=()
			for i in range(4):
				rgba = data[i]
				if positive[i] == '1':
					tup += (-1*rgba,)
				else:
					tup += (rgba,)
			imageOffsets.append(tup)
	return {'image':imageOffsets,'mode':mode}

def makeColourdImage(imageOffsets,rgb,size):
	data = imageOffsets['image']
	rgb += (0,)*(4-len(rgb))
	for i in range(len(data)):
		stuff=data[i]
		stuff = tupleAdd(stuff,rgb)
		stuff[3]=abs(stuff[3])		
		data[i]=tuple(stuff)
		
	b = Image.new(imageOffsets['mode'],size)
	b.putdata(data)
	data = b.tobytes()
	print(data[-5:])
	b.close()
	this_image = loadImage(data, size, imageOffsets['mode'])
	return this_image
	
class elementGroup:
	visible = True
	maxSize = [-1*maxInt,-1*maxInt]
	minSize = [maxInt,maxInt]
	lSearch = {}
	nSearch = {}
	def __init__(self,name,data):
		try:
			data['layer'] = int(data['layer'])-1
		except:
			raise ValueError('Layers cant be letters!')
		
		self.__dict__.update(data)
		
		
		self.orgCords = self.cords
		self.orgSize = self.size
		self.name = name
		self.rot = 0
		
		#self.imageOffsets = getColourdImage(self.src)
		
		#self.pyimage = makeColourdImage(self.imageOffsets,self.state_colour[0],self.size)
		self.pyimage = loadImage(self.src)
		self.tranImage = self.pyimage
		
		
		if self.layer in self.lSearch.keys():
			elementGroup.lSearch[self.layer].append(self)
		else:
			elementGroup.lSearch[self.layer] = [self]
		
		elementGroup.nSearch[self.name] = self
		
		a = self.size
		if elementGroup.maxSize[0]  < a[0]:
			elementGroup.maxSize[0] = a[0]
		if elementGroup.maxSize[1]  < a[1]:
			elementGroup.maxSize[1] = a[1]
		if elementGroup.minSize[0] >= a[0]:
			elementGroup.minSize[0] = a[0]
		if elementGroup.minSize[1] >= a[1]:
			elementGroup.minSize[1] = a[1]
		
		self.canStateChange = len(self.state_colour) > 1
		self.visible = elementGroup.visible
	
	def renderFrame(self,screen,resizeOffset):
		a = sorted(self.lSearch.keys())
		for key in a:
			objlst = self.lSearch[key]
			for obj in objlst:
				if obj.visible:
					screen.blit(obj.tranImage,obj.cords)
				obj.size[0] = round(obj.orgSize[0]*resizeOffset[0])
				obj.size[1] = round(obj.orgSize[1]*resizeOffset[1])
				obj.cords[0] = round(obj.orgCords[0]*resizeOffset[0])
				obj.cords[1] = round(obj.orgCords[1]*resizeOffset[1])
	
	
	def contains_point(self, point):
		return (self.cords[0] <= point[0] <= self.cords[0] + self.size[0] and
				self.cords[1] <= point[1] <= self.cords[1] + self.size[1])
	
	def find_element_at_cords(self, point, layer=None):
		def temp(layer):
			for el in layer:
				if el.contains_point(point):
					return el
			return None
		
		if layer is None:
			for i in range(len(self.lSearch)-1,-1,-1):
				la = self.lSearch[i]
				item = temp(la)
				if item is not None:
					return item
		else:
			if layer in self.lSearch.keys():
				return temp(self.lSearch[layer])
			
		return None
	
	def stateUpdate(self):
		#print(self.state_colour[self.state])
		#self.pyimage = makeColourdImage(self.imageOffsets,self.state_colour[self.state],self.orgSize)	
		#self.imageUpdate()
		pass
	
	def imageUpdate(self):
		orig_rect = self.pyimage.get_rect()
		rot_image = pyRotate(self.pyimage, self.rot)
		rot_rect = orig_rect.copy()
		rot_rect.center = rot_image.get_rect().center
		self.tranImage = rot_image.subsurface(rot_rect).copy()
	
	def stateChangeNext(self):
		self.state += 1
		if len(self.state_colour) <= self.state:
			self.state = 0
			
	def stateChangeTo(self,val):
		self.state = val
		a = len(self.state_colour)
		if a <= self.state:
			self.state = 0
		elif self.state < 0:
			self.state = a-1
	
	def toogleVisible():
		elementGroup.visible = not elementGroup.visible
		for obj in elementGroup.nSearch.values():
			obj.visible = elementGroup.visible
	
	def setVisible(visible):
		elementGroup.visible = visible
		for obj in elementGroup.nSearch.values():
			obj.visible = elementGroup.visible
	
	def rotate(self, angle):
		self.rot += angle
		if self.rot >= 360:
			self.rot -= 360
		elif self.rot <= 0:
			self.rot += 360

		self.imageUpdate()
	
	def contains_point(self, point):
		return (self.cords[0] <= point[0] <= self.cords[0] + self.size[0] and
				self.cords[1] <= point[1] <= self.cords[1] + self.size[1])
	
	def init_elements(em, elements):
		def cmpMax():
			if em.maxSize[0]  < elementGroup.maxSize[0]:
				em.maxSize[0] = elementGroup.maxSize[0]
			if em.maxSize[1]  < elementGroup.maxSize[1]:
				em.maxSize[1] = elementGroup.maxSize[1]
				
		def cmpMin():
			if em.minSize[0] >= elementGroup.minSize[0]:
				em.minSize[0] = elementGroup.minSize[0]
			if em.minSize[1] >= elementGroup.minSize[1]:
				em.minSize[1] = elementGroup.minSize[1]
		
		for key, item in elements.items():
			elementGroup(key,item)
		
		if 'maxSize' in em.__dict__.values():
			cmpMax()
		else:
			em.maxSize = elementGroup.maxSize
			
		if 'minSize' in em.__dict__.values():
			cmpMin()
		else:
			em.minSize = elementGroup.minSize
	