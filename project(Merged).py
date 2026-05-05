import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# ─── GLOBALS(NILOY)───────────────────────────────────────────────────────────────────
#Niloy Features:Nitro,Templlate,momentum drift,gravity jump,particle system,sweeper walls
particles=[]
#Niloy Feature 4
powerups={
    'active':False,
    'pos':[0,0,15],
    'rot':0,
    'timer':0
}
def update_powerup():
    if not powerups['active']:
        powerups['timer']+=1
        if powerups['timer']>500:
            powerups['active']=True
            powerups['pos'][0]=random.random(-400,400)
            powerups['pos'][1]=random.random(-400,400)
            
sweeper=[
    {'base_x':0,"y":200,'offset':0,"dir":1},
    {'base_x':0,"y":-200,'offset':0,"dir":-1},
]
GRID_LENGTH   = 500
score         = [0, 0]
game_state    = "PLAYING"
random_seed   = 12345
arena_objects = []

#Niloy feature 3
def update_sweeper():
    global ball
    for s in sweeper:
        s['offset']+=0.5*s['dir']
        if s['offset']>250:
            s['dir']=-1
        elif s['offset']<-250:
            s['dir']=1
        x=s['base_x']+s['offset']
        dist=math.hypot(ball['pos'][0]-x,ball['pos'][1]-s['y'])
        if dist<60:
            ball['vel'][0]=ball['pos'][0]*0.02
            ball['vel'][1]=ball['pos'][1]*0.02
            ball['vel'][2]=5
def draw_sweeper():
    glColor3f(1,0.5,0)
    for s in sweeper:
        glPushMatrix()
        glTranslatef(s['base_x']+s['offset'],s['y'],20)
        glScalef(120,20,40)
        glutSolidCube(1)
        glPopMatrix()
#Niloy Feature 1
def manage_particles_drift():
    global particles
    curr_speed=math.hypot(car['vx'],car['vy'])
    if curr_speed>0.1:
        #move_angle=math.degrees()
        car_a=math.radians(car['angle'])
        car_x=car['pos'][0]-(math.cos(car_a)*25)
        car_y=car['pos'][1]-(math.sin(car_a)*25)
        particles.append({
            'pos':[car_x,car_y,5],
            'vel':[random.uniform(-0.1,1),random.uniform(-0.1,1),random.uniform(0.5,1)],
            'life':1
        })
    for p in particles[:]:
        p['pos'][0]+=p['vel'][0]
        p['pos'][1]+=p['vel'][1]
        p['pos'][2]+=p['vel'][2]
        p['life']-=0.05
        if p['life']<=0:
            particles.remove(p)
def draw_particle():
    for p in particles:
        glPushMatrix()
        glTranslatef(p['pos'][0],p['pos'][1],p['pos'][2])
        darkness=0.6*p['life']
        glColor3f(darkness,darkness,darkness)
        glutSolidCube(4)
        glPopMatrix()
car = {
    'pos':          [0, -400, 0],
    'velocity':     0,
    'acceleration': 0.005,
    'friction':     0.98,
    'nitro':        0,        # current nitro %
    'nitro_max':    100,
    'angle':        90,
    'vx':           0,          # world-space velocity components
    'vy':           0,
    'vz':0,
    'using_nitro':  False,
}

ball = {
    'pos':    [0, 0, 20],
    'vel':    [0, 0, 0],
    'radius': 20,
    'friction': 0.99,
}

# ─── NITRO BOTTLES ─────────────────────────────────────────────────────────────
nitro_bottles   = []          # list of {'pos':[x,y], 'active':True, 'timer':0}
NITRO_RESPAWN   = 600         # frames until a collected bottle respawns
NITRO_AMOUNT    = 40          # nitro gained per bottle
NITRO_DRAIN     = 0.5         # nitro drained per frame while boosting
NITRO_BOOST_MUL = 2.5        # speed multiplier when nitro active
BOTTLE_RADIUS   = 18          # collision radius

# ─── MAP THEMES ────────────────────────────────────────────────────────────────
map_themes = [
    {'name': 'Urban Night',   'field': [(0.02,0.02,0.08), (0.04,0.04,0.12)],
     'wall': (0.3,0.3,0.35),  'goal': (0.0,0.6,1.0),  'car': (1.0,0.3,0.0)},
    {'name': 'Neon Desert',   'field': [(0.15,0.08,0.02),(0.18,0.10,0.03)],
     'wall': (0.4,0.25,0.1),  'goal': (1.0,0.5,0.0),  'car': (0.0,0.8,0.4)},
    {'name': 'Arctic Ice',    'field': [(0.55,0.75,0.85),(0.6,0.8,0.9)],
     'wall': (0.7,0.85,0.95), 'goal': (0.9,0.2,0.6),  'car': (0.2,0.9,1.0)},
    {'name': 'Toxic Swamp',   'field': [(0.05,0.15,0.03),(0.07,0.18,0.04)],
     'wall': (0.2,0.35,0.05), 'goal': (0.5,1.0,0.1),  'car': (0.8,0.0,0.8)},
]
current_theme = random.randint(0,2)#niloy
theme = map_themes[current_theme]

# ─── INPUT ─────────────────────────────────────────────────────────────────────
keys = {'w': False, 's': False, 'a': False, 'd': False, ' ': False}

# ─── CAMERA ────────────────────────────────────────────────────────────────────
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.25, 1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    cx, cy = car['pos'][0], car['pos'][1]
    # camera follows car from behind
    angle_r = math.radians(car['angle'])
    cam_dist = 350
    cam_x = cx - math.cos(angle_r) * cam_dist
    cam_y = cy - math.sin(angle_r) * cam_dist
    gluLookAt(cam_x, cam_y, 280,
              cx, cy, 0,
              0, 0, 1)
#Khalid feature 1
# ─── ARENA GENERATION ──────────────────────────────────────────────────────────
def generate_arena(seed):
    global arena_objects, nitro_bottles
    random.seed(seed)
    arena_objects = []
    # Ramps (wedge shapes represented as scaled cubes)
    for _ in range(3):
        rx = random.randint(-300, 300)
        ry = random.randint(-350, 350)
        arena_objects.append({'type': 'ramp', 'pos': [rx, ry, 10],
                              'rot': random.randint(0, 360)})
    # Pillars
    for _ in range(4):
        px = random.randint(-350, 350)
        py = random.randint(-400, 400)
        if abs(py) < 100:       # keep center clear
            py += 150 * (1 if py >= 0 else -1)
        arena_objects.append({'type': 'pillar', 'pos': [px, py, 0]})
    # Boost pads (decorative only)
    for _ in range(6):
        bx = random.randint(-400, 400)
        by = random.randint(-400, 400)
        arena_objects.append({'type': 'pad', 'pos': [bx, by, 1]})

    # Nitro bottles – random placement, avoid goal areas
    nitro_bottles = []
    bottle_positions = [
        (-300, -200), (300, -200),
        (-300,  200), (300,  200),
        (0,     0),
        (-150, -350), (150,  350),
    ]
    random.seed(seed + 77)
    for (bx, by) in bottle_positions:
        jx = bx + random.randint(-40, 40)
        jy = by + random.randint(-40, 40)
        nitro_bottles.append({'pos': [jx, jy], 'active': True, 'timer': 0})

# ─── DRAW HELPERS ──────────────────────────────────────────────────────────────
def draw_cylinder_z(base_r, top_r, height, slices=12, stacks=4):
    q = gluNewQuadric()
    gluCylinder(q, base_r, top_r, height, slices, stacks)
    gluDeleteQuadric(q)

def draw_arena():
    t = theme
    stripe_w = 100
    for x in range(-GRID_LENGTH, GRID_LENGTH, stripe_w):
        col = t['field'][0] if (x // stripe_w) % 2 == 0 else t['field'][1]
        glColor3f(*col)
        glBegin(GL_QUADS)
        glVertex3f(x,           -GRID_LENGTH, 0)
        glVertex3f(x+stripe_w,  -GRID_LENGTH, 0)
        glVertex3f(x+stripe_w,   GRID_LENGTH, 0)
        glVertex3f(x,            GRID_LENGTH, 0)
        glEnd()

    # boundary walls (4 sides)
    glColor3f(*t['wall'])
    walls = [
        (0,  GRID_LENGTH,  20, GRID_LENGTH*2, 10, 40),
        (0, -GRID_LENGTH,  20, GRID_LENGTH*2, 10, 40),
        ( GRID_LENGTH, 0,  20, 10, GRID_LENGTH*2, 40),
        (-GRID_LENGTH, 0,  20, 10, GRID_LENGTH*2, 40),
    ]
    for (wx, wy, wz, sx, sy, sz) in walls:
        glPushMatrix()
        glTranslatef(wx, wy, wz)
        glScalef(sx, sy, sz)
        glutSolidCube(1)
        glPopMatrix()

    # arena objects
    for obj in arena_objects:
        glPushMatrix()
        glTranslatef(*obj['pos'])
        if obj['type'] == 'pillar':
            glColor3f(*t['wall'])
            draw_cylinder_z(18, 18, 80)
        elif obj['type'] == 'ramp':
            glColor3f(t['wall'][0]*0.7, t['wall'][1]*0.7, t['wall'][2]*0.7)
            glRotatef(obj.get('rot', 0), 0, 0, 1)
            glScalef(60, 40, 15)
            glutSolidCube(1)
        elif obj['type'] == 'pad':
            glColor3f(0.9, 0.7, 0.0)
            glScalef(30, 30, 1)
            glutSolidCube(1)
        glPopMatrix()

    # goal posts
    for sign in [1, -1]:
        glColor3f(*t['goal'])
        glPushMatrix()
        glTranslatef(0, sign * GRID_LENGTH, 50)
        glScalef(200, 8, 100)
        glutSolidCube(1)
        glPopMatrix()
        # posts
        for px in [-100, 100]:
            glPushMatrix()
            glTranslatef(px, sign * GRID_LENGTH, 50)
            glScalef(8, 8, 110)
            glutSolidCube(1)
            glPopMatrix()

    # nitro bottles
    draw_nitro_bottles()

def draw_nitro_bottles():
    for bottle in nitro_bottles:
        if not bottle['active']:
            continue
        bx, by = bottle['pos']
        glPushMatrix()
        glTranslatef(bx, by, 10)
        # spinning bottle made from basic shapes
        t_rot = glutGet(GLUT_ELAPSED_TIME) * 0.1
        glRotatef(t_rot, 0, 0, 1)
        # bottle body (cylinder)
        glColor3f(0.1, 0.9, 0.3)
        draw_cylinder_z(8, 6, 28, 12, 4)
        # bottle neck
        glTranslatef(0, 0, 28)
        glColor3f(0.05, 0.6, 0.2)
        draw_cylinder_z(4, 3, 10, 8, 2)
        # cap
        glTranslatef(0, 0, 10)
        glColor3f(0.9, 0.1, 0.1)
        draw_cylinder_z(4, 0, 5, 8, 2)
        glPopMatrix()
        # glow ring on ground
        glColor4f(0.1, 1.0, 0.3, 0.25)
        glPushMatrix()
        glTranslatef(bx, by, 1)
        glScalef(1, 1, 0.1)
        q = gluNewQuadric()
        gluDisk(q, 12, 22, 20, 2)
        gluDeleteQuadric(q)
        glPopMatrix()

def draw_car():
    t = theme
    glPushMatrix()
    glTranslatef(car['pos'][0], car['pos'][1], 15+car['pos'][2])
    glRotatef(car['angle'] - 90, 0, 0, 1)

    # exhaust flames when nitro active
    if car['using_nitro'] and car['nitro'] > 0:
        glColor3f(1.0, 0.4, 0.0)
        glPushMatrix()
        glTranslatef(0, -35, 0)
        glScalef(10, 20 + random.random()*10, 8)
        glutSolidCone(1, 1, 6, 2)
        glPopMatrix()

    # body
    glColor3f(*t['car'])
    glPushMatrix()
    glScalef(40, 60, 20)
    glutSolidCube(1)
    glPopMatrix()
    # roof / cabin
    glColor3f(t['car'][0]*0.6, t['car'][1]*0.6, t['car'][2]*0.6)
    glPushMatrix()
    glTranslatef(0, 5, 17)
    glScalef(28, 28, 14)
    glutSolidCube(1)
    glPopMatrix()
    # windows
    glColor3f(0.5, 0.85, 1.0)
    glPushMatrix()
    glTranslatef(0, 6, 22)
    glScalef(22, 18, 4)
    glutSolidCube(1)
    glPopMatrix()
    # wheels (4)
    glColor3f(0.15, 0.15, 0.15)
    for wx, wy in [(-22, 20), (22, 20), (-22, -20), (22, -20)]:
        glPushMatrix()
        glTranslatef(wx, wy, -8)
        glRotatef(90, 0, 1, 0)
        draw_cylinder_z(9, 9, 8, 10, 2)
        glPopMatrix()

    glPopMatrix()

def draw_ball():
    glPushMatrix()
    glTranslatef(*ball['pos'])
    glColor3f(1.0, 1.0, 1.0)
    q = gluNewQuadric()
    gluSphere(q, ball['radius'], 20, 20)
    gluDeleteQuadric(q)
    glPopMatrix()
#Khalid Feature 2
# ─── MINIMAP ───────────────────────────────────────────────────────────────────
MINIMAP_X      = 820   # screen pixel x (top-right area)
MINIMAP_Y      = 620   # screen pixel y
MINIMAP_SIZE   = 160
MINIMAP_SCALE  = MINIMAP_SIZE / (GRID_LENGTH * 2)

def world_to_mini(wx, wy):
    mx = MINIMAP_X + (wx + GRID_LENGTH) * MINIMAP_SCALE
    my = MINIMAP_Y + (wy + GRID_LENGTH) * MINIMAP_SCALE
    return mx, my

def draw_minimap():
    # switch to 2D ortho
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    # background
    glColor4f(0.0, 0.0, 0.0, 0.6)
    glBegin(GL_QUADS)
    glVertex2f(MINIMAP_X - 5,              MINIMAP_Y - 5)
    glVertex2f(MINIMAP_X + MINIMAP_SIZE+5, MINIMAP_Y - 5)
    glVertex2f(MINIMAP_X + MINIMAP_SIZE+5, MINIMAP_Y + MINIMAP_SIZE+5)
    glVertex2f(MINIMAP_X - 5,              MINIMAP_Y + MINIMAP_SIZE+5)
    glEnd()

    # field
    glColor3f(*theme['field'][0])
    glBegin(GL_QUADS)
    glVertex2f(MINIMAP_X,              MINIMAP_Y)
    glVertex2f(MINIMAP_X+MINIMAP_SIZE, MINIMAP_Y)
    glVertex2f(MINIMAP_X+MINIMAP_SIZE, MINIMAP_Y+MINIMAP_SIZE)
    glVertex2f(MINIMAP_X,              MINIMAP_Y+MINIMAP_SIZE)
    glEnd()

    # centre circle
    glColor3f(1.0, 1.0, 1.0)
    cx_m, cy_m = world_to_mini(0, 0)
    r = 15 * MINIMAP_SCALE * GRID_LENGTH / 100
    glBegin(GL_LINE_LOOP)
    for i in range(30):
        a = 2*math.pi*i/30
        glVertex2f(cx_m + math.cos(a)*r, cy_m + math.sin(a)*r)
    glEnd()

    # goal lines
    glColor3f(*theme['goal'])
    glLineWidth(3)
    gx1, gy1 = world_to_mini(-100, GRID_LENGTH)
    gx2, gy2 = world_to_mini( 100, GRID_LENGTH)
    glBegin(GL_LINES); glVertex2f(gx1, gy1); glVertex2f(gx2, gy2); glEnd()
    gx1, gy1 = world_to_mini(-100, -GRID_LENGTH)
    gx2, gy2 = world_to_mini( 100, -GRID_LENGTH)
    glBegin(GL_LINES); glVertex2f(gx1, gy1); glVertex2f(gx2, gy2); glEnd()
    glLineWidth(1)

    # obstacles
    glColor3f(*theme['wall'])
    for obj in arena_objects:
        if obj['type'] in ('pillar', 'ramp'):
            ox, oy = world_to_mini(obj['pos'][0], obj['pos'][1])
            glBegin(GL_QUADS)
            glVertex2f(ox-3, oy-3); glVertex2f(ox+3, oy-3)
            glVertex2f(ox+3, oy+3); glVertex2f(ox-3, oy+3)
            glEnd()

    # nitro bottles on minimap
    for bot in nitro_bottles:
        if not bot['active']:
            continue
        bx, by = world_to_mini(bot['pos'][0], bot['pos'][1])
        glColor3f(0.1, 1.0, 0.3)
        glBegin(GL_TRIANGLES)
        glVertex2f(bx, by+5); glVertex2f(bx-4, by-4); glVertex2f(bx+4, by-4)
        glEnd()

    # ball (white dot)
    bx, by = world_to_mini(ball['pos'][0], ball['pos'][1])
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glVertex2f(bx-4, by-4); glVertex2f(bx+4, by-4)
    glVertex2f(bx+4, by+4); glVertex2f(bx-4, by+4)
    glEnd()

    # car (coloured arrow)
    carx, cary = world_to_mini(car['pos'][0], car['pos'][1])
    glColor3f(*theme['car'])
    ar = math.radians(car['angle'])
    tip_x = carx + math.cos(ar) * 7
    tip_y = cary + math.sin(ar) * 7
    lft_x = carx + math.cos(ar + 2.4) * 5
    lft_y = cary + math.sin(ar + 2.4) * 5
    rgt_x = carx + math.cos(ar - 2.4) * 5
    rgt_y = cary + math.sin(ar - 2.4) * 5
    glBegin(GL_TRIANGLES)
    glVertex2f(tip_x, tip_y)
    glVertex2f(lft_x, lft_y)
    glVertex2f(rgt_x, rgt_y)
    glEnd()

    # border
    glColor3f(0.8, 0.8, 0.8)
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(MINIMAP_X, MINIMAP_Y)
    glVertex2f(MINIMAP_X+MINIMAP_SIZE, MINIMAP_Y)
    glVertex2f(MINIMAP_X+MINIMAP_SIZE, MINIMAP_Y+MINIMAP_SIZE)
    glVertex2f(MINIMAP_X, MINIMAP_Y+MINIMAP_SIZE)
    glEnd()
    glLineWidth(1)

    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()
#Khalid Feature 3
# ─── NITRO HUD BAR ─────────────────────────────────────────────────────────────
def draw_hud():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    # Score
    glColor3f(1, 1, 1)
    draw_text(470, 770, f"BLUE  {score[0]} : {score[1]}  ORANGE")

    # Nitro bar background
    bar_x, bar_y, bar_w, bar_h = 40, 30, 200, 22
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y); glVertex2f(bar_x+bar_w, bar_y)
    glVertex2f(bar_x+bar_w, bar_y+bar_h); glVertex2f(bar_x, bar_y+bar_h)
    glEnd()
    # Nitro fill
    pct = car['nitro'] / car['nitro_max']
    if pct > 0.5:
        nc = (0.1, 0.9, 0.3)
    elif pct > 0.2:
        nc = (1.0, 0.7, 0.0)
    else:
        nc = (1.0, 0.1, 0.1)
    glColor3f(*nc)
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y); glVertex2f(bar_x + bar_w*pct, bar_y)
    glVertex2f(bar_x + bar_w*pct, bar_y+bar_h); glVertex2f(bar_x, bar_y+bar_h)
    glEnd()
    # label
    glColor3f(1, 1, 1)
    draw_text(bar_x, bar_y + 5, f"NITRO  {int(car['nitro'])}%")

    # boost indicator
    if car['using_nitro'] and car['nitro'] > 0:
        glColor3f(1.0, 0.6, 0.0)
        draw_text(bar_x, bar_y + 30, "!! BOOST ACTIVE !!")

    # theme name (top-left)
    glColor3f(0.7, 0.7, 0.7)
    draw_text(10, 780, f"MAP: {theme['name']}")

    # controls hint
    glColor3f(0.5, 0.5, 0.5)
    draw_text(10, 10, "WASD: Drive  SPACE: Nitro  T: Change Map  R: Reset")

    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()

def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(ch))

# ─── PHYSICS ───────────────────────────────────────────────────────────────────
def update_car():
    global game_state
    #Niloy feature 2
    car['pos'][2]+=car['vz']
    if car['pos'][2]>0:
        car['vz']-=0.05
    else:
        car['pos'][2]=0
        car['vz']=0
    angle_r = math.radians(car['angle'])

    # nitro modifier
    #Niloy fix
    using = keys[' '] and car['nitro'] > 0
    car['using_nitro'] = using
    boost = NITRO_BOOST_MUL if using else 1.0
    if using:
        car['nitro'] = max(0, car['nitro'] - NITRO_DRAIN)

    if keys['w']:
        car['vx'] += math.cos(angle_r) * car['acceleration'] * boost
        car['vy'] += math.sin(angle_r) * car['acceleration'] * boost
    if keys['s']:
        car['vx'] -= math.cos(angle_r) * car['acceleration'] * 0.6
        car['vy'] -= math.sin(angle_r) * car['acceleration'] * 0.6
    if keys['a']:
        car['angle'] += 0.3#niloy
    if keys['d']:
        car['angle'] -= 0.3

    car['vx'] *= car['friction']
    car['vy'] *= car['friction']

    nx = car['pos'][0] + car['vx']
    ny = car['pos'][1] + car['vy']
    nx = max(-GRID_LENGTH+25, min(GRID_LENGTH-25, nx))
    ny = max(-GRID_LENGTH+25, min(GRID_LENGTH-25, ny))
    car['pos'][0] = nx
    car['pos'][1] = ny

def update_ball():
    ball['pos'][0] += ball['vel'][0]
    ball['pos'][1] += ball['vel'][1]
    ball['pos'][2] += ball['vel'][2]
    ball['vel'][0] *= ball['friction']
    ball['vel'][1] *= ball['friction']
    ball['vel'][2] *= 0.97
    # gravity-ish
    if ball['pos'][2] > ball['radius']:
        ball['vel'][2] -= 0.3
    else:
        ball['pos'][2] = ball['radius']
        ball['vel'][2] *= -0.4

    # wall bounce
    for i, lim in enumerate([GRID_LENGTH-20, GRID_LENGTH-20]):
        if abs(ball['pos'][i]) > lim:
            ball['vel'][i] *= -0.7
            ball['pos'][i] = math.copysign(lim, ball['pos'][i])

    # goal detection
    #check_goal()
    check_goal_with_celebration()

def check_goal():
    global game_state
    if abs(ball['pos'][0]) < 100:
        if ball['pos'][1] > GRID_LENGTH - 25:
            score[0] += 1
            reset_ball()
        elif ball['pos'][1] < -(GRID_LENGTH - 25):
            score[1] += 1
            reset_ball()

def reset_ball():
    ball['pos']  = [0, 0, 20]
    ball['vel']  = [0, 0, 0]

def car_ball_collision():
    dx = ball['pos'][0] - car['pos'][0]
    dy = ball['pos'][1] - car['pos'][1]
    dist = math.hypot(dx, dy)
    hit_r = ball['radius'] + 30
    if dist < hit_r and dist > 0:
        nx, ny = dx/dist, dy/dist
        speed = math.hypot(car['vx'], car['vy']) + 2
        ball['vel'][0] = nx * speed * 3
        ball['vel'][1] = ny * speed * 3
        ball['vel'][2] = 4

def check_nitro_pickups():
    cx, cy = car['pos'][0], car['pos'][1]
    for bottle in nitro_bottles:
        if not bottle['active']:
            bottle['timer'] += 1
            if bottle['timer'] >= NITRO_RESPAWN:
                bottle['active'] = True
                bottle['timer']  = 0
            continue
        bx, by = bottle['pos']
        if math.hypot(cx - bx, cy - by) < BOTTLE_RADIUS + 20:
            bottle['active'] = False
            bottle['timer']  = 0
            car['nitro'] = min(car['nitro_max'], car['nitro'] + NITRO_AMOUNT)

# ─── DISPLAY ───────────────────────────────────────────────────────────────────
def show_screen():
    glClearColor(0.05, 0.05, 0.08, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_camera()
    draw_arena()
    draw_sweeper()
    draw_particle()
    draw_car()
    draw_ball()
    draw_minimap()
    draw_hud()
    draw_enemy_car()
    draw_dynamic_light_effect()
    glutSwapBuffers()

# ─── INPUT HANDLERS ────────────────────────────────────────────────────────────
def keyboard_down(key, x, y):
    global current_theme, theme, random_seed
    k = key.decode('utf-8').lower() if isinstance(key, bytes) else key.lower()
        
    if k in keys:
        keys[k] = True
    if k == 't':
        current_theme = (current_theme + 1) % len(map_themes)
        theme = map_themes[current_theme]
    if k == 'r':
        car['pos'] = [0, -400, 0]
        car['vx'] = 0; car['vy'] = 0
        car['nitro'] = car['nitro_max']
        reset_ball()
    if k == 'n':          # new random map
        random_seed = random.randint(1, 99999)
        generate_arena(random_seed)
    #Niloy feature 2
    if k=='j' and car['pos'][2]<=0:
        car['vz']=12
def keyboard_up(key, x, y):
    k = key.decode('utf-8').lower() if isinstance(key, bytes) else key.lower()
    if k in keys:
        keys[k] = False

def special_down(key, x, y):
    mapping = {GLUT_KEY_UP:'w', GLUT_KEY_DOWN:'s',
                GLUT_KEY_LEFT:'a', GLUT_KEY_RIGHT:'d'}
    if key in mapping:
        keys[mapping[key]] = True

def special_up(key, x, y):
    mapping = {GLUT_KEY_UP:'w', GLUT_KEY_DOWN:'s',
                GLUT_KEY_LEFT:'a', GLUT_KEY_RIGHT:'d'}
    if key in mapping:
        keys[mapping[key]] = False

def idle():
    update_car()
    update_ball()
    update_sweeper()
    car_ball_collision()
    check_nitro_pickups()
    manage_particles_drift()
    update_enemy_ai()
    enemy_ball_collision()
    update_dynamic_light()
    update_goal_celebration()
    glutPostRedisplay()








enemy_car = {
    'pos': [0, 400, 0],
    'vx': 0,
    'vy': 0,
    'angle': -90,
    'acceleration': 0.015,
    'friction': 0.97,
    'max_speed': 3
}

dynamic_light_angle = 0

goal_message_timer = 0
goal_flash_timer = 0
camera_shake_timer = 0


# ─── SAZZAD FEATURE 1: ENEMY AI ───────────────────────────────────────────────

# Enemy car follows the ball
def update_enemy_ai():
    # 1. Find the distance to the ball
    dx = ball['pos'][0] - enemy_car['pos'][0]
    dy = ball['pos'][1] - enemy_car['pos'][1]
    dist = math.hypot(dx, dy)

    # 2. Always look exactly at the ball
    target_angle = math.degrees(math.atan2(dy, dx))
    enemy_car['angle'] = target_angle
    angle_r = math.radians(target_angle)

    # 3. Direct Movement (No sliding, no friction, no overshooting)
    # It just moves forward at a constant speed of 3.5
    enemy_car['pos'][0] += math.cos(angle_r) * 0.15
    enemy_car['pos'][1] += math.sin(angle_r) * 0.15

    # 4. Keep enemy inside the arena walls
    enemy_car['pos'][0] = max(-GRID_LENGTH + 25, min(GRID_LENGTH - 25, enemy_car['pos'][0]))
    enemy_car['pos'][1] = max(-GRID_LENGTH + 25, min(GRID_LENGTH - 25, enemy_car['pos'][1]))


# Draw enemy car
def draw_enemy_car():
    glPushMatrix()
    glTranslatef(enemy_car['pos'][0], enemy_car['pos'][1], 15)
    glRotatef(enemy_car['angle'] - 90, 0, 0, 1)

    # enemy body
    glColor3f(0.9, 0.1, 0.1)
    glPushMatrix()
    glScalef(40, 60, 20)
    glutSolidCube(1)
    glPopMatrix()

    # enemy cabin
    glColor3f(0.4, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 5, 17)
    glScalef(28, 28, 14)
    glutSolidCube(1)
    glPopMatrix()

    # enemy window
    glColor3f(1.0, 0.7, 0.7)
    glPushMatrix()
    glTranslatef(0, 6, 22)
    glScalef(22, 18, 4)
    glutSolidCube(1)
    glPopMatrix()

    # enemy wheels
    glColor3f(0.1, 0.1, 0.1)
    for wx, wy in [(-22, 20), (22, 20), (-22, -20), (22, -20)]:
        glPushMatrix()
        glTranslatef(wx, wy, -8)
        glRotatef(90, 0, 1, 0)
        draw_cylinder_z(9, 9, 8, 10, 2)
        glPopMatrix()

    glPopMatrix()


# Enemy car hits the ball
def enemy_ball_collision():
    dx = ball['pos'][0] - enemy_car['pos'][0]
    dy = ball['pos'][1] - enemy_car['pos'][1]

    dist = math.hypot(dx, dy)
    hit_r = ball['radius'] + 30 # Collision radius

    if dist < hit_r and dist > 0:
        # Calculate the push angle
        nx = dx / dist
        ny = dy / dist

        # Hardcode a massive hit speed so it always smashes the ball away
        impact_power = 6 

        ball['vel'][0] = nx * impact_power * 0.3
        ball['vel'][1] = ny * impact_power * 0.3
        ball['vel'][2] = 2 # Pop it into the air


# ─── SAZZAD FEATURE 2: DYNAMIC LIGHTING EFFECT ────────────────────────────────
# Fake dynamic lighting using normal shapes only.
# No glLightfv, no GL_LIGHTING, no GLUT time function.

# Moves the fake light around the arena
def update_dynamic_light():
    global dynamic_light_angle

    dynamic_light_angle += 0.05

    if dynamic_light_angle >= 360:
        dynamic_light_angle = 0


# Draws fake moving light effect
def draw_dynamic_light_effect():
    lx = math.cos(math.radians(dynamic_light_angle)) * 350
    ly = math.sin(math.radians(dynamic_light_angle)) * 350

    # bright light orb
    glPushMatrix()
    glTranslatef(lx, ly, 180)
    glColor3f(1.0, 1.0, 0.2)
    gluSphere(gluNewQuadric(), 18, 12, 12)
    glPopMatrix()

    # outer glow orb
    glPushMatrix()
    glTranslatef(lx, ly, 175)
    glColor3f(1.0, 0.6, 0.0)
    gluSphere(gluNewQuadric(), 28, 12, 12)
    glPopMatrix()

    # light patch on the ground
    glPushMatrix()
    glTranslatef(lx, ly, 2)
    glColor3f(1.0, 0.8, 0.1)
    glScalef(70, 70, 1)
    glutSolidCube(1)
    glPopMatrix()


# ─── SAZZAD FEATURE 3: GOAL CELEBRATION EFFECT ────────────────────────────────

# Camera shake during celebration
def setup_camera_with_goal_shake():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.25, 1, 3000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    cx, cy = car['pos'][0], car['pos'][1]

    angle_r = math.radians(car['angle'])
    cam_dist = 350

    shake_x = 0
    shake_y = 0

    if camera_shake_timer > 0:
        shake_x = random.randint(-8, 8)
        shake_y = random.randint(-8, 8)

    cam_x = cx - math.cos(angle_r) * cam_dist + shake_x
    cam_y = cy - math.sin(angle_r) * cam_dist + shake_y

    gluLookAt(
        cam_x, cam_y, 280,
        cx, cy, 0,
        0, 0, 1
    )


# When the ball goes inside the goal
def check_goal_with_celebration():
    global game_state
    global goal_message_timer, goal_flash_timer, camera_shake_timer

    if goal_message_timer > 0:
        return

    if abs(ball['pos'][0]) < 100:
        if ball['pos'][1] > GRID_LENGTH - 25:
            score[0] += 1

            goal_message_timer = 120
            goal_flash_timer = 120
            camera_shake_timer = 40

            reset_ball()

        elif ball['pos'][1] < -(GRID_LENGTH - 25):
            score[1] += 1

            goal_message_timer = 120
            goal_flash_timer = 120
            camera_shake_timer = 40

            reset_ball()


# How long the celebration stays active
def update_goal_celebration():
    global goal_message_timer, goal_flash_timer, camera_shake_timer

    if goal_message_timer > 0:
        goal_message_timer -= 1

    if goal_flash_timer > 0:
        goal_flash_timer -= 1

    if camera_shake_timer > 0:
        camera_shake_timer -= 1


# Goal posts flash after scoring
def draw_goal_posts_with_flash():
    for sign in [1, -1]:
        if goal_flash_timer > 0 and goal_flash_timer % 20 < 10:
            glColor3f(1.0, 0.0, 0.0)
        else:
            glColor3f(*theme['goal'])

        glPushMatrix()
        glTranslatef(0, sign * GRID_LENGTH, 50)
        glScalef(200, 8, 100)
        glutSolidCube(1)
        glPopMatrix()

        for px in [-100, 100]:
            glPushMatrix()
            glTranslatef(px, sign * GRID_LENGTH, 50)
            glScalef(8, 8, 110)
            glutSolidCube(1)
            glPopMatrix()


# Big GOAL text during celebration
def draw_goal_celebration_text():
    if goal_message_timer > 0:
        glColor3f(1.0, 1.0, 0.0)
        draw_text(455, 430, "GOAL!")

        glColor3f(1.0, 1.0, 1.0)
        draw_text(435, 405, "GET READY!")
        
        
        
        
# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(b"CAR SOCCER  |  WASD + SPACE-Nitro  |  T-Theme  |  N-New Map")
    glEnable(GL_DEPTH_TEST)
    #Banned(Niloy fix)
    #glEnable(GL_BLEND)
    #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glutDisplayFunc(show_screen)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutIdleFunc(idle)
    generate_arena(random_seed)
    glutMainLoop()

if __name__ == "__main__":
    main()