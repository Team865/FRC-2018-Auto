import numpy as np
import pygame
import matplotlib.pyplot as plt
from scipy import interpolate
import json
from math import hypot

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
		x = interpolate.Akima1DInterpolator(n,x)
		y = interpolate.Akima1DInterpolator(n,y)
		
		self.calculated = (x,y)
	
	def addPoint(self,point):
		self.points.append(Point(point,self.rad,self))
		self.calculatePath()		

	def find_element_at_cords(self,a, cords, layer=None):
		for point in self.points:
			if point.inCircle(cords[0],cords[1]):
				return point
		
		return None 
	
	def exportPath(self, fName):
		print("Exporting...")
		data = []
		totalDistance=0.0;
		n = 1/1000000
		lastX=self.calculated[0](0)
		lastY=self.calculated[1](0)
		for i in range(len(self.points)):
			point = self.points[i]
			pointData = {"point": point.cords}
			z=0
			distance=0.0
			while True:
				pointX = self.calculated[0](z+i)
				pointY =  self.calculated[1](z+i)
				distance += hypot(pointX-lastX,pointY-lastY)
				lastX = pointX
				lastY = pointY
				z += n
				if z<i+1:
					break
			
			pointData["distance"] = distance
			totalDistance += distance
			pointData["methods"] = [
				{"name":"print",
					"args":[
					   "hello",
					   "world"
					]
				}
			]
			data.append(pointData)
		
		exportedPath = {"data": data, "description": "describes the auto", "sides": "LLL", "totalDistance":totalDistance}
		with open(fName, 'w') as f:
			f.write(json.dumps(exportedPath, sort_keys=True, indent=4))
		print("Done!")
		
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
		
		