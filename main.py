#sprite
import pygame
import random
import os

# initialization
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()
FPS = 60  #frequence per second
COLOR = (169, 169, 169)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (227, 245, 136)
WIDTH = 500
HEIGHT = 600
running = True

ROCK_NUMBER = 10

#
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(r"雷霆戰機")


#圖片庫
#loading local picture
background_img = pygame.image.load(os.path.join("img", "background.png")).convert()
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
#rock_img = pygame.image.load(os.path.join("img", "rock.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())
bullets_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
player_mini_image = pygame.transform.scale(player_img, (25, 19))
player_mini_image.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_image)
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("img", "shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("img", "gun.png")).convert()

#字體
font_name = os.path.join("img", "font.ttf")

#音效
shoot_sound = pygame.mixer.Sound(os.path.join("img", "shoot.wav"))
die_sound = pygame.mixer.Sound(os.path.join("img", "rumble.ogg"))
expl_sound = [
pygame.mixer.Sound(os.path.join("img", "expl0.wav")),
pygame.mixer.Sound(os.path.join("img", "expl1.wav"))
]
gun_sound = pygame.mixer.Sound(os.path.join("img", "pow0.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("img", "pow1.wav"))


pygame.mixer.music.load(os.path.join("img", "background.ogg"))
pygame.mixer.music.set_volume(0.2)

#爆炸動畫
expl_animate = dict()
expl_animate['lg'] = []
expl_animate['sm'] = []
expl_animate['player'] = []

for i in range(9):
    expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png"))
    expl_img.set_colorkey(BLACK)
    expl_animate['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_animate['sm'].append(pygame.transform.scale(expl_img, (40, 40)))
    player_expl_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png"))
    player_expl_img.set_colorkey(BLACK)
    expl_animate['player'].append(player_expl_img)

def draw_health(surface, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    OUTLINER = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, RED, fill_rect)
    pygame.draw.rect(surface, WHITE, OUTLINER, 2) #最後一個2是外框參數

def new_rock():
    r = Rock()
    all_sprites.add(r)
    rocks.add(r)

def draw_text(surface, text, fontsize, x, y):
    font = pygame.font.Font(font_name, fontsize)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surface.blit(text_surface, text_rect)

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30*i #間隔多少像素畫一個
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_init():
    screen.blit(background_img, (0, 0))
    draw_text(screen, "太空生存戰", 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, "← → 移動太空飛船 空白鍵發射子彈", 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, "按任意鍵結束畫面",18, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True

            elif event.type == pygame.KEYUP:
                waiting = False
                return False
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, [50,   50])
        player_img.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        #self.rect.x = 200
        #self.rect.y = 200
        self.rect = self.image.get_rect()
        self.radius = 20
        #pygame.draw.circle(self.image, WHITE, self.rect.center, self.radius)
        #self.rect.center = (WIDTH/2, HEIGHT/2)
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 20
        self.speedx = 8
        self.speedy = 5

        self.health = 100
        self.lives = 3
        self.hidden = False

        self.gun = 1
        self.gun_time = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.rect.left < 0:
            self.rect.left = 0

        if self.hidden and pygame.time.get_ticks() - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT - 10

    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs)  #避免失真
        self.image = self.image_ori.copy()
        self.image_ori.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = self.rect.width * 0.4/ 2
        #pygame.draw.circle(self.image, WHITE, self.rect.center, self.radius)
        #self.rect.center = (WIDTH/2, HEIGHT/2)
        self.rect.x = random.randrange(0, WIDTH-self.rect.width)
        self.rect.y = random.randrange(-180, -100 )
        self.speedy = random.randrange(2, 10)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rotate_degree = 3

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.top > HEIGHT or self.rect.left > WIDTH:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)


    def rotate(self):
        self.total_degree += self.rotate_degree
        self.total_degree =  self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)

        #不斷重新定位中心，避免轉動不正常
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullets_img, (15 , 50))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.rect.bottom = y
        self.speedy = -20

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom == 0:
            self.kill()

class explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_animate[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_animate[self.size]):
                self.kill()
            else:
                self.image = expl_animate[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


#adding chars for game
#adding chars for game




#looping the game
show_init = True
score = 0
pygame.mixer.music.play(-1)
while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        players = pygame.sprite.Group()
        powers = pygame.sprite.Group()

        player = Player()
        all_sprites.add(player)
        players.add(player)
        # enemies
        for i in range(ROCK_NUMBER):
            new_rock()
        score = 0



    clock.tick(FPS)  #一秒鐘最多執行迴圈FPS次
    # acquire the input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

            if event.key == pygame.K_ESCAPE:
                pygame.quit()

    ###renew the screen
    all_sprites.update()
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    #True 表示第一個rock要不要刪掉, True 表示第二bullets要不要刪掉
    crushes = pygame.sprite.groupcollide(players, rocks, False, pygame.sprite.collide_circle)
    get_power = pygame.sprite.groupcollide(powers, players, True, False)

    for crush in crushes:
        new_rock()
        player.health -= crush.radius
        expl = explosion(crush.rect.center, 'sm')
        all_sprites.add(expl)



        if player.lives == 0 and not(death_expl.alive()):
            show_init = True


        if player.health <= 0:
            death_expl = explosion(player.rect.center, 'player')
            all_sprites.add(death_expl)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()
            #running = False

    for hit in hits:
        random.choice(expl_sound).play()
        score += hit.radius
        expl = explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9: #掉寶率9成
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()

    for power in get_power:
        if power.type == 'shield':
            shield_sound.play()
            player.health += 20
            if player.health > 100:
                player.health = 100

        elif power.type == 'gun':
            gun_sound.play()
            player.gunup()



    #screen display
    screen.fill(COLOR)
    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)
    draw_text(screen, f"score: {int(score)}", 18, WIDTH-40, 10)
    draw_health(screen, player.health, 20, 10)
    draw_lives(screen, player.lives, player_mini_image, WIDTH/2, 10)
    pygame.display.update() #要有這行才可以跑出顏色









