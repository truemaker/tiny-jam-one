import pygame, os, math, random

pygame.init()

screen = pygame.display.set_mode((800, 600))
smallfont = pygame.font.SysFont('Arial', 15)
font = pygame.font.SysFont('Arial', 30)
bigfont = pygame.font.SysFont('Arial', 80)

screen.fill((0, 0, 0))
screen.blit(font.render('Loading...', True, (255, 255, 255)), (400-font.size("Loading...")[0]/2, 300-font.size("Loading...")[1]/2))
pygame.display.flip()

pygame.display.set_caption("Eternity²")

fb = pygame.Surface((800,600))
clock = pygame.time.Clock()


player_stats = {'rate': 30, 'speed': 5, 'mana': 100, 'burst_cooldown': 0}

textures = {
    'powerup0': pygame.image.load('resources/powerup0.png').convert(),
    'powerup1': pygame.image.load('resources/powerup1.png').convert(),
    'powerup2': pygame.image.load('resources/powerup2.png').convert(),
    'cursor': pygame.image.load('resources/cursor.png').convert(),
    'splash': pygame.image.load('resources/splash.png').convert()
}

sounds = {
    'explosion': pygame.mixer.Sound('resources/explosion_handmade.wav')
}

# Make the background transparent again
for texname in textures:
    textures[texname].set_colorkey((0,0,0))

def circle_surf(color, radius):
    radius = int(radius)
    surf = pygame.Surface((radius*2, radius*2))
    pygame.draw.circle(surf, color,(radius,radius),radius)
    surf.set_colorkey((0, 0, 0))
    return surf

# Start score system
def get_scores():
    if os.path.exists('scores'):
        with open('scores', 'r') as f:
            return f.read().split('\n')
    else:
        return []

def save_scores(scores):
    with open('scores', 'w') as f:
        f.write('\n'.join(scores))

scores = get_scores()
score = 0
# End score system

# Start game classes
class GameObject:
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.x_speed = 0
        self.y_speed = 0
        self.ignore_collision = False
        self.glowing = False
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
    def update(self):
        if not self.ignore_collision:
            self.rect.x += self.x_speed
            if scene.check_collision_on_obj(self):
                self.rect.x -= self.x_speed
            self.rect.y += self.y_speed
            if scene.check_collision_on_obj(self):
                self.rect.y -= self.y_speed
        else:
            self.rect.x += self.x_speed
            self.rect.y += self.y_speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 800:
            self.rect.right = 800
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > 600:
            self.rect.bottom = 600
    def check_collision(self, other):
        return self.rect.colliderect(other.rect)
    def kill(self):
        self.ignore_collision = True
        scene.remove_object(self)
    def collision(self,other):
        pass
    def glow(self):
        if not self.glowing:
            return
        rsize = (math.sin(frames/10)/2+0.5)*2 + 0.1
        cs = circle_surf((self.color[0]/12,self.color[1]/12,self.color[2]/12), self.rect.width*2+rsize)
        fb.blit(cs,(self.rect.centerx-self.rect.width*2-rsize, self.rect.centery-self.rect.width*2-rsize), special_flags=pygame.BLEND_RGB_ADD)
        cs = circle_surf((self.color[0]/12,self.color[1]/12,self.color[2]/12), int(self.rect.width*1.75+rsize))
        fb.blit(cs,(self.rect.centerx-self.rect.width*1.75-rsize, self.rect.centery-self.rect.width*1.75-rsize), special_flags=pygame.BLEND_RGB_ADD)
        cs = circle_surf((self.color[0]/12,self.color[1]/12,self.color[2]/12), self.rect.width*1.25+rsize)
        fb.blit(cs,(self.rect.centerx-self.rect.width*1.25-rsize, self.rect.centery-self.rect.width*1.25-rsize), special_flags=pygame.BLEND_RGB_ADD)

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20, (0, 255, 255))
        self.glowing = True
    def update(self):
        if player_stats['burst_cooldown'] > 0:
            player_stats['burst_cooldown'] -= 1
        keys = pygame.key.get_pressed()
        self.x_speed = 0
        self.y_speed = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x_speed = -player_stats['speed']
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x_speed = player_stats['speed']
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y_speed = -player_stats['speed']
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y_speed = player_stats['speed']
        
        if keys[pygame.K_LCTRL] and player_stats['mana'] > 0:
            if player_stats['mana'] > 10:
                self.x_speed *= 5
                self.y_speed *= 5
                if abs(self.x_speed) > 0 or abs(self.y_speed) > 0:
                    player_stats['mana'] -= 1
            else:
                self.x_speed *= 2
                self.y_speed *= 2
                if abs(self.x_speed) > 0 or abs(self.y_speed) > 0:
                    player_stats['mana'] -= 1

        if keys[pygame.K_LSHIFT] and player_stats['burst_cooldown'] <= 0:
            player_stats['burst_cooldown'] = 300
            for i in range(200):
                x = random.randint(self.rect.left, self.rect.right)
                y = random.randint(self.rect.top, self.rect.bottom)
                velx = random.randint(-10,10)
                vely = random.randint(-10,10)
                while not ((abs(velx) > 2) or (abs(vely) > 2)):
                    velx = random.randint(-10,10)
                    vely = random.randint(-10,10)
                scene.add_object(Projectile(x, y, (0, 255, 255), random.randint(-5,5), random.randint(-5,5), True))
                particle_system.add_particle(Particle(x, y, (255, 255, 255), velx, vely, random.randint(10,50)/10))

        if abs(self.x_speed) > player_stats['speed'] or abs(self.y_speed) > player_stats['speed']:
            particle_system.add_particle(Particle(self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2, (255, 255, 255), random.randint(-10, 10)/10, random.randint(-10, 10)/10, (abs(self.x_speed)+abs(self.y_speed))/4))
        else:
            if pygame.mouse.get_pressed()[0]:
                if frames % player_stats['rate'] == 0:
                    directionx = mousex - self.rect.x
                    directiony = mousey - self.rect.y
                    directionmax = max(abs(directionx), abs(directiony))
                    directionx /= directionmax
                    directiony /= directionmax
                    scene.add_object(Projectile(self.rect.centerx, self.rect.centery, (0,255,255), directionx*5, directiony*5, True))
        if health <= 0:
            self.kill()
            scene.stop()
        super().update()
    def draw(self, screen):
        super().draw(screen)
        

class Enemy(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20, (255, 0, 0))
    def update(self):
        self.x_speed = -(self.rect.centerx - player.rect.centerx)
        self.y_speed = -(self.rect.centery - player.rect.centery)
        maximum = max(abs(self.x_speed), abs(self.y_speed))
        self.x_speed = self.x_speed / maximum
        self.y_speed = self.y_speed / maximum
        if frames % (30/level) == 0:
            scene.add_object(Projectile(self.rect.centerx, self.rect.centery, (255,0,0), self.x_speed*5, self.y_speed*5))
        super().update()
    def kill(self):
        for i in range(0,20):
            particle_system.add_particle(PhysicsParticle(self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2, (255, 0, 0), random.randint(-10, 10)/5, random.randint(-10, 10)/5, random.randint(40,60)/10))
        shake(2)
        sounds['explosion'].set_volume(random.randint(5,10)/10)
        sounds['explosion'].play()
        super().kill()

class Projectile(GameObject):
    def __init__(self, x, y, color, xVel, yVel,by_player=False):
        super().__init__(x, y, 5, 5, color)
        self.ignore_collision = True
        self.x_speed = xVel
        self.y_speed = yVel
        self.by_player = by_player
        self.glowing = True
    def update(self):
        super().update()
        if self.rect.left <= 0 or self.rect.right >= 800:
            self.kill()
        if self.rect.top <= 0 or self.rect.bottom >= 600:
            self.kill()
    def collision(self, other):
        global score, health
        if self.by_player:
            if other.__class__ == Enemy:
                other.kill()
                self.kill()
                score += 1
        else:
            if other.__class__ == Player:
                self.kill()
                health -= 1*level

class PowerUp(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20, (100, 100, 100))
        self.glowing = True

class PowerUp0(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = textures['powerup0']
        self.ignore_collision = True
    def draw(self, screen):
        super().draw(screen)
        screen.blit(self.image, (self.rect.x, self.rect.y))
    def collision(self, other):
        global health
        if other.__class__ == Player:
            if health < 50:
                health += 25
                notify('+25 health')
            elif health < 75:
                health += 10
                notify('+10 health')
            elif health < 95:
                health += 5
                notify('+5 health')
            elif health < 100:
                health += 1
                notify('+1 health')
            else:
                notify('Max health')
            
            self.kill()

class PowerUp1(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = textures['powerup1']
        self.ignore_collision = True
    def draw(self, screen):
        super().draw(screen)
        screen.blit(self.image, (self.rect.x, self.rect.y))
    def collision(self, other):
        global health
        if other.__class__ == Player:
            player_stats['speed'] += 2
            notify('+2 Speed')
            self.kill()

class PowerUp2(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = textures['powerup2']
        self.ignore_collision = True
    def draw(self, screen):
        super().draw(screen)
        screen.blit(self.image, (self.rect.x, self.rect.y))
    def collision(self, other):
        global health
        if other.__class__ == Player:
            if (player_stats['rate']>10):
                player_stats['rate'] -= 10
                notify('+1 fire rate')
            elif (player_stats['rate']>1):
                player_stats['rate'] -= 1
                notify('+0.1 fire rate')
            self.kill()

class ParticleSystem(GameObject):
    def __init__(self):
        super().__init__(0, 0, 0, 0, (0, 0, 0))
        self.particles = []
    def update(self):
        for particle in self.particles:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)
    def add_particle(self, particle):
        self.particles.append(particle)

class Particle():
    def __init__(self, x, y, color, xVel, yVel, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.x_speed = xVel
        self.y_speed = yVel
        self.lifetime = lifetime
    def update(self):
        self.x += self.x_speed
        self.y += self.y_speed
        self.lifetime -= 0.1
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.lifetime))
        cs = circle_surf((self.color[0]/12,self.color[1]/12,self.color[2]/12), int(self.lifetime)*2)
        screen.blit(cs,(self.x-self.lifetime*2, self.y-self.lifetime*2), special_flags=pygame.BLEND_RGB_ADD)

class PhysicsParticle(Particle):
    def __init__(self, x, y, color, xVel, yVel, lifetime):
        super().__init__(x, y, color, xVel, yVel, lifetime)
    def update(self):
        self.x_speed *= 0.98
        self.y_speed *= 0.98

        self.x += self.x_speed
        if self.check_collision():
            self.x -= self.x_speed
            self.x_speed *= -1
        self.y += self.y_speed
        if self.check_collision():
            self.y -= self.y_speed
            self.y_speed *= -1
        
        self.lifetime -= 0.1
    def check_collision(self):
        rect = pygame.Rect(self.x-self.lifetime/2, self.y-self.lifetime/2, self.lifetime, self.lifetime)
        for obj in scene.objects:
            if rect.colliderect(obj.rect):
                return True
        return False

class Scene:
    def __init__(self):
        self.objects = []
        self.stopped = False
    def add_object(self, obj):
        if self.stopped:
            return
        self.objects.append(obj)
    def remove_object(self, obj):
        if self.stopped:
            return
        if obj in self.objects:
            self.objects.remove(obj)
    def draw(self, screen):
        if self.stopped:
            return
        for obj in self.objects:
            obj.draw(screen)
        for obj in self.objects:
            obj.glow()
    def update(self):
        if self.stopped:
            return
        for obj in self.objects:
            if self.stopped:
                return
            obj.update()
    def check_collision(self):
        if self.stopped:
            return
        for obj in self.objects:
            for other in self.objects:
                if obj != other and obj.check_collision(other):
                    if self.stopped:
                        return
                    obj.collision(other)
                    if (obj.ignore_collision or other.ignore_collision):
                        continue
                    if obj.rect.y < other.rect.y:
                        obj.rect.y = other.rect.y - obj.rect.height
                    elif obj.rect.y > other.rect.y:
                        obj.rect.y = other.rect.y + other.rect.height
                    if obj.rect.x < other.rect.x:
                        obj.rect.x = other.rect.x - obj.rect.width
                    elif obj.rect.x > other.rect.x:
                        obj.rect.x = other.rect.x + other.rect.width
    def check_collision_on_obj(self,obj):
        if self.stopped:
            return
        for other in self.objects:
            if obj != other and obj.check_collision(other):
                if not obj.ignore_collision and not other.ignore_collision:
                    return not obj.ignore_collision and not other.ignore_collision
        return False
    def stop(self):
        self.stopped = True

# End game classes

mousex = 0
mousey = 0

scene = Scene()
player = Player(100, 100)
enemies = []
particle_system = ParticleSystem()
scene.add_object(player)
scene.add_object(particle_system)

notify_text = ''
notify_time = 0
notify_active = False

health = 100

def draw_healthbar(health,color,outline):
    pygame.draw.rect(fb, outline, (0, 0, 102, 22))
    pygame.draw.rect(fb, (0, 0, 0), (1, 1, 100, 20))
    pygame.draw.rect(fb, color, (1, 1, health, 20))
    fb.blit(smallfont.render(str(health), True, (255, 255, 255)), (1, 1))

def draw_manabar(mana,color,outline):
    pygame.draw.rect(fb, outline, (0, 24, 102, 22))
    pygame.draw.rect(fb, (0, 0, 0), (1, 25, 100, 20))
    pygame.draw.rect(fb, color, (1, 25, mana, 20))
    fb.blit(smallfont.render(str(mana), True, (255, 255, 255)), (1, 25))

def notify(text):
    global notify_text, notify_time, notify_active
    notify_text = text
    notify_time = 60
    notify_active = True

def draw_notify():
    global notify_text, notify_time, notify_active
    if notify_active:
        pygame.draw.rect(fb, (255, 0, 255), (800-font.size(notify_text)[0]-10, 0+5, font.size(notify_text)[0]+10, 30))
        fb.blit(font.render(notify_text, True, (255, 255, 255)), (800-font.size(notify_text)[0]-5, 0+5))
        notify_time -= 1
        if notify_time == 0:
            notify_active = False

def button(fb, text, x, y, color, hover_color, on_click):
    global mousex, mousey
    buttonsurf = font.render(text,True,color)
    buttonrect = pygame.Rect(x,y,font.size(text)[0],font.size(text)[1])
    if buttonrect.collidepoint(mousex, mousey):
        buttonsurf = font.render(text,True,hover_color)
        if pygame.mouse.get_pressed()[0]:
            on_click()
    fb.blit(buttonsurf,(x,y))

started = False

def start_game():
    global started
    started = True

while not started:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.MOUSEMOTION:
            mousex, mousey = pygame.mouse.get_pos()
    screen.fill((0,0,0))
    fb.fill((0,0,0))
    for i in range(0,100):
        num = random.randint(0,10)
        particle_system.add_particle(Particle(random.randint(0,800), random.randint(0,600), (num, num, num), random.randint(-1,1), random.randint(-1,1), random.randint(10,100)/10))
    particle_system.update()
    particle_system.draw(fb)
    fb.blit(bigfont.render('Eternity²', True, (255, 255, 255)), (400-bigfont.size('Eternity²')[0]/2, 200))
    button(fb, 'Start', 400-font.size('Start')[0]/2, 300, (255, 255, 255), (128, 128, 128), start_game)
    #fb.blit(font.render('Start', True, (255, 255, 255)), (400-font.size('Start')[0]/2, 300))
    fb.blit(smallfont.render('WASD to move', True, (255, 255, 255)), (400-smallfont.size('WASD to move')[0]/2, 340))
    fb.blit(smallfont.render('Click to shoot', True, (255, 255, 255)), (400-smallfont.size('Click to shoot')[0]/2, 360))
    fb.blit(smallfont.render('Shift to send a burst of projectiles', True, (255, 255, 255)), (400-smallfont.size('Shift to send a burst of projectiles')[0]/2, 380))
    fb.blit(smallfont.render('LControl to go speed', True, (255, 255, 255)), (400-smallfont.size('LControl to go speed')[0]/2, 400))
    screen.blit(fb, (0, 0))
    pygame.display.update()

shake_time = 0
shake_strength = 0
def get_shake_pos():
    global shake_strength, shake_time
    if shake_time > 0:
        if shake_time < shake_strength and shake_strength > 0:
            shake_strength -= 1
        shake_time -= 1
        return random.randint(-shake_strength,shake_strength), random.randint(-shake_strength,shake_strength)
    else:
        shake_strength = 0
    return 0, 0


running = True
frames = 0
level = 1
def restart_game():
    global running, frames, level, player, enemies, health, notify_text, notify_time, notify_active, player_stats, scene, score, particle_system
    running = True
    frames = 0
    level = 1
    score = 0
    scene = Scene()
    player = Player(100, 100)
    particle_system = ParticleSystem()
    scene.add_object(player)
    scene.add_object(particle_system)
    health = 100
    player_stats = {'rate': 30, 'speed': 5, 'mana': 100, 'burst_cooldown': 0}
    enemies = []
    notify_text = ''
    notify_time = 0
    notify_active = False

def shake(strength):
    global shake_strength, shake_time
    shake_strength += strength
    shake_time = 15

pygame.mouse.set_visible(False)
restart = False
while running:
    frames += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
            if scene.stopped:
                restart = True
        if event.type == pygame.MOUSEMOTION:
            mousex = pygame.mouse.get_pos()[0]
            mousey = pygame.mouse.get_pos()[1]
            if mousex < 0:
                pygame.mouse.set_pos(0, mousey)
            if mousey < 0:
                pygame.mouse.set_pos(mousex, 0)
            if mousex > 800:
                pygame.mouse.set_pos(800, mousey)
            if mousey > 600:
                pygame.mouse.set_pos(mousex, 600)
    
    screen.fill((0,0,0))
    fb.fill((0, 0, 0))
    if score < 100*level:
        if frames % ((100*level) - score) == 0:
            num = random.randint(0,10)
            if num < 10:
                enemies.append(Enemy(random.randint(0,800), random.randint(0, 600)))
                scene.add_object(enemies[-1])
            else:
                num = random.randint(0,2)
                if num == 0:
                    scene.add_object(PowerUp0(random.randint(0,800), random.randint(0, 600)))
                elif num == 1:
                    scene.add_object(PowerUp1(random.randint(0,800), random.randint(0,600)))
                elif num == 2:
                    scene.add_object(PowerUp2(random.randint(0,800), random.randint(0,600)))
    else:
        level += 1
    if frames % 2 == 0 and player_stats['mana'] < 100:
        player_stats['mana'] += 1
    
    #if frames % 2 == 0:
    #    particle_system.add_particle(Particle(mousex, mousey, (255, 255, 255), random.randint(-10, 10)/10, random.randint(-10,10)/10, random.randint(10,60)/10))
    scene.update()
    scene.check_collision()
    scene.draw(fb)
    if scene.stopped:
        fb.blit(bigfont.render("Game Over", True, (255, 255, 255)), (400-bigfont.size("Game Over")[0]/2, 200-bigfont.size("Game Over")[1]/2))
        fb.blit(font.render("Score: " + str(score), True, (255, 255, 255)), (400-font.size("Score: " + str(score))[0]/2, 300-font.size("Score: " + str(score))[1]/2))
        fb.blit(font.render("Press Any Key to restart", True, (255, 255, 255)), (400-font.size("Press Any Key to restart")[0]/2, 400-font.size("Press Any Key to restart")[1]/2))
    else:  
        draw_healthbar(health,(255,0,0),(255,255,255))
        draw_manabar(player_stats['mana'],(0,255,255),(255,255,255))
        fb.blit(font.render("Score: " + str(score), True, (255, 255, 255)), (0, 50))
        draw_notify()
    
    screen.blit(fb,get_shake_pos())

    cursor = pygame.transform.scale(textures['cursor'],(32,32))
    if pygame.mouse.get_pressed()[0]:
        cursor = pygame.transform.rotate(cursor, frames*10)

    screen.blit(cursor,(mousex-cursor.get_height()/2,mousey-cursor.get_width()/2))

    #screen.blit(smallfont.render("FPS: " + str(int(clock.get_fps())), True, (255, 255, 255)), (800-smallfont.size("FPS: " + str(int(clock.get_fps())))[0], 0))
    #screen.blit(smallfont.render("Particles: " + str(len(particle_system.particles)), True, (255, 255, 255)), (800-smallfont.size("Particles: " + str(len(particle_system.particles)))[0], 20))
    #screen.blit(smallfont.render("Objects: " + str(len(scene.objects)), True, (255, 255, 255)), (800-smallfont.size("Objects: " + str(len(scene.objects)))[0], 40))
    pygame.display.update()
    if restart:
        restart_game()
        restart = False
    clock.tick(60)