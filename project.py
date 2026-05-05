#GLOBAL STUFF
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
GRID_LENGTH=500
score=[0,0]
game_state="PLAYING"
random_seed=12345
arena_objects=[]

#NILOY GLOBALS
particles=[]
powerups=[]
car['dir']=[0,1]
car={
    'pos':[0,-400,0],
    'velocity':0,
    'acceleration':0.2,
    'friction':0.98,
    'nitro':100,
    'angle':90
}

ball={
    'pos':[0,0,20],
    'vel_axis':[0,0,0],
    'radius':20,
    'friction':0.99
}


def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60,1.25,1,2500) 
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0,-700,300,
              0,0,0,
              0,0,1)
#PLAYER__ARENA
def generate_arena(seed):
    global arena_objects
    random.seed(seed)
    arena_objects=[]
    for i in range(5):
        obj_x=random.randint(50,GRID_LENGTH-100)
        obj_y=random.randint(-GRID_LENGTH+100,GRID_LENGTH-100)
        obj_type=random.choice(['wall','pillar'])
        obj={
            'type':obj_type,
            'pos':[obj_x,obj_y,25]
        }
        arena_objects.append(obj)
        obj_mirror={
            'type':obj_type,
            'pos':[-obj_x,-obj_y,25]
        }
        arena_objects.append(obj_mirror)
def draw_arena():
    global arena_objects
    stripe_width=100
    for x in range(-GRID_LENGTH,GRID_LENGTH,stripe_width):
        if (x//stripe_width)%2==0:
            glColor3f(0.0,0.4,0.0)
        else:
            glColor3f(0.0,0.5,0.0)
        glBegin(GL_QUADS)
        glVertex3f(x,-GRID_LENGTH,0)
        glVertex3f(x+stripe_width,-GRID_LENGTH,0)
        glVertex3f(x+stripe_width,GRID_LENGTH,0)
        glVertex3f(x,GRID_LENGTH,0)
        glEnd()
    glColor3f(0.5,0.5,0.5)
    for obj in arena_objects:
        glPushMatrix()
        glTranslatef(obj['pos'][0],obj['pos'][1],obj['pos'][2])
        if obj['type']=='wall':
            glScalef(2,1,3)
            glutSolidCube(50)
        else:
            gluCylinder(gluNewQuadric(),20,20,100,10,10)
        glPopMatrix()
    #goal post draw
    glPushMatrix()
    glColor3f(1,1,0)
    glTranslatef(0,GRID_LENGTH,50)
    glScalef(200,20,100)
    glutSolidCube(1)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(1,1,0)
    glTranslatef(0,-GRID_LENGTH,50)
    glScalef(200,20,100)
    glutSolidCube(1)
    glPopMatrix()



def draw_car():
    glPushMatrix()
    glTranslatef(car['pos'][0],car['pos'][1],15)
    glRotatef(car['angle']-90,0,0,1)
    #car bbody
    glColor3f(0.0,0.3,0.8)
    glPushMatrix()
    glScalef(40,60,20)
    glutSolidCube(1)
    glPopMatrix()
    #windows
    glColor3f(0.5,0.8,1.0)
    glPushMatrix()
    glTranslatef(0,5,15)
    glScalef(25,20,10)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()
    
def draw_ball():
    glPushMatrix()
    glTranslatef(ball['pos'][0], ball['pos'][1], ball['pos'][2])
    glColor3f(1.0, 1.0, 1.0)
    gluSphere(gluNewQuadric(), ball['radius'], 20, 20)
    glPopMatrix()
        
def show_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_camera()
    draw_arena()
    draw_car()
    draw_ball()
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"CAR SOCCER")  # Create the window

    glutDisplayFunc(show_screen)  # Register display function
    #lutKeyboardFunc(keyboardListener)  # Register keyboard listener
    #glutSpecialFunc(specialKeyListener)
    #glutMouseFunc(mouseListener)
    #glutIdleFunc(idle)  # Register the idle function to move the bullet automatically
    generate_arena(random_seed)
    glutMainLoop()  # Enter the GLUT main loop
    

if __name__ == "__main__":
    main()