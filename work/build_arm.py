from __future__ import annotations
import sys, json, math, struct, zipfile, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work'/'cad-deps'))
import numpy as np
import manifold3d as md
import trimesh

OUT=ROOT
for sub in ['stl/gabarits','stl/structure','stl/coques','sources']:
    (OUT/sub).mkdir(parents=True,exist_ok=True)
SEG=64

def fmt(a):
    if isinstance(a,(list,tuple,np.ndarray)): return '['+','.join(fmt(i) for i in a)+']'
    return f'{float(a):.5f}'.rstrip('0').rstrip('.') or '0'

class S:
    def __init__(self,m,code): self.m,self.code=m,code
    def move(self,p):
        T=np.eye(4); T[:3,3]=p
        return self.tf(T)
    def tf(self,T):
        return S(self.m.transform(np.array(T)[:3,:].tolist()),'multmatrix('+fmt(T)+'){'+self.code+'}')
    def rot(self,xyz):
        return self.tf(rot(*xyz))

def rot(x=0,y=0,z=0):
    x,y,z=np.radians([x,y,z]); cx,cy,cz=np.cos([x,y,z]); sx,sy,sz=np.sin([x,y,z])
    R=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
    T=np.eye(4); T[:3,:3]=R; return T
def trans(x=0,y=0,z=0):
    T=np.eye(4);T[:3,3]=[x,y,z];return T
def box(d,p=(0,0,0)):
    return S(md.Manifold.cube(d,True),'cube('+fmt(d)+',center=true);').move(p)
def cyl(r,h,p=(0,0,0),r2=None,n=SEG):
    return S(md.Manifold.cylinder(h,r,r if r2 is None else r2,n,True),'cylinder(h='+fmt(h)+',r1='+fmt(r)+',r2='+fmt(r if r2 is None else r2)+',center=true,$fn='+str(n)+');').move(p)
def cy(r,h,p=(0,0,0),n=SEG): return cyl(r,h,n=n).rot((90,0,0)).move(p)
def sphere(r,p=(0,0,0)):
    return S(md.Manifold.sphere(r,SEG),'sphere(r='+fmt(r)+',$fn='+str(SEG)+');').move(p)
def ellipsoid(r,p=(0,0,0)):
    T=np.diag([*r,1.]);return sphere(1).tf(T).move(p)
def union(*ss):
    ss=[s for s in ss if s is not None]
    return S(md.Manifold.batch_boolean([s.m for s in ss],md.OpType.Add),'union(){'+''.join(s.code for s in ss)+'}')
def cut(a,*ss):
    return S(md.Manifold.batch_boolean([a.m]+[s.m for s in ss],md.OpType.Subtract),'difference(){'+a.code+''.join(s.code for s in ss)+'}')
def intersect(a,b):
    return S(md.Manifold.batch_boolean([a.m,b.m],md.OpType.Intersect),'intersection(){'+a.code+b.code+'}')
def hull(*ss):
    return S(md.Manifold.batch_hull([s.m for s in ss]),'hull(){'+''.join(s.code for s in ss)+'}')
def rbox(d,r,p=(0,0,0)):
    x,y,z=d
    return hull(*[cyl(r,z,(a*(x/2-r),b*(y/2-r),0),n=32) for a in [-1,1] for b in [-1,1]]).move(p)
def roundbox3(d,r,p=(0,0,0)):
    return hull(*[sphere(r,(a*(d[0]/2-r),b*(d[1]/2-r),c*(d[2]/2-r))) for a in [-1,1] for b in [-1,1] for c in [-1,1]]).move(p)
def slot_y(x,z,y=0,length=7,d=3.3,h=12,axis='x'):
    a=(length-d)/2
    return hull(cy(d/2,h,(x-a if axis=='x' else x,y,z-a if axis=='z' else z),n=24),cy(d/2,h,(x+a if axis=='x' else x,y,z+a if axis=='z' else z),n=24))

BIG={'name':'MG996R','l':40.7,'w':19.7,'depth':36.8,'off':10.3,'front':8.0,'ear':47.5,'ear_y':5,'mount_d':3.3,'plate':(61,30),'plate_z':-13,'back':-47,'side_y':32,'br':6.5,'bore':4.25,'foot':-38,'rise':31,'mass':55}
SMALL={'name':'MG90S','l':22.8,'w':12.2,'depth':23.0,'off':5.7,'front':5.5,'ear':27.8,'ear_y':0,'mount_d':2.3,'plate':(37,21),'plate_z':-9,'back':-31,'side_y':24,'br':5,'bore':3.25,'foot':-24,'rise':22,'mass':13.4}
PITCH=np.array([[0,1,0,0],[0,0,1,0],[1,0,0,0],[0,0,0,1]],float)
L1,L2=94.,76.
SERV_AXIS_Z=51.
YAW_Z=70.
SHOULDER_Z=112.
ROLL_Z=35.
ROLL_Y=14.
PINCH_Z=23.
TARGET_LOAD_G=20.
ELEC_H=40.
UNO_HOLES=[(13.97,2.54),(66.04,7.62),(66.04,35.56)]
LID_BOLTS=[(62*np.cos(np.radians(a)),62*np.sin(np.radians(a))) for a in [45,135,225,315]]
PANEL=trans(48,-48,-22)@rot(z=45)

def uno_xy(x,y): return 26.7-y,-56+x

def slot_z(x,y,z,length=4.5,d=2.8,h=15):
    return hull(cyl(d/2,h,(x,y-(length-d)/2,z),n=24),cyl(d/2,h,(x,y+(length-d)/2,z),n=24))

def body_void(p,extra=.35,depth_extra=0):
    # Axis is +Z. Output axis at the origin; long body dimension along X.
    cx=p['off']-p['l']/2
    return box((p['l']+2*extra,p['w']+2*extra,p['depth']+2*extra+depth_extra),(cx,0,-p['front']-p['depth']/2-depth_extra/2))

def servo_visual(p):
    cx=p['off']-p['l']/2
    b=box((p['l'],p['w'],p['depth']),(cx,0,-p['front']-p['depth']/2))
    ears=box((p['ear']+6,p['w'],2.5),(cx,0,p['plate_z']+3))
    tower=cyl(p['w']/2-1,p['front']-1,(0,0,-p['front']/2-1))
    shaft=cyl(3 if p==BIG else 2.4,4,(0,0,0))
    return union(b,ears,tower,shaft)

def servo_cradle(p):
    cx=p['off']-p['l']/2
    px,py=p['plate']; fz=p['plate_z']
    face=rbox((px,py,3.4),py/2-.5,(cx,0,fz))
    face=cut(face,box((p['l']+.7,p['w']+.7,8),(cx,0,fz)))
    holes=[]
    for sx in [-1,1]:
        xx=cx+sx*p['ear']/2
        for yy in ([-p['ear_y'],p['ear_y']] if p['ear_y'] else [0]):
            holes.append(hull(cyl(p['mount_d']/2,9,(xx-1.5,yy,fz),n=24),cyl(p['mount_d']/2,9,(xx+1.5,yy,fz),n=24)))
    face=cut(face,*holes)
    back=p['back']; mid=(back+fz)/2; height=fz-back+2
    rails=union(*[box((p['l']+6,2.8,height),(cx,sy*(p['w']/2+2.25),mid)) for sy in [-1,1]])
    stop=rbox((p['l']+6,p['w']+7,3),2,(cx,0,back))
    stop=cut(stop,box((p['l']-8,p['w']-3,7),(cx,0,back)),box((8,7,10),(cx-p['l']/2+2,0,back+1)))
    # Discrete internal M3 skin attachment pads, outside motor cavity.
    return union(face,rails,stop)

def static_pitch(p):
    holder=servo_cradle(p).tf(PITCH)
    sy=p['side_y']; foot=p['foot']; br=p['br']
    support=hull(cy(br+4.2,6.2,(0,sy,0)),cy(br+3,6.2,(0,sy,foot+4)))
    seat=cy(br+.12,5.2,(0,sy-.6,0))
    support=cut(support,seat,cy(p['bore']/2,12,(0,sy,0)))
    # Hollow bottom bridge keeps positive connection while reducing carried mass.
    span=sy-p['back']+4
    bridge=box((p['w']+8,span,4),(0,(sy+p['back'])/2,foot))
    bridge=cut(bridge,box((p['w']-2,span-16,8),(0,(sy+p['back'])/2,foot)))
    # Two feet remain connected to the yoke bridge and cradle rails.
    bridge=union(bridge,box((p['w']+8,12,6),(0,p['back']+3,foot)),box((p['w']+8,11,6),(0,sy-2,foot)))
    return cut(union(holder,support,bridge),servo_visual(p).tf(PITCH))

def horn_holes(p,yy=5.5):
    # Slotted M2 attachments to the supplied horn; no printed servo spline.
    rad=8.2 if p==BIG else 5.8
    hole=cy(2.35,12,(0,yy,0))
    return [hole]+[slot_y(sx*rad,0,yy,length=5.2,d=2.25,h=12) for sx in [-1,1]]

def moving_fork(p):
    dy,ry=5.5,p['side_y']-6.5
    rise=p['rise']; rr=15 if p==BIG else 10.5
    left=hull(cy(rr,4,(0,dy,0)),cy(8 if p==BIG else 6,4,(0,dy,rise)))
    left=cut(left,*horn_holes(p,dy))
    right=hull(cy(p['br']+3,4,(0,ry,0)),cy(7,4,(0,ry,rise)))
    right=cut(right,cy(p['bore']/2,10,(0,ry,0)))
    bridge=box((16 if p==BIG else 13,ry-dy+4,5),(0,(ry+dy)/2,rise-1))
    return union(left,right,bridge)

def link(p_in,p_out,L):
    fork=moving_fork(p_in)
    a=p_in['rise']-1; b=L+p_out['foot']+1
    ym=(5.5+p_in['side_y']-6.5)/2
    # Two longitudinal spars leave a central cable opening.
    if b>a:
        spars=union(*[box((4.2,18,b-a+5),(sx*7.3,ym,(a+b)/2)) for sx in [-1,1]])
    else: spars=box((18,18,6),(0,ym,a))
    distal=static_pitch(p_out).move((0,0,L))
    s=union(fork,spars,distal)
    # Do not allow an upstream spar to enter a distal motor insertion volume.
    s=cut(s,body_void(p_out,.4,2).tf(PITCH).move((0,0,L)))
    # Elastic/spring attachment provision, to be tuned after physical balancing.
    tab=cy(4.7,5,(-13,ym,p_in['rise']+3))
    tab=union(tab,box((9,5,8),(-9,ym,p_in['rise']+3)))
    tab=cut(tab,cy(1.65,12,(-13,ym,p_in['rise']+3)))
    return union(s,tab)

def large_cap():
    # Rear service shell, open towards the horn. Only enclosure geometry is nominal.
    outer=hull(cy(34,46,(0,-30,-13)),cy(34,46,(0,-30,0)))
    inner=hull(cy(31.8,47,(0,-26.7,-13)),cy(31.8,47,(0,-26.7,0)))
    cap=cut(outer,inner,box((110,80,130),(0,32,-5)))
    cap=cut(cap,box((10,30,11),(0,-49,-27)))
    for zz in [-18,18]:cap=cut(cap,cy(.9,8,(0,-52,zz),n=24))
    return cap

def small_cap():
    outer=hull(cy(22,32,(0,-20,-5)),cy(22,32,(0,-20,0)))
    inner=hull(cy(19.8,33,(0,-17.1,-5)),cy(19.8,33,(0,-17.1,0)))
    return cut(outer,inner,box((100,60,100),(0,26,0)),box((100,100,100),(0,0,-74)))

def round_face():
    s=union(cy(26,1.8,(0,-56.1,0)),cy(24.5,2.5,(0,-54.1,0)))
    for zz in [-18,18]:s=cut(s,cy(1.1,10,(0,-55,zz),n=24))
    return s

def trim_ring():return cut(cy(29,2,(0,-54,0)),cy(24.8,6,(0,-54,0)))

def link_skin(p_in,p_out,L):
    ym=(5.5+p_in['side_y']-6.5)/2
    a=20; b=L-28
    if b<a+6: b=a+6
    # Rounded tapered arm covers, split on Y for easy flat-bed printing.
    out=hull(ellipsoid((23,23,8),(0,ym,a)),ellipsoid((19,19,8),(0,ym,b)))
    inn=hull(ellipsoid((20.7,20.7,9),(0,ym,a)),ellipsoid((16.7,16.7,9),(0,ym,b)))
    s=cut(out,inn,box((100,100,20),(0,ym,a-15)),box((100,100,20),(0,ym,b+15)))
    # Clip around actual distal cradle and fork with clearance.
    return s

def split_axis(s,axis=0,value=0):
    a=[0,0,0]; b=[0,0,0]; a[axis]=value+150; b[axis]=value-150
    d=[600,600,600];d[axis]=300
    return intersect(s,box(d,a)),intersect(s,box(d,b))

def seam_lugs(s,axis,positions):
    lugs=[];holes=[]
    for pos in positions:
        dims=(10,5,8) if axis==0 else (5,8,8)
        lugs.append(rbox(dims,1,pos))
        if axis==0:
            holes.append(cyl(1.15,16,n=24).rot((0,90,0)).move(pos))
            holes.append(cyl(2.45,2,n=6).rot((0,90,0)).move((pos[0]-4.4,pos[1],pos[2])))
        else:
            holes.append(cy(1.15,15,pos,n=24))
            holes.append(cy(2.45,2,(pos[0],pos[1]-3.4,pos[2]),n=6))
    return cut(union(s,*lugs),*holes)

def base_fixed():
    floor=cyl(58,5,(0,0,2.5),r2=56)
    wall=cut(cyl(55,47,(0,0,28.5),r2=51),cyl(51.8,49,(0,0,29),r2=48))
    cradle=servo_cradle(BIG).move((0,0,SERV_AXIS_Z))
    mounts=[]; holes=[]
    for a in [45,135,225,315]:
        x,y=42*np.cos(np.radians(a)),42*np.sin(np.radians(a))
        mounts.append(cyl(4.8,52,(x,y,30),n=32))
        holes.append(cyl(1.5,20,(x,y,47),n=24))
    s=union(floor,wall,cradle,*mounts)
    s=cut(s,*holes,box((18,30,9),(-47,0,9)))
    for a in [0,90,180,270]:
        x,y=48*np.cos(np.radians(a)),48*np.sin(np.radians(a))
        s=cut(s,cyl(2.3,12,(x,y,3),n=24))
    # Off-axis feed-through into the separate lower electronics compartment.
    s=cut(s,rbox((14,9,14),2,(-40,-18,3)))
    return s

def electronics_case():
    # Fixed load path: wall -> annular upper seat -> original mechanical base.
    wall=cut(cyl(70,37,(0,0,-18.5)),cyl(66.8,42,(0,0,-18.5)))
    seat=cut(cyl(70,3,(0,0,-1.5)),cyl(54.5,8,(0,0,-1.5)))
    bosses=[];holes=[];feet=[]
    for angle in [0,90,180,270]:
        rad=np.radians(angle);x,y=48*np.cos(rad),48*np.sin(rad)
        bosses.append(cyl(5.7,10,(x,y,-5),n=32))
        bosses.append(box((19,9,7),(57,0,-3.5)).rot((0,0,angle)))
        holes.append(cyl(2.3,18,(x,y,-5),n=24))
        # External mounting lugs remain reachable after the lower tray is closed.
        foot=union(cyl(6,6,(77,0,-37),n=32),box((15,10,4),(71.5,0,-35)))
        foot=cut(foot,cyl(2.3,12,(77,0,-37),n=24))
        feet.append(foot.rot((0,0,angle)))
    for x,y in LID_BOLTS:
        bosses.append(cyl(5.6,9,(x,y,-32.5),n=32))
        holes.extend([cyl(1.7,15,(x,y,-33),n=24),cyl(3.35,3.6,(x,y,-29.5),n=6)])
    s=cut(union(wall,seat,*bosses,*feet),*holes)
    # Recessed direct USB access. Dimensions are a clearance provision, not a socket standard.
    s=cut(s,rbox((30,32,21),2,(-12,-66,-23.5)))
    # Rear-right replaceable connector panel, tangent to the circular enclosure.
    frame=union(box((48,5,30),(0,1.8,0)),*[cy(5,8,(x,3,0),n=32) for x in [-17,17]])
    s=union(s,frame.tf(PANEL))
    s=cut(s,box((52,20,31),(0,-10.7,0)).tf(PANEL),box((28,28,17),(0,0,0)).tf(PANEL))
    for x in [-17,17]:
        s=cut(s,cy(1.7,22,(x,1,0),n=24).tf(PANEL),cy(3.35,4,(x,5.2,0),n=6).tf(PANEL))
    for x in [-28,-14,0,14,28]:
        for z in [-22,-16]:s=cut(s,box((8,32,2.2),(x,65,z)))
    return s

def electronics_tray():
    floor=cyl(70,3,(0,0,-38.5))
    lip=cut(cyl(66.5,2.2,(0,0,-36)),cyl(65.1,5,(0,0,-36)))
    lip=cut(lip,*[cyl(6,7,(x,y,-36)) for x,y in LID_BOLTS])
    lip=cut(lip,*[box((18,14,8),(70,0,-36)).rot((0,0,a)) for a in [0,90,180,270]])
    lip=cut(lip,box((52,14,10),(0,2,-14)).tf(PANEL))
    s=union(floor,lip)
    for x,y in LID_BOLTS:
        s=cut(s,cyl(1.7,15,(x,y,-37),n=24),cyl(3.1,1.5,(x,y,-39.35),n=32))
    for ux,uy in UNO_HOLES:
        x,y=uno_xy(ux,uy)
        boss=hull(cyl(2.9,6.2,(x,y-.85,-34.1),n=24),cyl(2.9,6.2,(x,y+.85,-34.1),n=24))
        s=union(s,boss)
        s=cut(s,slot_z(x,y,-35),slot_z(x,y,-39.25,length=6.5,d=5.2,h=1.6))
    # Tie-down slots straddle a nominal 60 x 22 mm distribution/fuse zone.
    for x in [-24,24]:
        for y in [17,47]:s=cut(s,rbox((9,3,8),1,(x,y,-38)))
    anchor=rbox((10,6,4),1,(-42,-9,-35.1))
    anchor=cut(anchor,box((5,12,2),(-42,-9,-34.6)))
    return union(s,anchor)

def electronics_panel():
    s=rbox((42,2.4,25),1.1,(0,-2.15,0))
    for x in [-17,17]:s=cut(s,cy(1.7,12,(x,-2,0),n=24))
    s=cut(s,cy(4,12,(-8,-2,0),n=32))
    return s

def electronics_references():
    # Nominal placement references, deliberately not distributed as printable parts.
    pcb=box((53.4,68.6,1.6),(0,-21.7,-30.2))
    for ux,uy in UNO_HOLES+[(15.24,50.8)]:
        x,y=uno_xy(ux,uy);pcb=cut(pcb,cyl(1.6,6,(x,y,-30.2),n=24))
    components=union(box((12,16,10.8),(-12,-54,-24)),box((9,14,11),(18,-50,-23.9)),box((8,34,5),(5,-15,-26.9)),*[box((2.6,47,9),(x,-15,-24.9)) for x in [-24,24]])
    return [('E01_Uno_circuit','Arduino Uno R3 · contour nominal','pcb',pcb),('E02_Uno_composants','Connecteurs et composants Uno · volumes simplifiés','metal',components),('E03_zone_alimentation','Réserve distribution / fusible 60 × 22 × 16 mm · à adapter','zone',box((60,22,16),(0,32,-23))),('E04_fiche_USB','Fiche USB · enveloppe de dégagement 14 × 22 × 13 mm','servo',box((14,22,13),(-12,-73,-24))) ]

def yaw_support():
    disk=cut(cyl(50,4,(0,0,58)),cyl(19,14,(0,0,58)))
    ring=cut(cyl(15,9,(0,0,62.5)),cyl(11.1,7.3,(0,0,63.5)),cyl(9.6,20,(0,0,63)))
    spokes=union(*[box((31,7,4),(a*29,0,60.5)) for a in [-1,1]],*[box((7,31,4),(0,a*29,60.5)) for a in [-1,1]])
    disk=union(disk,spokes,ring)
    for a in [45,135,225,315]:
        x,y=42*np.cos(np.radians(a)),42*np.sin(np.radians(a))
        disk=cut(disk,cyl(1.7,16,(x,y,58),n=24))
    return disk

def yaw_drive():
    plate=cyl(17,5,(0,0,55.5))
    neck=cyl(3.94,13,(0,0,63.5))
    spacer=cyl(5.2,3,(0,0,68.5))
    key=intersect(cyl(3.94,7,(0,0,73.5)),box((6.3,12,10),(0,0,73.5)))
    s=union(plate,neck,spacer,key)
    holes=[cyl(2.2,35,(0,0,65)),cyl(4.18,4.4,(0,0,54.8),n=6)]
    for sx in [-1,1]:
        holes.append(hull(cyl(1.13,12,(sx*7.5,0,55),n=24),cyl(1.13,12,(sx*11,0,55),n=24)))
    return cut(s,*holes)

def turret():
    disk=cyl(34,6,(0,0,73))
    key=intersect(cyl(4.08,14,(0,0,73)),box((6.65,12,14),(0,0,73)))
    disk=cut(disk,key)
    support=static_pitch(BIG).move((0,0,SHOULDER_Z))
    anchor=hull(cy(5,5,(0,32,10+SHOULDER_Z)),cy(5,5,(-25,32,25+SHOULDER_Z)))
    anchor=cut(anchor,cy(1.65,12,(-25,32,25+SHOULDER_Z),n=24))
    return cut(union(disk,support,anchor),servo_visual(BIG).tf(PITCH).move((0,0,SHOULDER_Z)))

def wrist_pitch():
    fork=moving_fork(SMALL)
    cr=servo_cradle(SMALL).move((0,ROLL_Y,ROLL_Z))
    part=union(fork,cr,box((20,19,7),(0,ROLL_Y,18)))
    return cut(part,servo_visual(SMALL).move((0,ROLL_Y,ROLL_Z)),box((200,100,200),(0,70.2,0)))

def wrist_roll_gripper():
    root=cyl(12,4,(0,0,5))
    root=cut(root,cyl(2.3,12,(0,0,5)))
    for sx in [-1,1]: root=cut(root,hull(cyl(1.13,12,(sx*4.6,0,5),n=24),cyl(1.13,12,(sx*7.6,0,5),n=24)))
    d=9.18
    holder=servo_cradle(SMALL).tf(PITCH).move((-d,0,PINCH_Z))
    back=box((43,29,4),(0,-9,8))
    bridge=box((43,8,6),(0,-2,13))
    bearing=cut(cy(8.2,5,(d,-1,PINCH_Z)),cy(5.12,4.2,(d,-1.5,PINCH_Z)),cy(1.65,12,(d,-1,PINCH_Z)))
    stand=box((9,5,14),(d,-1,17))
    result=union(root,back,bridge,holder,bearing,stand)
    return cut(result,servo_visual(SMALL).tf(PITCH).move((-d,0,PINCH_Z)))

def gear2d(teeth=18,module=1.,phase=0):
    # Polygonal involute spur gear, 20 degree pressure angle, backlash .12 mm per flank.
    rp=teeth*module/2; rb=rp*math.cos(math.radians(20)); ra=rp+module; rf=rp-1.25*module
    half=math.pi/(2*teeth)-.12/(2*rp)
    invp=math.tan(math.acos(rb/rp))-math.acos(rb/rp)
    def inv(r):
        if r<=rb:return 0.
        a=math.acos(rb/r);return math.tan(a)-a
    pts=[]
    for k in range(teeth):
        c=k*2*math.pi/teeth+phase
        pts.append((rf*math.cos(c-math.pi/teeth),rf*math.sin(c-math.pi/teeth)))
        for r in np.linspace(max(rb,rf),ra,5):
            a=c-half-invp+inv(r);pts.append((r*math.cos(a),r*math.sin(a)))
        for r in np.linspace(ra,max(rb,rf),5):
            a=c+half+invp-inv(r);pts.append((r*math.cos(a),r*math.sin(a)))
        pts.append((rf*math.cos(c+math.pi/teeth),rf*math.sin(c+math.pi/teeth)))
    # CCW section normal along Z.
    return pts

def finger(right=False):
    poly=gear2d(phase=math.pi/18 if right else 0)
    sec=md.CrossSection([poly])
    m=sec.extrude(3.5).translate((0,0,-1.75))
    raw=S(m,'linear_extrude(height=3.5,center=true)polygon('+fmt(poly)+');').rot((90,0,0)).move((0,5.5,0))
    sgn=-1 if right else 1
    arm=hull(cy(4,3.5,(sgn*1,5.5,8)),cy(3,3.5,(sgn*5.0,5.5,29)))
    pad=rbox((6,6,9),1,(sgn*6.0,5.5,30))
    s=union(raw,arm,pad)
    s=cut(s,cy(1.65 if right else 2.25,12,(0,5.5,0)))
    if not right:
        s=cut(s,slot_y(0,5.6,5.5,length=4.8,d=2.2,h=12,axis='z'),slot_y(0,-5.6,5.5,length=4.8,d=2.2,h=12,axis='z'))
    return s

def wrist_skin():
    out=roundbox3((47,22.2,41),7,(-5.5,9.1,16.5))
    inn=roundbox3((42.6,25,42),4.8,(-5.5,13,16.5))
    s=cut(out,inn,cy(8,14,(0,-2,0)))
    return s

def gripper_skin():
    out=roundbox3((48,40,37),7,(0,-14,18))
    inn=roundbox3((43.6,35.6,38),4.8,(0,-14,18))
    return cut(out,inn,box((100,40,100),(0,23,18)),box((100,100,100),(0,0,-42)))

PARTS=[]; SCENE=[]; SERVO_SCENE=[]
def mesh(s):
    mm=s.m.simplify(.005).to_mesh64();return trimesh.Trimesh(vertices=np.asarray(mm.vert_properties)[:,:3],faces=np.asarray(mm.tri_verts),process=True)
def add(name,label,s,group='structure',color='dark',owner='base',print_rot=(0,0,0),split_print_axis=None):
    # Mesh is validated before print export. The assembled CAD keeps original coordinates.
    mm=mesh(s)
    T=rot(*print_rot)
    pp=mm.copy(); pp.apply_transform(T)
    pp.apply_translation(-np.array([*pp.bounds[0][:2],pp.bounds[0][2]]))
    path=OUT/'stl'/group/(name+'.stl'); pp.export(path)
    stat={'id':name,'designation':label,'groupe':group,'couleur':color,'volume_cm3':round(abs(mm.volume)/1000,3),'masse_pleine_PLA_g':round(abs(mm.volume)/1000*1.24,2),'dimensions_impression_mm':np.round(pp.extents,2).tolist(),'ferme':bool(mm.is_watertight),'volume_positif':bool(mm.volume>0),'owner':owner,'orientation_deg':list(print_rot),'s':s,'mesh':mm}
    PARTS.append(stat)
    return name
def place(part,owner,local=np.eye(4)):
    SCENE.append({'part':part,'owner':owner,'local':local})

def build():
    # Fit coupons are the first and only parts recommended for immediate printing.
    for p in [BIG,SMALL]:
        cx=p['off']-p['l']/2
        for clearance in [.2,.35,.5]:
            test=rbox((p['plate'][0],p['plate'][1],3.4),2,(cx,0,0))
            test=cut(test,box((p['l']+2*clearance,p['w']+2*clearance,9),(cx,0,0)))
            for sx in [-1,1]:
                xx=cx+sx*p['ear']/2
                for yy in ([-p['ear_y'],p['ear_y']] if p['ear_y'] else [0]):
                    test=cut(test,hull(cyl(p['mount_d']/2,9,(xx-1.5,yy,0),n=24),cyl(p['mount_d']/2,9,(xx+1.5,yy,0),n=24)))
            add('G_'+p['name']+'_jeu_'+str(clearance).replace('.','p'),f"Gabarit {p['name']}, jeu {clearance:.2f} mm par côté",test,'gabarits','white')
    # A small bed-level coupon tests the bearing seats without printing an assembly.
    coupon=rbox((50,25,6.2),3)
    coupon=cut(coupon,cyl(6.62,9,(-13,0,0)),cyl(5.12,9,(11,0,0)))
    add('G_paliers_624_623','Gabarit logements 624ZZ et 623ZZ',coupon,'gabarits','dark')

    add('S01_socle','Socle fixe et berceau du moteur de base',base_fixed(),color='white');place('S01_socle','base')
    add('S02_support_palier_base','Support démontable du roulement 608ZZ',yaw_support(),print_rot=(180,0,0));place('S02_support_palier_base','base')
    add('S03_entraineur_base','Entraîneur à méplats, écrou M4 et palonnier',yaw_drive());place('S03_entraineur_base','yaw')
    add('S04_tourelle_epaule','Tourelle et berceau de l’épaule',turret(),owner='yaw',print_rot=(90,0,0));place('S04_tourelle_epaule','yaw')
    add('S05_bras','Bras supérieur avec berceau du coude',link(BIG,BIG,L1),owner='upper',print_rot=(90,0,0));place('S05_bras','upper')
    add('S06_avant_bras','Avant-bras avec berceau du poignet',link(BIG,SMALL,L2),owner='forearm',print_rot=(90,0,0));place('S06_avant_bras','forearm')
    add('S07_poignet_inclinaison','Fourche du poignet et berceau de rotation',wrist_pitch(),owner='wrist',print_rot=(90,0,0));place('S07_poignet_inclinaison','wrist')
    add('S08_poignet_rotation_pince','Plateau de rotation et support de pince',wrist_roll_gripper(),owner='roll',print_rot=(90,0,0));place('S08_poignet_rotation_pince','roll')
    add('S09_doigt_menant','Doigt menant avec roue dentée',finger(False),owner='finger_l',print_rot=(90,0,0));place('S09_doigt_menant','finger_l')
    add('S10_doigt_mene','Doigt entraîné avec roue dentée',finger(True),owner='finger_r',print_rot=(90,0,0));place('S10_doigt_mene','finger_r')
    add('S11_boitier_electronique','Boîtier fixe inférieur et pattes de fixation',electronics_case(),color='white',print_rot=(180,0,0));place('S11_boitier_electronique','base')
    add('S12_fond_electronique','Fond démontable avec supports Uno et passages de colliers',electronics_tray());place('S12_fond_electronique','base')
    add('S13_platine_arriere','Platine amovible pour câble et futur interrupteur',electronics_panel(),print_rot=(90,0,0));place('S13_platine_arriere','base',PANEL)

    # Service shells: split and printable individually, 2.1–2.2 mm nominal wall.
    for number,owner,L,pin,pout in [(1,'upper',L1,BIG,BIG),(2,'forearm',L2,BIG,SMALL)]:
        skin=link_skin(pin,pout,L);ym=(5.5+pin['side_y']-6.5)/2
        skin=seam_lugs(skin,1,[(sx*20.5,ym,(20+L-28)/2) for sx in [-1,1]])
        aa,bb=split_axis(skin,1,ym)
        for suffix,ss,rr in [('avant',aa,(90,0,0)),('arriere',bb,(-90,0,0))]:
            ident=f'C{number:02d}_{suffix}'
            add(ident,'Demi-coque '+('bras' if number==1 else 'avant-bras')+' '+suffix,ss,'coques','white',owner,rr);place(ident,owner)
    cap=large_cap()
    for number,owner,offset in [(3,'yaw',trans(0,0,SHOULDER_Z)),(4,'upper',trans(0,0,L1))]:
        use_cap=cut(cap,box((160,160,100),(0,0,-85))) if number==3 else cap
        use_cap=seam_lugs(use_cap,0,[(0,-50.2,zz) for zz in [-24,15]])
        aa,bb=split_axis(use_cap,0,0)
        for suffix,ss,rr in [('gauche',aa,(0,-90,0)),('droite',bb,(0,90,0))]:
            ident=f'C{number:02d}_{suffix}'
            add(ident,'Demi-coque '+('épaule' if number==3 else 'coude')+' '+suffix,ss,'coques','white',owner,rr);place(ident,owner,offset)
    for number,owner,s in [(5,'wrist',wrist_skin()),(6,'roll',gripper_skin())]:
        s=seam_lugs(s,0,[(0,-.5,zz) for zz in [11,27]]) if number==5 else seam_lugs(s,0,[(0,-32.7,zz) for zz in [15,28]])
        aa,bb=split_axis(s,0,0)
        for suffix,ss,rr in [('gauche',aa,(0,-90,0)),('droite',bb,(0,90,0))]:
            ident=f'C{number:02d}_{suffix}'
            add(ident,'Demi-coque '+('poignet' if number==5 else 'pince')+' '+suffix,ss,'coques','white',owner,rr);place(ident,owner)
    for number,owner,T in [(7,'yaw',trans(0,0,SHOULDER_Z)),(8,'upper',trans(0,0,L1))]:
        ident=f'C{number:02d}_cache_rond'
        add(ident,'Cache circulaire '+('épaule' if number==7 else 'coude'),round_face(),'coques','white',owner,(90,0,0));place(ident,owner,T)
        ident=f'C{number:02d}_bague'
        add(ident,'Bague sombre '+('épaule' if number==7 else 'coude'),trim_ring(),'coques','dark',owner,(90,0,0));place(ident,owner,T)
    aa,bb=split_axis(seam_lugs(small_cap(),0,[(0,-35.1,zz) for zz in [-12,10]]),0,0)
    for suffix,ss,rr in [('gauche',aa,(0,-90,0)),('droite',bb,(0,90,0))]:
        ident='C09_articulation_poignet_'+suffix
        add(ident,'Demi-coque articulation du poignet '+suffix,ss,'coques','white','forearm',rr);place(ident,'forearm',trans(0,0,L2))

def frames(angles=None):
    q=angles or [0,25,45,100,0,18]
    base=trans(0,0,ELEC_H); yaw=base@rot(z=q[0])
    upper=yaw@trans(0,0,SHOULDER_Z)@rot(y=q[1])
    forearm=upper@trans(0,0,L1)@rot(y=q[2])
    wrist=forearm@trans(0,0,L2)@rot(y=q[3])
    roll=wrist@trans(0,ROLL_Y,ROLL_Z)@rot(z=q[4])
    fl=roll@trans(-9.18,0,PINCH_Z)@rot(y=-q[5])
    fr=roll@trans(9.18,0,PINCH_Z)@rot(y=q[5])
    return {'base':base,'yaw':yaw,'upper':upper,'forearm':forearm,'wrist':wrist,'roll':roll,'finger_l':fl,'finger_r':fr}

def hardware():
    defs=[('M1',BIG,'base',trans(0,0,SERV_AXIS_Z)),('M2',BIG,'yaw',trans(0,0,SHOULDER_Z)@PITCH),('M3',BIG,'upper',trans(0,0,L1)@PITCH),('M4',SMALL,'forearm',trans(0,0,L2)@PITCH),('M5',SMALL,'wrist',trans(0,ROLL_Y,ROLL_Z)),('M6',SMALL,'roll',trans(-9.18,0,PINCH_Z)@PITCH)]
    for name,p,owner,T in defs:
        SERVO_SCENE.append({'id':name,'type':p['name'],'owner':owner,'local':T,'shape':servo_visual(p),'mass':p['mass']})
    return defs

def cleanup_shell_clearance():
    lookup={p['id']:p for p in PARTS}
    scene_by={r['part']:r for r in SCENE}
    originals={p['id']:p['s'] for p in PARTS}
    for p in PARTS:
        if p['groupe']!='coques' or p['id'].endswith('_bague') or p['id'].endswith('_cache_rond'):continue
        rec=scene_by[p['id']]; inv=np.linalg.inv(rec['local']); obstacles=[]
        for other in SCENE:
            if other['owner']==rec['owner'] and other['part'].startswith('S'):
                obstacles.append(originals[other['part']].tf(inv@other['local']))
        for other in SERVO_SCENE:
            if other['owner']==rec['owner']:
                obstacles.append(other['shape'].tf(inv@other['local']))
        if p['id'].startswith(('C03_','C04_')):
            num='C07_cache_rond' if p['id'].startswith('C03_') else 'C08_cache_rond'
            other=scene_by[num];obstacles.append(originals[num].tf(inv@other['local']))
        if not obstacles:continue
        raw=union(*obstacles)
        expanded=union(raw,*[raw.move(v) for v in [(.25,0,0),(-.25,0,0),(0,.25,0),(0,-.25,0),(0,0,.25),(0,0,-.25)]])
        s=cut(p['s'],expanded);mm=mesh(s)
        p['s']=s;p['mesh']=mm;p['ferme']=bool(mm.is_watertight);p['volume_positif']=bool(mm.volume>0)
        p['volume_cm3']=round(abs(mm.volume)/1000,3);p['masse_pleine_PLA_g']=round(abs(mm.volume)/1000*1.24,2)
        pp=mm.copy();pp.apply_transform(rot(*p['orientation_deg']));pp.apply_translation(-pp.bounds[0]);p['dimensions_impression_mm']=np.round(pp.extents,2).tolist()
        pp.export(OUT/'stl'/'coques'/(p['id']+'.stl'))

def export_all():
    frame=frames(); lookup={p['id']:p for p in PARTS}
    entries=[]; assembly=[]
    for rec in SCENE:
        p=lookup[rec['part']];T=frame[rec['owner']]@rec['local']
        mm=p['mesh'].copy();mm.apply_transform(T);assembly.append(mm)
        entries.append({'id':p['id'],'label':p['designation'],'kind':'print','color':p['couleur'],'owner':rec['owner'],'matrix':np.round(rec['local'],6).reshape(-1).tolist(),'positions':np.round(p['mesh'].vertices,4).astype(float).reshape(-1).tolist(),'indices':p['mesh'].faces.astype(int).reshape(-1).tolist()})
    for rec in SERVO_SCENE:
        mm=mesh(rec['shape']);T=frame[rec['owner']]@rec['local'];show=mm.copy();show.apply_transform(T);assembly.append(show)
        entries.append({'id':rec['id'],'label':rec['id']+' · '+rec['type'],'kind':'servo','color':'servo','owner':rec['owner'],'matrix':np.round(rec['local'],6).reshape(-1).tolist(),'positions':np.round(mm.vertices,4).astype(float).reshape(-1).tolist(),'indices':mm.faces.astype(int).reshape(-1).tolist()})
    for name,label,color,s in electronics_references():
        mm=mesh(s);show=mm.copy();show.apply_transform(frame['base']);assembly.append(show)
        entries.append({'id':name,'label':label,'kind':'electronics','color':color,'owner':'base','matrix':np.eye(4).reshape(-1).tolist(),'positions':np.round(mm.vertices,4).astype(float).reshape(-1).tolist(),'indices':mm.faces.astype(int).reshape(-1).tolist()})
    # Real bearings, visual reference only, not printable meshes.
    bearing_defs=[('R1_608ZZ','base',trans(0,0,63.5),11,4,7),('R2_624ZZ','yaw',trans(0,BIG['side_y']-.6,SHOULDER_Z)@rot(90,0,0),6.5,2,5),('R3_624ZZ','upper',trans(0,BIG['side_y']-.6,L1)@rot(90,0,0),6.5,2,5),('R4_623ZZ','forearm',trans(0,SMALL['side_y']-.6,L2)@rot(90,0,0),5,1.5,4),('R5_623ZZ','roll',trans(9.18,-1.5,PINCH_Z)@rot(90,0,0),5,1.5,4)]
    for name,owner,T,ro,ri,h in bearing_defs:
        s=cut(cyl(ro,h),cyl(ri,h+2));mm=mesh(s)
        entries.append({'id':name,'label':name.replace('_',' · '),'kind':'bearing','color':'metal','owner':owner,'matrix':T.reshape(-1).tolist(),'positions':np.round(mm.vertices,4).astype(float).reshape(-1).tolist(),'indices':mm.faces.astype(int).reshape(-1).tolist()})
    (ROOT/'work'/'scene.json').write_text(json.dumps(entries,separators=(',',':')),encoding='utf-8')
    trimesh.util.concatenate(assembly).export(OUT/'assemblage_visuel_NE_PAS_IMPRIMER.stl')
    public=[{k:v for k,v in p.items() if k not in ['s','mesh']} for p in PARTS]
    (OUT/'nomenclature_pieces.json').write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding='utf-8')
    scad=['// ORBITE V0.2 — prototype non valide sur materiel. Unites : mm.\n// A1 mini : 180 x 180 x 180. Imprimer les gabarits avant toute structure.\n// Les coques sont des propositions de forme : fixation et collisions a finaliser.\npiece="assemblage"; // remplacer par un identifiant Sxx / Cxx / G_xxx\n$fn=64;\n']
    for p in PARTS: scad.append('module '+p['id']+'(){'+p['s'].code+'}\n')
    scad.append('if(piece=="assemblage"){\n')
    for rec in SCENE:
        p=lookup[rec['part']];T=frame[rec['owner']]@rec['local'];col='[0.86,0.87,0.87]' if p['couleur']=='white' else '[0.09,0.105,0.12]'
        scad.append('color('+col+')multmatrix('+fmt(T)+')'+p['id']+'();\n')
    for rec in SERVO_SCENE: scad.append('color([0.18,0.19,0.20])multmatrix('+fmt(frame[rec['owner']]@rec['local'])+'){'+rec['shape'].code+'}\n')
    for name,label,color,s in electronics_references():scad.append('// '+label+' — reference non imprimable\ncolor([0.1,0.3,0.45])multmatrix('+fmt(frame['base'])+'){'+s.code+'}\n')
    scad.append('}\n')
    for p in PARTS:
        # Export orientation matches the distributed individual STL.
        T=rot(*p['orientation_deg']);mm=p['mesh'].copy();mm.apply_transform(T);b=mm.bounds[0]
        scad.append('if(piece=="'+p['id']+'")translate('+fmt(-b)+')multmatrix('+fmt(T)+')'+p['id']+'();\n')
    (OUT/'sources'/'orbite_v0.scad').write_text(''.join(scad),encoding='utf-8')
    params={'version':'0.2','statut':'PROTOTYPE — NON VALIDE SUR MATERIEL','imprimante':'Bambu Lab A1 mini','plateau_mm':[180,180,180],'L1_mm':L1,'L2_mm':L2,'axes':{'base':'MG996R','epaule':'MG996R','coude':'MG996R','poignet_inclinaison':'MG90S','poignet_rotation':'MG90S','pince':'MG90S'},'servos_nominales':{'MG996R':BIG,'MG90S':SMALL},'charge_etudiee_g':TARGET_LOAD_G,'coques_epaisseur_mm':2.2,'socle_electronique':{'diametre_corps_mm':140,'hauteur_ajoutee_mm':ELEC_H,'encombrement_pattes_mm':166,'UNO_PCB_mm':[68.6,53.4,1.6],'supports_carte_hauteur_mm':6,'passage_cables_S01_mm':[14,9],'passage_cables_S01_xy_mm':[-40,-18],'fenetre_USB_mm':[30,21],'platine_mm':[42,25,2.4],'passage_cable_platine_mm':8,'zone_alimentation_mm':[60,22,16],'adaptateur_secteur':'EXTERNE','references_electroniques':'ENVELOPPES NOMINALES A VERIFIER AVEC COMPOSANTS ACHETES'},'reference_servo_vendeur':'A CONFIRMER','fixation_coques':'A FINALISER APRES ESSAI ARMATURE','compensation_epaule':'ANCRAGES PREVUS, RESSORT A DIMENSIONNER'}
    (OUT/'sources'/'parametres.json').write_text(json.dumps(params,ensure_ascii=False,indent=2),encoding='utf-8')

def gravity_check():
    # Conservative solid-PLA mass; not a stress, dynamic, thermal, or fatigue validation.
    ancestors={'upper':['upper','forearm','wrist','roll','finger_l','finger_r'],'forearm':['forearm','wrist','roll','finger_l','finger_r'],'wrist':['wrist','roll','finger_l','finger_r']}
    lookup={p['id']:p for p in PARTS}
    result={}
    for name,q in [('presentation',[0,25,45,100,0,18]),('bras_horizontal',[0,90,0,0,0,0])]:
        ff=frames(q);items=[]
        for rec in SCENE:
            p=lookup[rec['part']];c=np.r_[p['mesh'].center_mass,1];w=(ff[rec['owner']]@rec['local']@c)[:3]
            items.append((rec['owner'],p['masse_pleine_PLA_g'],w))
        for rec in SERVO_SCENE:
            mm=mesh(rec['shape']);c=np.r_[mm.center_mass,1];w=(ff[rec['owner']]@rec['local']@c)[:3]
            items.append((rec['owner'],rec['mass'],w))
        # Allowance for screws, horn adapters, wiring and moving bearings.
        for own,mass,z in [('upper',12,55),('forearm',10,40),('wrist',7,20),('roll',6,20)]:items.append((own,mass,(ff[own]@np.array([0,10,z,1]))[:3]))
        payload=(ff['roll']@np.array([0,5.5,PINCH_Z+32,1]))[:3]
        torques={}
        for joint,owners in ancestors.items():
            T=ff[joint];o=T[:3,3];axis=T[:3,1];mom=0
            for own,mass,w in items:
                if own in owners:
                    force=np.array([0,0,-mass*.00980665]);mom+=np.dot(np.cross((w-o)/1000,force),axis)
            force=np.array([0,0,-TARGET_LOAD_G*.00980665]);mom+=np.dot(np.cross((payload-o)/1000,force),axis)
            torques[joint]=round(abs(mom)/.0980665,3)
        result[name]={'angles_deg':q,'couples_statiques_kgf_cm':torques,'charge_g':TARGET_LOAD_G}
    result['limites']='Masses PLA pleines calculees; pas de validation des engrenages, du fluage, des efforts de pince, de la temperature, des mouvements ou des servos reels. Un couple de blocage ne constitue pas un couple continu admissible.'
    (OUT/'calcul_statique_preliminaire.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

def qc():
    problems=[]
    for p in PARTS:
        # Edge-connected components without optional scipy/networkx dependencies.
        f=p['mesh'].faces; parents=np.arange(len(p['mesh'].vertices))
        def root(a):
            while parents[a]!=a:parents[a]=parents[parents[a]];a=parents[a]
            return a
        for tri in f:
            a=root(int(tri[0]))
            for v in tri[1:]:parents[root(int(v))]=a
        comps=len({root(i) for i in range(len(parents))})
        p['composantes']=comps
        if not p['ferme'] or not p['volume_positif'] or max(p['dimensions_impression_mm'])>175 or comps!=1:
            problems.append({'id':p['id'],'ferme':p['ferme'],'volume':p['volume_cm3'],'dimensions':p['dimensions_impression_mm'],'composantes':comps})
    return problems

if __name__=='__main__':
    print('Generating geometry...',flush=True)
    build(); print('Generated',len(PARTS),'parts',flush=True)
    hardware();cleanup_shell_clearance();print('Checking meshes...',flush=True)
    issues=qc();print('QC:',json.dumps(issues),flush=True)
    export_all();print('Static:',json.dumps(gravity_check()),flush=True)
    (OUT/'controle_maillages.json').write_text(json.dumps({'pieces':len(PARTS),'anomalies':issues,'maillages':[{k:v for k,v in p.items() if k not in ['s','mesh']} for p in PARTS]},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Output:',OUT,flush=True)
