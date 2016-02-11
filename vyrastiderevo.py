import numpy as np
import pygame as pg, sys
from pygame.locals import *

pg.init()
DISPLAYSURF = pg.display.set_mode((600, 500))
pg.display.set_caption('vyrastiderevo')

#Set up colours
black = (0, 0, 0)
blue = (0, 0, 255)
gray = (128, 128, 128)
red = (255, 0, 0)
silver = (192,192,192)
white = (255,255,255)

def dist(x1,y1,x2,y2):
    d=((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))**0.5
    return d

def angle(x0,y0,x1,y1):
    #what angle (0 to 2*pi) forms a ray(x0,y0),(x1,y1) with zero
    if x0==x1:
        if y1<y0:
            gamma=np.pi/2
        else:
            gamma=np.pi*3/2
    else:			
        aatan=np.arctan((y0-y1)/(x1-x0))
        if aatan==0:
            if x1>x0:
                gamma=0
            else:
                gamma=np.pi
        elif aatan>0:
            if x1>x0:
                gamma=aatan
            else:
                gamma=aatan+np.pi/2
        else:
            if x1>x0:
                gamma=aatan+np.pi/2
            else:
                gamma=aatan+np.pi
    return gamma

def arcplatform_intersection(arc,platform):
    xa=arc[0]
    ya=arc[1]
    radius=arc[2]
    x1p=platform[0]
    x2p=platform[1]
    yp=platform[2]
    angle1=min(arc[4],arc[5])*np.pi/180
    angle2=max(arc[4],arc[5])*np.pi/180
    intersection=False
    if (((x1p<xa<x2p and (yp-radius)<ya<(yp+radius)) or
         dist(xa,ya,x1p,yp)<radius or
         dist(xa,ya,x2p,yp)<radius) and
        (not(dist(xa,ya,x1p,yp)<radius-width and
             dist(xa,ya,x2p,yp)<radius-width))):
        #if imaginated whole ring crosses the platform, check angles:
        angles_to_check=()

        #intersections with big cercle:
        deltax=(radius*radius-(yp-ya)*(yp-ya))**0.5
        if x1p<(xa+deltax)<x2p:
            a=np.arcsin((ya-yp)/radius)
            if a<0:
                a+=np.pi*2
            angles_to_check+=(a,)
        if x1p<(xa-deltax)<x2p:
            a=np.pi-np.arcsin((ya-yp)/radius)
            angles_to_check+=(a,)

        #intersections with small cercle:
        if radius>width and abs(radius-width)>abs(yp-ya):

            deltax=((radius-width)*(radius-width)-(yp-ya)*(yp-ya))**0.5
            if x1p<(xa+deltax)<x2p:
                a=np.arcsin((ya-yp)/(radius-width))
                if a<0:
                    a+=np.pi*2
                angles_to_check+=(a,)
            if x1p<(xa-deltax)<x2p:
                a=np.pi-np.arcsin((ya-yp)/(radius-width))
                angles_to_check+=(a,)    

        #checking angles
        for a in angles_to_check:
            if angle1<a<angle2 or angle1<(a+np.pi)<angle2:
                intersection=True
                break
        else:
            #checking ends of platforms
            xends=(x1p,x2p)
            for xp in xends:
                a=angle(xa,ya,xp,yp)
                if angle1<(a)<angle2 or angle1<(a+np.pi)<angle2:
                    if (radius-width)<dist(xa,ya,xp,yp)<radius:
                        intersection=True
                        break
    return intersection   

def lineplatform_intersection(line,platform):
    x0=line[1]
    y0=line[2]
    deltax=line[3]
    deltay=line[4]
    intersection=False

    long=dist(0,0,deltax,deltay)
    semiwidth_x=width/2*deltay/long
    semiwidth_y=-width/2*deltax/long
    pointlist=[(x0+semiwidth_x,y0+semiwidth_y),
               (x0-semiwidth_x,y0-semiwidth_y),
               (x0+deltax-semiwidth_x,y0+deltay-semiwidth_y),
               (x0+deltax+semiwidth_x,y0+deltay+semiwidth_y)]

    higher=()
    for point in pointlist:
        higher+=(point[1]>platform[2],)
    intersection_with_line=False
    paires_of_points=()
    for i in range(4):
        if not higher[i]==higher[i-1]:
            intersection_with_line=True
            paires_of_points+=((pointlist[i-1],pointlist[i]),)

    if intersection_with_line:
        xes_of_sec=()
        for pair in paires_of_points:
            #x=ky+b
            x1=pair[0][0]
            y1=pair[0][1]
            x2=pair[1][0]
            y2=pair[1][1]
            k=(x1-x2)/(y1-y2)
            b=(x1*y2-x2*y1)/(y2-y1)
            xsec=k*platform[2]+b
            xes_of_sec+=(xsec,)

        if xes_of_sec[1]<xes_of_sec[0]:
            xes_of_sec=(xes_of_sec[1],xes_of_sec[0])

        xes_of_platform=(platform[0],platform[1])
        zones=() #True = in the left, False = in the right
        for x in xes_of_platform:
            if xes_of_sec[0]<=x<=xes_of_sec[1]:
                intersection=True
                break
            zones+=(x<xes_of_sec[0],)
        else:
            intersection=not(zones[0]==zones[1])
    return intersection
		
        

def my_draw_line(line):
    x0=line[1]
    y0=line[2]
    deltax=line[3]
    deltay=line[4]

    long=dist(0,0,deltax,deltay)
    semiwidth_x=width/2*deltay/long
    semiwidth_y=-width/2*deltax/long
    pointlist=((x0+semiwidth_x,y0+semiwidth_y),
               (x0-semiwidth_x,y0-semiwidth_y),
               (x0+deltax-semiwidth_x,y0+deltay-semiwidth_y),
               (x0+deltax+semiwidth_x,y0+deltay+semiwidth_y))
    pg.draw.polygon(DISPLAYSURF,gray,pointlist,0)
	
def my_draw_arc(arc):
    x=arc[0]
    y=arc[1]
    radius=arc[2]
    angle_begin=arc[4]
    angle_end=arc[5]

    angle_1=min(angle_begin,angle_end)*np.pi/180
    angle_2=max(angle_begin,angle_end)*np.pi/180
    pg.draw.arc(DISPLAYSURF,gray,(x-radius,y-radius,radius*2,radius*2),
                angle_1,angle_2+0.1,width)
    pg.draw.arc(DISPLAYSURF,gray,(x-radius+1,y-radius,radius*2,radius*2),
                angle_1,angle_2+0.1,width)
    pg.draw.arc(DISPLAYSURF,gray,(x-radius,y-radius+1,radius*2,radius*2),
                angle_1,angle_2+0.1,width)

def angle_min_to_bornes(angle_begin,angle_end): #brings the smallest of angles between 0 et 360
    while angle_begin<0 or angle_end<0:
        angle_begin+=360
        angle_end+=360
    while min(angle_begin,angle_end)>360:
        angle_begin-=360
        angle_end-=360
    return(angle_begin,angle_end)

def tree_arc(tree,left,right):
    #seek the last arc
    j=-1
    previous=tree[j]
    deltax_lines=0
    deltay_lines=0
    while previous[0]=='line':
        deltax_lines+=previous[3]
        deltay_lines+=previous[4]
        j-=1
        previous=tree[j]
        
    if left==right: #we will draw line
        if left>0:
            long=alpha*np.pi/180*width*left
            angle_line=previous[5]*np.pi/180
            if previous[3]:
                angle_line+=np.pi/2
            else:
                angle_line-=np.pi/2
            x0=previous[0]+deltax_lines+(previous[2]-width/2)*np.cos(previous[5]*np.pi/180)
            y0=previous[1]+deltay_lines-(previous[2]-width/2)*np.sin(previous[5]*np.pi/180)
            delta_x=long*np.cos(angle_line)
            delta_y=-long*np.sin(angle_line)
            line=('line',x0,y0,delta_x,delta_y)

            #verify intersection
            for platform in tuple_of_platforms:
                if platform[3]: #flip line
                    vline=(line[0],line[2],line[1],line[4],line[3])
                else:
                    vline=line
                if lineplatform_intersection(vline,platform):
                    break
            else:
                tree+=(line,)
                my_draw_line(line)

    else: #we will draw arc
        radius=width*max(left,right)/abs(right-left)
        sign=right>left
        deltaangle=alpha*(right-left)
        if sign==previous[3]:
            angle_begin=previous[5]
            x=previous[0]+np.cos(np.pi/180*previous[5])*(previous[2]-radius)
            y=previous[1]-np.sin(np.pi/180*previous[5])*(previous[2]-radius)
        else:
            angle_begin=previous[5]-180
            x=previous[0]+np.cos(np.pi/180*previous[5])*(previous[2]+radius-width)
            y=previous[1]-np.sin(np.pi/180*previous[5])*(previous[2]+radius-width)
    
        x+=deltax_lines
        y+=deltay_lines
    	
        angle_end=angle_begin+deltaangle
    
        #both angles will be positive, minimum will be in 0<a<360
        (angle_begin,angle_end)=angle_min_to_bornes(angle_begin,angle_end)
    
        angle_1=min(angle_begin,angle_end)*np.pi/180
        angle_2=max(angle_begin,angle_end)*np.pi/180
    
        arc=(x,y,radius,sign,angle_begin,angle_end)
		
        #verify intersection
        for platform in tuple_of_platforms:
            if platform[3]:	#flip the arc (to virtual_arc) to verify crossing with vertical platforms
                vangle_begin=270-arc[4]
                vangle_end=270-arc[5]
                (vangle_begin,vangle_end)=angle_min_to_bornes(vangle_begin,vangle_end)
                varc=(arc[1],arc[0],arc[2],arc[3],vangle_begin,vangle_end)
            else:
                varc=arc
            if arcplatform_intersection(varc,platform):
                break
        else:
            tree+=(arc,)
            my_draw_arc(arc)
    return(tree)

def moveplt():
    global chpos,ch_place
    flag_tree=False
    if chpos[1]<ch_place[2]-chsize-1:
        chpos[1]+=fallv*clock.get_time() #fall
    elif chpos[1]>ch_place[2]-chsize:
        chpos[1]=ch_place[2]-chsize-1
    else:
        if chpos[0]<ch_place[0]+chsize:
            chpos[0]=ch_place[0]+chsize+1
        elif chpos[0]>ch_place[1]-chsize:
            chpos[0]=ch_place[1]-chsize-1
        else:
            if event.type == pg.KEYDOWN:
                if event.key==pg.K_d:
                    chpos[0]+=chv*clock.get_time()
                if event.key==pg.K_a:
                    chpos[0]-=chv*clock.get_time()
    if (crdseed[0]-width/2)<chpos[0]<(crdseed[0]+width/2) and (crdseed[1]-chsize-2)<chpos[1]<(crdseed[1]-chsize+2) and len(tree1)>1:
        if event.type == pg.KEYDOWN:
            if event.key==pg.K_w:
                chpos=[crdseed[0],crdseed[1]]
                ch_place=tree1[1]
                flag_tree=True
    return(flag_tree)

def movetree():
    global chpos,ch_place,i_tree,passage
    ch_place=tree1[i_tree]

    if ch_place[0]=='line':
        moveline()
    else:
        movearc()

    if event.type == pg.KEYDOWN:
        if event.key==pg.K_e:
            dpossibleplatforms={} #dict
            ypossibleplatforms=() #tuple
            for j in range(len(tuple_of_platforms)):
                if not tuple_of_platforms[j][3]:
                    if tuple_of_platforms[j][0]<=chpos[0]<=tuple_of_platforms[j][1] and chpos[1]<=(tuple_of_platforms[j][2]+1):
                        dpossibleplatforms[tuple_of_platforms[j][2]]=j
                        ypossibleplatforms+=(tuple_of_platforms[j][2],)
            dkey=min(ypossibleplatforms)
            j_number=dpossibleplatforms[dkey]
            ch_place=tuple_of_platforms[j_number]

def moveline():
    global chpos,ch_place,i_tree,passage

    long=dist(0,0,ch_place[3],ch_place[4])

    if passage==1:
        chpos=[ch_place[1],ch_place[2]]
        passage=0
    if passage==-1:
        chpos=[ch_place[1]+ch_place[3],ch_place[2]+ch_place[4]]
        passage=0

    if event.type == pg.KEYDOWN:
        if event.key==pg.K_w:
            chpos[0]+=chv*clock.get_time()*ch_place[3]/long
            chpos[1]+=chv*clock.get_time()*ch_place[4]/long
        if event.key==pg.K_s:
            chpos[0]-=chv*clock.get_time()*ch_place[3]/long
            chpos[1]-=chv*clock.get_time()*ch_place[4]/long
    
    if ((chpos[0]<ch_place[1] and ch_place[3]>0) or
        (chpos[0]>ch_place[1] and ch_place[3]<0) or
        (chpos[1]<ch_place[2] and ch_place[4]>0) or
        (chpos[1]>ch_place[2] and ch_place[4]<0)):
        if i_tree>1:
            i_tree-=1
            passage=-1
        else:
            passage=1

    if ((chpos[0]>(ch_place[1]+ch_place[3]) and ch_place[3]>0) or
        (chpos[0]<(ch_place[1]+ch_place[3]) and ch_place[3]<0) or
        (chpos[1]>(ch_place[2]+ch_place[4]) and ch_place[4]>0) or
        (chpos[1]<(ch_place[2]+ch_place[4]) and ch_place[4]<0)):
        if i_tree<len(tree1)-1:
            i_tree+=1
            passage=1
        else:
            passage=-1

def movearc():
    global chpos,ch_place,i_tree,passage,cha
    x0=ch_place[0]
    y0=ch_place[1]
    r=ch_place[2]-width/2 #effective radius
    sign=ch_place[3] #True or False
    ab=ch_place[4]*np.pi/180 #angle begin
    ae=ch_place[5]*np.pi/180 #angle end

    da=chv*clock.get_time()/r
    if not sign:
        da=-da

    if passage==1:
        passage=0
        cha=ab #cha - character's angle
    if passage==-1:
        passage=0
        cha=ae

    if event.type == pg.KEYDOWN:
        if event.key==pg.K_w:
            cha+=da
        if event.key==pg.K_s:
            cha-=da

    chpos=[x0+r*np.cos(cha),y0-r*np.sin(cha)]
    
    if ((cha>ae and sign) or (cha<ae and not sign)):
        if i_tree<len(tree1)-1:
            i_tree+=1
            passage=1
        else:
            passage=-1

    if (cha<ab and sign) or (cha>ab and (not sign)):
        if i_tree>1:
            i_tree-=1
            passage=-1
        else:
            passage=1

def myprint(x,y,number):
    font = pg.font.SysFont("comicsansms", 15)
    string=str(number)
    bitmap=font.render(string,False,white)
    DISPLAYSURF.blit(bitmap,(x,y))
    
    
				
	
#########################################################################################
alpha=45
width=15

chsize=9 #radius of character
chpos=[9,491] #start character position
chv=0.4 #character's speed
fallv=0.6

crdseed=(500,499) #coordinates of seed
tree1=((crdseed[0]-width/2,crdseed[1],width,True,0,0),) #"seed"
#xcenter,ycenter,radius,sign(True=+),angle_begin,_angle_end 

tuple_of_platforms=((0,600,0,False,'plt'),
                    (0,600,500,False,'plt'),
                    (0,500,0,True,'vrt'),
                    (0,500,600,True,'vrt'),
                    (250,370,370,False,'plt'))
					#xstart,xstop,y,if_vertical,plt=platform vrt=vertical

ch_place=tuple_of_platforms[1]
###########################################################################################


DISPLAYSURF.fill(black)

#draw platforms
for platform in tuple_of_platforms:
    if platform[3]:
        pg.draw.line(DISPLAYSURF,silver,(platform[2],platform[0]),
                     (platform[2],platform[1]),3)
    else:
        pg.draw.line(DISPLAYSURF,silver,(platform[0],platform[2]),
                     (platform[1],platform[2]),3)

#draw seed
#pointlist for seed
pst_seed=((crdseed[0]-2,crdseed[1]),(crdseed[0],crdseed[1]-10),(crdseed[0]+2,crdseed[1]))
pg.draw.polygon(DISPLAYSURF,gray,pst_seed,0)

pixarray=pg.surfarray.array2d(DISPLAYSURF) #remember background

#clock
clock = pg.time.Clock()

#font
#pg.font.init

i=0
phaseofgrowth=False
drawpos=[0,0]
passage=0
cha=0
leftright=[0,0]

while True: # main game loop

    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()


    pg.surfarray.blit_array(DISPLAYSURF,pixarray) #background

    if phaseofgrowth:
        tree1=tree_arc(tree1,leftright[0],leftright[1])
        pixarray=pg.surfarray.array2d(DISPLAYSURF)
        phaseofgrowth=False
    
    if not phaseofgrowth:
        drawpos[0]=int(round(chpos[0]))
        drawpos[1]=int(round(chpos[1]))
        pg.draw.circle(DISPLAYSURF,red,drawpos,chsize,0)

        #print tree state
        myprint(crdseed[0]-15,crdseed[1]-20,leftright[0])
        myprint(crdseed[0]+9,crdseed[1]-20,leftright[1])

        if ch_place[4]=='plt':
            flag_tree=moveplt()
        else:
            if flag_tree:
                i_tree=1
                passage=1
                flag_tree=False
            movetree()

        if event.type == pg.KEYDOWN:
            if event.key==pg.K_t:
                phaseofgrowth=True
                pg.time.wait(500)

        if (crdseed[0]-2*chsize)<chpos[0]<crdseed[0]:
            if crdseed[1]>chpos[1]>(crdseed[1]-2*chsize):
                if event.type == pg.KEYDOWN:
                    if event.key==pg.K_p:
                        leftright[0]+=1
                        pg.time.wait(500)
                    if event.key==pg.K_m and leftright[0]>0:
                        leftright[0]-=1
                        pg.time.wait(500)
      
        if crdseed[0]<chpos[0]<(crdseed[0]+2*chsize):
            if crdseed[1]>chpos[1]>(crdseed[1]-2*chsize):
                if event.type == pg.KEYDOWN:
                    if event.key==pg.K_p:
                        leftright[1]+=1
                        pg.time.wait(500)
                    if event.key==pg.K_m and leftright[0]>0:
                        leftright[1]-=1
                        pg.time.wait(500)

    pg.display.update()
    clock.tick()
