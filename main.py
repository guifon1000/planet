import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import NumericProperty,ReferenceListProperty,\
    ObjectProperty
from kivy.vector import Vector
from random import randint,random
import math
from kivy.graphics import Color, Rectangle,Ellipse
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import ScatterLayout
from random import random as r

class physObject(Widget):
    def __init__(self):
        self.rho=10.
        self.pos_hint={'x':r(), 'y':r()}
        super(physObject, self).__init__()
        self.velocity=[0.,0.]
        self.force=[0.,0.]
    def setPosition(self,x,y):
        self.pos_hint={'x':x-0.5*self.size_hint[0],'y':y-0.5*self.size_hint[1]}
    def addForce(self,f):
        self.force[0]+=f[0]
        self.force[1]+=f[1]
    def move(self,dt):
        pCenter=[self.pos_hint['x']+0.5*self.size_hint[0],self.pos_hint['y']+0.5*self.size_hint[1]]
        self.setPosition(self.velocity[0]*dt+pCenter[0],self.velocity[1]*dt+pCenter[1])
    def applyForce(self,f,dt):
        self.velocity=[self.velocity[0]+f[0]*dt/self.mass,self.velocity[1]+f[1]*dt/self.mass]
    def distance(self,p2):
        dx = p2.centerX-self.centerX
        dy = p2.centerY-self.centerY
        return math.sqrt(dx**2+dy**2),dx,dy
    def radius(self):
        po1=po1=self.pos
        po2=[self.right,self.top]
        return float(0.5*math.sqrt((po2[0]-po1[0])**2+(po2[1]-po1[1])**2))



class Cosmos(FloatLayout):
    def __init__(self):
        self.dt=0.01
        self.rl=ScatterLayout()
        super(Cosmos, self).__init__()
    def Zoom(self,fac,*largs):
        self.size=[fac*self.size[0],fac*self.size[1]]
    def varyDT(self,direction,*largs):
        if direction == '+':self.dt+=0.01
        if direction == '-':
            self.dt=max(0.0000001,self.dt-0.01)
    def distanceMatrix(self):
        n=len(self.physObj)
        matrix=[[0 for i in xrange(n)] for i in xrange(n)]
        collided=[]
        for i in range(n):
            for j in range(i,n): 
                Pi=self.physObj[i]
                Pj=self.physObj[j]
                if i!=j:
                    d,dx,dy=Pi.distance(Pj)
                    if Pi.distance(Pj)[0]<0.9*(Pi.radius()+Pj.radius()):
                        collided.append([Pi,Pj])
                    matrix[i][j]=Pi.distance(Pj)
                    matrix[j][i]=Pi.distance(Pj)
                else:
                    matrix[i][j]=0  
        return matrix, collided
    def collisions(self,collided):
        for c in collided:
            m1=c[0].mass
            m2=c[1].mass
            rho1=c[0].rho
            rho2=c[1].rho
            s1=c[0].size_hint[0]
            s2=c[1].size_hint[0]
            v1=c[0].velocity
            v2=c[1].velocity
            c[1].rho=(s1**2.*rho1+s2**2.*rho2)/(s1**2.+s2**2.)
            c[1].mass=c[0].mass+c[1].mass
            s=math.sqrt(c[1].mass/(math.pi*c[1].rho))
            c[1].size_hint=(s,s)
            c[1].velocity=((m1*v1[0]+m2*v2[0])/(m1+m2),(m1*v1[1]+m2*v2[1])/(m1+m2))
            self.remove_widget(c[0])

    def physicalObjects(self):
        co=self.children[:]
        x=[]
        print co 
        print '***** BEFORE *********'
        for c in co:
            print str(c)
            if 'physObject' in str(c) :
                x.append(c)
        print '***** AFTER  *********'
        for c in x:
            print str(type(c))
        self.physObj=x
    def updateForce(self,G):
        #print '********   UPDATE FORCE  *********'
        n=len(self.physObj)
        print n
        for c in self.physObj:
            #print type(c)
            c.force=[0.,0.]
        for i in range(n):
            for j in range(i,n): 
                Pi=self.physObj[i]
                Pj=self.physObj[j]
                #print type(Pi)
                if i!=j:
                    d,dx,dy=Pi.distance(Pj)
                    d3=d**3.
                    fx=G*Pi.mass*Pj.mass*dx/d3
                    fy=G*Pi.mass*Pj.mass*dy/d3
                    fij=[-fx,-fy]
                    fji=[fx,fy]
                    Pi.addForce(fji)
                    Pj.addForce(fij)
    def update(self,dt):
        G=1.
        self.physicalObjects()
        self.updateForce(G)
        for g in self.children[0:-1]:
            if not isinstance(g,BoxLayout): 
                g.applyForce(g.force,self.dt)
                if g.pos[0]<0 or g.right>=self.width:
                    g.velocity[0]=-g.velocity[0]
                if g.pos[1]<0 or g.top>self.height:
                    g.velocity[1]=-g.velocity[1]
                g.move(self.dt)
                g.force=[0,0]
        matrix,collided=self.distanceMatrix()
        self.collisions(collided)
    pass


class visuZone:
    pass




class PlanetApp(App):
    def add_planet(self,root,x,y,ray,rho=r()*100000.,mass=r(),*largs):
        wid=physObject()
        wid.mass=1.
        wid.pos=[r()*root.width,r()*root.height]
        wid.rho=1000.
        s=math.sqrt(wid.mass/(wid.rho*math.pi))
        wid.size_hint=(s,s)
        root.add_widget(wid)
    def build(self):
        cosmos=Cosmos()
        cosmos.size=[1800,600]
        btn_add = Button(text='add a planet',on_press=partial(self.add_planet,cosmos.rl,r(),r(),10.))
        btnQ = Button(text='quit',on_press=self.stop)
        btnDTplus = Button(text='dt+',on_press=partial(cosmos.varyDT,'+'))
        btnDTmoins = Button(text='dt-',on_press=partial(cosmos.varyDT,'-'))
        btnZoomIn = Button(text='ZoomIn',on_press=partial(cosmos.Zoom,0.5))
        btnZoomOut = Button(text='ZoomOut',on_press=partial(cosmos.Zoom,2.))
        layout = BoxLayout(size_hint=(float(1./cosmos.size_hint[0]), None), height=30)
        layout.add_widget(btn_add)
        layout.add_widget(btnQ)
        layout.add_widget(btnDTplus)
        layout.add_widget(btnDTmoins)
        layout.add_widget(btnZoomIn)
        layout.add_widget(btnZoomOut)
        cosmos.rl.add_widget(layout)
        Clock.schedule_interval(cosmos.update,cosmos.dt)
        return cosmos.rl
if __name__=='__main__':
    PlanetApp().run()
