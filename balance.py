import pypot.dynamixel
import time
import cv2
import numpy as np


abc =True
y,u,v = 0,91,80

cap = cv2.VideoCapture(1)
f = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('Output.avi',f,20.0,(640,480))
def sniper():

	rec=True	
	while rec:
		rec,img = cap.read()
		img_yuv = cv2.cvtColor(img,cv2.COLOR_BGR2YUV)
		out.write(img)
	
		blur = cv2.GaussianBlur(img_yuv,(11,11),2)
		ball = cv2.inRange(blur, (np.array([0,u-30,v-30])), (np.array([255,u+30,v+30])))
		im_floodfill = ball.copy()
		h, w = ball.shape[:2]
		mask = np.zeros((h+2, w+2), np.uint8)
		cv2.floodFill(im_floodfill, mask, (0,0), 255)
		fill = cv2.bitwise_and(im_floodfill,im_floodfill,mask = ball)

		if cv2.waitKey(25)&0xff==27:
		    break

		cv2.rectangle(img, (310,230), (330,250), (255,255,255),2)
		crop_img = fill[230:250, 310:330]
	
		images,s_contour,hierarchy = cv2.findContours(crop_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

		images,contour,hierarchy = cv2.findContours(fill,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

		cv2.drawContours(img, contour, -1, (0,255,0), 2)

		cv2.imshow("",img)
		#cv2.imshow("mask",im_floodfill)
		
		t=time.time()
		if len(contour)>=1:
			cnt = contour[0]
			(x,y),radius = cv2.minEnclosingCircle(cnt)
			center = (float(x),float(y),t)
			return center
		else:
			return (-1,-1,t)


def init() :
	ports = pypot.dynamixel.get_available_ports()
	if not ports :
		raise IOError("Port not connected")

	print "Port:",ports[0]

	global dxl
	dxl = pypot.dynamixel.DxlIO(ports[0])
	global ids
	ids = dxl.scan(range(25))
	print ids
	dxl.enable_torque(ids)
	if len(ids)<1 :
		raise RuntimeError("Motor error")



def get_speed():
	pos0=sniper()
	pos1=sniper()
	if pos0[0]<0 or pos1[0]<0:
		#print "No ball"
		return -1E20,-1E20
	else:
		return (float(pos1[0]-pos0[0])/float(pos1[2]-pos0[2])),pos1[0]

t0=time.time()
init()
while True:
	dat=get_speed()
	vel=dat[0]
	dist=dat[1]-320
	k1=20.0/300
	k2=0.02
	angle=k1*dist+k2*vel
	print "t="+str(time.time()-t0)+" v="+str(vel)+" x="+str(dist)+" 8="+str(angle)
	if angle>20 or angle<-20:
		pass
	else:
		dxl.set_goal_position({22:-angle})
