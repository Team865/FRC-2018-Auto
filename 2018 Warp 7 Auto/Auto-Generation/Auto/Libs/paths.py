import numpy as np
import pygame
import matplotlib.pyplot as plt
from scipy import interpolate

def line(x,x2,fun):
	b = fun(x)
	m = fun.derivative(1)
	drivatve = m(x)
	y = drivatve*x2+b
	return y

def pixel(surface, color, pos):
    surface.fill(color, (pos, (5, 5)))

class Path:
	def __init__(self,points,lineColour,dotColour):
		self.dotColour = dotColour
		self.lineColour = lineColour
		self.rad = 10
		self.points = [Point(points,self.rad,self),Point(points,self.rad,self)]
		self.calculatePath()
		self.showg = False
		
	def renderFrame(self,a,screen,b):
		for point in self.points:
			point.renderFrame(screen,self.dotColour)
		
		if self.showg:
			xp = np.linspace(0, len(self.points)-1)
			_ = plt.plot(xp, self.calculated[0](xp), '-',xp, self.calculated[1](xp), '--')
			plt.ylim(0,2000)
			plt.show()
			plt.gcf().clear()
			self.showg = False
			
		m=len(self.points)-1
		z=0
		n = 1/10
		while z<m:
			pointX = self.calculated[0](z)
			pointY =  self.calculated[1](z)
			a = line(2.5,z,self.calculated[0])
			b = line(2.5,z,self.calculated[1])
			a2 = line(2.5,z*-1,self.calculated[0])
			b2 = line(2.5,z*-1,self.calculated[1])
			try:
				pixel(screen,self.lineColour,(a,b))
				pixel(screen,self.lineColour,(a2,b2))
			except ValueError:
				pass
			pixel(screen,self.lineColour,(pointX,pointY))
			z += n
	
	def calculatePath(self):
		x=[]
		y=[]
		for point in self.points:
			x.append(point.cords[0])
			y.append(point.cords[1])
		
		x = np.array(x)
		y = np.array(y)
		num = len(self.points)
		n = range(0,num)
		num *= 5
		# x = np.poly1d(np.polyfit(n, x, num))
		# y = np.poly1d(np.polyfit(n, y, num))
		x = interpolate.Akima1DInterpolator(n,x)
		y = interpolate.Akima1DInterpolator(n,y)
		# x = interpolate.CubicSpline(n,x)
		# y = interpolate.CubicSpline(n,y)
		
		self.calculated = (x,y)
	
	def addPoint(self,point):
		self.points.append(Point(point,self.rad,self))
		self.calculatePath()		

	def find_element_at_cords(self,a, cords, layer=None):
		for point in self.points:
			if point.inCircle(cords[0],cords[1]):
				return point
		
		return None 
		
class Point:
	def __init__(self,cords,size,path):
		self.path = path
		self.cords = list(cords)
		self.rad = size
	
	def inCircle(self, x, y):
		distancesquared = (x - self.cords[0]) * (x - self.cords[0]) + (y - self.cords[1]) * (y - self.cords[1]);
		return distancesquared <= self.rad * self.rad;
	
	def renderFrame(self,screen,colour):
		pygame.draw.circle(screen, colour, self.cords, self.rad, 0)
		
		