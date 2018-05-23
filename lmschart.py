import cv2
import numpy as np
import math
import sys

if len(sys.argv) != 2:
	print ("Invalid input, \nlmschart.py [filename]")
	quit()

fn = sys.argv[1]


tmp = fn.split(".")
tmp[-2] += "_chart"
tmp[-1] = "png" #png is lossless compression, retains more information
outfn = ".".join(tmp)


img = cv2.imread(fn)
if (img is None):
	print ("Image not found or corrupt")
	quit()
	
(height, width, c) = img.shape



outputimg = np.zeros((555,width,3), np.uint8) #This is the new image we will create

def rgb2lms(r,g,b): #convert rgb to lms cone activation based on conversion forumula
	L = 17.8824 * r + 43.5161 * g + 4.1194 * b
	M = 3.4557 * r + 27.1554 * g + 3.8671 * b
	S = 0.03 * r + 0.1843 * g + 1.4671 * b

	return [L,M,S]

def rgb2lmsf(r,g,b): #normalized number from 0 to 1
	L = 17.8824 * r + 43.5161 * g + 4.1194 * b
	M = 3.4557 * r + 27.1554 * g + 3.8671 * b
	S = 0.03 * r + 0.1843 * g + 1.4671 * b

	return [L/16641.5466,M/8757.4628,S/427.0756]
	#return [L/16707.6055,M/8791.941,S/46.9965]

def lms2rgb(l,m,s): #converts lms back to rgb
	l *= 16641.5466
	m *= 8757.4628
	s *= 427.0756


	r = 0.0809 * l -0.1305 * m + 0.1167 * s
	g = -0.0102 * l + 0.054 * m - 0.1136 * s
	b = -0.0004 * l - 0.0041 * m + 0.6935 * s

	return [r,g,b]


def clamp(a,b,c):
		return max(a,min(b, c))

imgB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #opencv uses BGR, I want RGB for simplicity


middleH = int(height/2) #grab the line of pixels in the middle of the image to avoid 3d graphing


for i in range(0,width): #go through the middle of the input image horizontally
	r = imgB[middleH][i][0]
	g = imgB[middleH][i][1] #grab each color from this pixel from each channel
	b = imgB[middleH][i][2]

	[l,m,s] = rgb2lmsf(r,g,b) #convert it to cone activation levels


	#if we want to attempt to change the color in the lms, we would modify it here
	#l = l * 0.5
	#m = m * 0.5 #note: these do not work as expected because this is happening in the lms color space
	#s = s * 0.5
	#[r2,g2,b2] = lms2rgb(l,m,s)


	#l, m, and s are all in 0-1, we need 0-255 for opencv
	li = int(l*255)
	mi = int(m*255)
	si = int(s*255)


	

	#this part creates the graph at the top
	#I model the l->b, m->g, s->r, simple pixel graphing
	#because the graph can overlay, it grabs the prexisting pixel and modifies the pixel value accordingly
	#e.g. a cross between all three values would create a white pixel, cross between m and s would make a yellow pixel, etc
	#i is the pixel going from left to right, the second fixed value is the color channel
	loc = 255-clamp(0,li,255) #the location of this pixel, subtracting clamp inverts the graph and puts it in a logical direction
	outputimg[loc][i] = (255,outputimg[loc][i][1],outputimg[loc][i][2])
	loc = 255-clamp(0,mi,255)
	outputimg[loc][i] = (outputimg[loc][i][0],255,outputimg[loc][i][2])
	loc = 255-clamp(0,si,255)
	outputimg[loc][i] = (outputimg[loc][i][0],outputimg[loc][i][1],255)


	for m in range(256,300):
		outputimg[m][i] = (r,g,b) #draw the original line of pixels between 256 and 280, creating a 24 pixel high line. 44 if not using the next for loop

	#enable this part if you are modifying the r2, g2, and b2 colors from above. It will show the modified value here
	#for m in range(280,300): #will overwrite half of the original pixels with the new pixels
		#outputimg[m][i] = (r2,g2,b2)


	#300-555 shows difficulty chart
	deltaLM = abs(li-mi) #get the difference between L and M (problematic for dueteranomly). We will represent with green
	outputimg[299+max(0,min(deltaLM, 255))][i] = (0,255,0)

	deltaMS = abs(mi-si) #get the difference between M and S, represent with Red
	outputimg[299+max(0,min(deltaMS, 255))][i] = (255,0,0)

	deltaLS = abs(li-si) #get the difference between L and S, represent with Blue
	outputimg[299+max(0,min(deltaLS, 255))][i] = (0,0,255)





output = cv2.cvtColor(outputimg, cv2.COLOR_RGB2BGR) #go back to opencv's BGR
cv2.imwrite(outfn, output) #output a more exact image
output = cv2.resize(output, (1280,720),interpolation=cv2.INTER_NEAREST ) #scale it up so we can see it. comment out this line for more precise results
#cv2.imwrite("lms.png", img2)
cv2.imshow('Chart',output)
cv2.waitKey(0)
cv2.destroyAllWindows()