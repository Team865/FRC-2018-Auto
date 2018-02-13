import pygame
import os, sys, json
from Libs.element_group import Create_Element_Group
from Libs.paths import Path

class Renderer:
	def __init__(self,display):
		self.display = display
		self.emList = []
		self.nSearch = {}		
	
	def renderFrame(self,egList=[]):
		if len(egList) == 0:
			egList = self.emList
		
		for em in egList:
			a = sorted(em.gSearch.keys())
			for key in a:
				eL = em.gSearch[key]
				for eg in eL.values():
					eg.renderFrame(eg,self.screen,self.resizeOffset)
				
		a=pygame.transform.scale(self.screen,self.screen.get_size())
		self.screen.blit(a,(0,0))
		self.update()

		
	def setSize(self,size):
		self.orgSize = [float(size[0]),float(size[1])]
		self.resizeOffset = [1.0,1.0]
		self.screen = self.display.set_mode(size, pygame.HWSURFACE | pygame.RESIZABLE)
		
	def sizeWindowUpdate(self,size):
		self.resizeOffset[0] = size[0]/self.orgSize[0]
		self.resizeOffset[1] = size[1]/self.orgSize[1]
		self.screen = self.display.set_mode(size, pygame.HWSURFACE |pygame.RESIZABLE)
	
	def em_regiser(self,em,renderQueue):
		try:
			layer = int(renderQueue)
		except:
			raise ValueError('renderQueue cant be letters!')
			
		self.emList[renderQueue:renderQueue] = [em]
		self.nSearch[em.name] = em
	
	def find_obj_at_cords(self,cords,em=None, group=None,layer=None):
		def temp(em):
			item = em.find_obj_at_cords(cords,group=None, layer=layer)
			if item is not None:
				return item
			return None
			
		if em is None:
			for em in self.nSearch.values():
				item = temp(em)
				if item is not None:
					return item
		else:
			if em in self.nSearch.keys():
				return temp(self.nSearch[em])
			
		return None
	
	def update(self):
		self.display.flip()

class ElementMannger:
	emSearch = {}
	def __init__(self,name):
		self.gSearch = {} 
		self.nSearch = {}
		self.name = name
		ElementMannger.emSearch[self.name] = self
		
	def add_group(self,name,group,func):
		try:
			group = int(group)
		except:
			raise ValueError('Groups cant be letters!')
		
		if group in self.gSearch.keys():
			self.gSearch[group].update({name:func})
		else:
			self.gSearch[group] = {name:func}
			
		self.nSearch[name] = func
		
		return func
	
	def find_obj_at_cords(self,cords,group=None,layer=None):
		def temp(group):
			for eg in group.values():
				item = eg.find_element_at_cords(eg,cords,layer=layer)
				if item is not None:
					return item
			return None
			
		if group is None:
			for i in range(len(self.gSearch)-1,-1,-1):
				group = self.gSearch[i]
				item = temp(group)
				if item is not None:
					return item
		else:
			if group in self.gSearch.keys():
				return temp(self.gSearch[group])
			
		return None
	
	def init_item(self,elements, name=None, obj=None):
		if obj is None:
			if name is None:
				raise IndexError('Name is type None')
			obj = self.nSearch[name]
		obj.init_elements(self,elements)
		
def getConfigfile(fName):
	with open(directoryConfig+fName, 'r') as f:
		a = json.load(f)
	return a

directoryConfig = 'Config/'
LMB = 1
MMB = 2
RMB = 3
SU  = 4
SD  = 5

def main():
	def left_mouse_down():
		nonlocal e
		obj = myRenderer.find_obj_at_cords(e.pos,em='bobr00s',group=0)
		if type(obj).__name__ == 'elementGroup' and obj.moveable:
			dragging = True
			mouse_x, mouse_y = e.pos
			offset_x = obj.cords[0] - mouse_x
			offset_y = obj.cords[1] - mouse_y
			while dragging:
				e = pygame.event.wait()
				if e.type == pygame.MOUSEBUTTONUP:
					if e.button == 1:            
						dragging = False

				elif e.type == pygame.MOUSEMOTION:
					if dragging:
						mouse_x, mouse_y = e.pos
						obj.cords[0] = mouse_x + offset_x
						obj.cords[1] = mouse_y + offset_y
				elif e.button == SU:
					obj.rotate(10)
				elif e.button == SD:
					obj.rotate(-10)
				
				myRenderer.renderFrame()
				myRenderer.update()
		elif type(obj).__name__ == 'Point':
			dragging = True
			mouse_x, mouse_y = e.pos
			offset_x = obj.cords[0] - mouse_x
			offset_y = obj.cords[1] - mouse_y
			while dragging:
				e = pygame.event.wait()
				if e.type == pygame.MOUSEBUTTONUP:
					if e.button == 1:
						dragging = False
						obj.path.calculatePath()

				elif e.type == pygame.MOUSEMOTION:
					if dragging:
						mouse_x, mouse_y = e.pos
						obj.cords[0] = mouse_x + offset_x
						obj.cords[1] = mouse_y + offset_y
				
				myRenderer.renderFrame()
				myRenderer.update()
	
	def middle_mouse_down():
		nonlocal e
		obj = myRenderer.find_obj_at_cords(e.pos,em='bobr00s',group=0)
		if obj.canStateChange:
			obj.stateChangeNext()
			obj.stateUpdate()
			print(obj.state)
		
	def right_mouse_down():
		nonlocal e
	
	pygame.init()
	elements = getConfigfile('config.json')
	a = ElementMannger('bobr00s')
	b = a.add_group('wow',0,Create_Element_Group(visible=True))
	myRenderer = Renderer(pygame.display)
	a.init_item(elements,obj=b)
	myRenderer.setSize(a.maxSize)
	myRenderer.em_regiser(a,0)

	try:
		myRenderer.renderFrame()
		while True:
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					raise StopIteration
					
				if e.type == pygame.MOUSEBUTTONDOWN:
					myRenderer.renderFrame()
					if e.button == LMB:
						left_mouse_down()
					elif e.button == MMB:
						middle_mouse_down()
					elif e.button == RMB:
						right_mouse_down()
						
					myRenderer.update()
				elif e.type == pygame.VIDEORESIZE:
					myRenderer.sizeWindowUpdate((e.w, e.h))
					myRenderer.update()
				
				elif e.type == pygame.KEYDOWN:
					if e.key == pygame.K_p:
						b = a.add_group('PointCurve',1,Path(pygame.mouse.get_pos(),(255,255,255),(255,255,255)))
					elif e.key == pygame.K_a:	
						b.showg = True
					elif e.key == pygame.K_n:	
						b.addPoint(pygame.mouse.get_pos())
					elif e.key == pygame.K_x:	
						b.exportPath("ExportedPath.json")
				
	except StopIteration:
		pass

	pygame.quit()

if __name__ == '__main__':
	main()