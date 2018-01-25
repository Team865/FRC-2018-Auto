import subprocess
import re
import os
from shutil import move
from PIL import Image, ImageChops
from colorthief import ColorThief
from copy import deepcopy
from collections import OrderedDict
from numpy import subtract as tupleSubtract
import json

def load_build_config(fName):
	def parse(a):
		vals = a.split('+/')
		path = ""
		for val in vals:
			if val in globals():
				path += globals()[val]
			else:
				path += val
		
		return path+'/'
	
	def path_gen(mainItem):
		print('Building paths...')
		for prop, item in mainItem.items():
			item = parse(item)
			print('\t'+item)
			globals()[prop] = item
			if not os.path.exists(item):
				os.makedirs(item)
				
	with open(fName, 'r') as f:
		a = json.load(f, object_pairs_hook=OrderedDict)
	
	for mainProp, mainItem in a.items():
		if mainProp == 'paths':
			path_gen(mainItem)

def get_image_sum(imgpath,color_count=10, quality=10):
	color_thief = ColorThief(imgpath[0])
	palette = color_thief.get_palette(color_count, quality)
	return(palette)

def getBbox(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return bbox
	
def find_object(imp):
	im = Image.open(imp)	
	bbox = getBbox(im)
	im1 = im.crop(bbox)
	im.close()
	color_thief=None
	color_thief = ColorThief('pdn/1x1.png')
	color_thief.image = im1
	im1.save(imp)
	orgVal = color_thief.get_palette(color_count=2, quality=10)[0]
	#a = [tuple(tupleSubtract(orgVal,(val+((0,)*(4-len(val))))[:-1]))+val[-1:] for val in im1.getdata()]
	size = im1.size
	mode = im1.mode
	im1.close()
	'''
	with open(imp,'wb') as f:
		f.write(mode.encode())
		f.write(bytes([0]))
		for tup in a:
			data = b''
			positive = '1111'
			for i in range(4):
				rgba = tup[i]
				if rgba < 0:
					rgba = abs(rgba)
					positive = positive[:i] + '0' + positive[i+1:]
				data += bytes([rgba])

			data += bytes([int(positive,2)])
			f.write(data)
			data=b''
	'''
	return (bbox[:2],size,orgVal)

def extract_pdn(pdnfile,loc):
	print('Extracting pdn...')
	subprocess.call(['pdn2png.exe','/split', '/outfile=.\\'+loc+'\\.png', pdnfile])

def read_json(fName):
	with open(fName, 'r') as f:#yes i know of json.load() 
		types = eval(f.read())#json loads errors with->json.decoder.JSONDecodeError: Invalid \escape: line 2 column 14 (char 15)
		#errors because of RE in json
	return types

def apply_re_compiler(types):
	elementConfig=OrderedDict()
	for key in types.keys():
		elementConfig[re.compile(key)] = types[key]
	types=None
	return elementConfig

def generate_assets(elementConfig):
	objects ={}
	for x in os.listdir(directoryElements):
		if  x.startswith('-L') and x.endswith(".png"):
			layer = int(re.split('-L|Normal',x)[1])
			x = '{}/{}'.format(directoryElements,x)
			b = re.sub('(-)(L)(\d+)(Normal)(\d+)(V)','',x)
			move(x,b)
			for element in elementConfig.keys():
				d = element.findall(b)
				c=len(d)-1
				if c>=0:
					value = deepcopy(elementConfig[element])#FeelsDeepMan
					print('\t'+b)
					value['cords'], value['size'],p = find_object(b)
					
					if 'moveable' not in value:
						value['moveable'] = False
					
					if 'state' not in value:
						value['state'] = 0
						
					if 'state_colour' in value:
						value['state_colour'][:] = [p] + value['state_colour']
					else:
						value['state_colour'] = [p]
					
					value['src'] = b.replace(directoryGame,'',1)
					value['layer'] = layer
					objects[(''.join(d[c])).split('.')[0]] = value
					break
	return objects
		
def write_config(fName,objects):
	with open(directoryConfig+fName, 'w') as f:
		json.dump(objects,f)

def main():
	pdnfile = 'pdn/FieldGameLayers1px-1cm.pdn'
	extract_pdn(pdnfile,directoryElements)
	elementConfig = read_json('objects.json')
	elementConfig = apply_re_compiler(elementConfig)
	elementConfig[re.compile('[^/]+$')] = {}
	print('Generating assets...')
	objects = generate_assets(elementConfig)
	write_config('config.json',objects)
	
if __name__ == '__main__':
	load_build_config('BuildConfig.json')
	main()