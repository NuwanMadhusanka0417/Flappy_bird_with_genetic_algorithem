import pygame
import neat
import time
import os
import random
pygame.font.init()

WIN_WIDTH=500
WIN_HEIGHT=800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png"))),]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))
# STAT_FONT = pygame.font.SysFont("comicsans",50)
class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5
    def __init__(self,x,y):
        self.wx = random.uniform(-1,1)
        self.wyt = random.uniform(-1,1)
        self.wyb = random.uniform(-1,1)
        self.bias = random.uniform(-1,1)
        self.fitness = 0
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        d = self.vel*self.tick_count+1.5*self.tick_count**2 # s = ut + (at**2)/2

        if d >16:
            d=16
        if d<0:
            d -= 2
        self.y=self.y+d
        if d<0 or self.y < self.height+50:
            if self.tilt<self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self,win):
        self.img_count += 1
        if self.img_count <self.ANIMATION_TIME:
            self.img =self.IMGS[0]
        elif self.img_count <self.ANIMATION_TIME*2:
            self.img =self.IMGS[1]
        elif self.img_count <self.ANIMATION_TIME*3:
            self.img =self.IMGS[2]
        elif self.img_count <self.ANIMATION_TIME*4:
            self.img =self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4+1:
            self.img =self.IMGS[0]
            self.img_count=0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img,self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x,self.y)).center)
        win.blit(rotated_image,new_rect.topleft)

    def get_mask(self):
        return  pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self,x):
        self.x = x
        self.height = 0
        # self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG,False,True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self,win):
        win.blit(self.PIPE_TOP,(self.x,self.top))
        win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))

    def collide(self,bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x-bird.x,self.top-round(bird.y))
        bottom_offset = (self.x - bird.x,self.bottom-round(bird.y))

        b_point = bird_mask.overlap(bottom_mask,bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if t_point or b_point:
            return True
        return  False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    def draw(self,win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))


def draw_window(win,birds,pipes,base,score):
    win.blit(BG_IMG,(0,0))

    for pipe in pipes:
        pipe.draw(win)
    # text = STAT_FONT.render("Score: "+str(score),1,(255,255,255))
    # win.blit(text,(WIN_WIDTH-10-text.get_width(),10))
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

def crosover(bird1,bird2):
    a = random.randint(0,3)
    if a>5:
        bird = bird1
    else:
        bird = bird2
    b = random.randint(0,3)
    if b==0:
        bird.wx = (bird1.wx+bird2.wx)/2
    elif b==1:
        bird.wyb = (bird1.wyb+bird2.wyb)/2
    elif b == 2:
        bird.wyt = (bird1.wyt+bird2.wyt)/2
    else:
        bird.bias = (bird1.bias+bird2.bias)/2
    return bird
def mutation(bird):
    b = random.randint(0, 3)
    if b == 0:
        bird.wx = random.uniform(-1,1)
    elif b == 1:
        bird.wyb = random.uniform(-1,1)
    elif b == 2:
        bird.wyt = random.uniform(-1,1)
    else:
        bird.bias = random.uniform(-1,1)
    return  bird


def main(N,itteration,prop) :
    birds = []
    for i in range(N):
        birds.append(Bird(230,350))

    S_birds = []
    base = Base(700)

    run =True
    # i = 0
    itt = 0
    while itt<itteration:
        pipes = [Pipe(700)]
        win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        clock = pygame.time.Clock()
        score = 0
        while run:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    run = False
            add_pipe = False
            rem = []
            pipe_ind = 0
            if len(birds) > 0:
                if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                    pipe_ind = 1
            else:
                run = False
                break

            for x, bird in enumerate(birds):
                bird.move()
                bird.fitness += 0.1
                val = bird.y*bird.wx+(bird.y-pipes[pipe_ind].height)*bird.wyt+(bird.y - pipes[pipe_ind].bottom)*bird.wyb+bird.bias
                if val>0:
                    bird.jump()
            for pipe in pipes:
                for x,bird in enumerate(birds):
                    if pipe.collide(bird):
                        birds[x].x = 230
                        birds[x].y = 350
                        S_birds.append(birds[x])
                        birds.pop(x)
                        pass
                    if not pipe.passed and pipe.x < bird.x:
                        pipe.passed = True
                        add_pipe = True
                if pipe.x+pipe.PIPE_TOP.get_width()<0:
                    rem.append(pipe)
                pipe.move()
            if add_pipe:
                score += 1
                pipes.append(Pipe(600))
            for r in rem:
                pipes.remove(r)

            for x, bird in enumerate(birds):
                if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                    birds[x].x=230
                    birds[x].y=350
                    S_birds.append(birds[x])
                    birds.pop(x)

            base.move()

            # i+=1
            draw_window(win,birds,pipes,base,score)

        for m in range(N):
            print("-----------------",m)
            for n in range(N-1):
                print(n)
                if S_birds[n].fitness>S_birds[n+1].fitness:
                    a = S_birds[n]
                    S_birds[n] = S_birds[n+1]
                    S_birds[n+1] =a
        birds =  S_birds[:N//2]
        while len(birds)<N:
            p = random.randint(0,100)
            if p<prop:
                selct_brd = random.randint(0, len(birds) - 1)
                birds.append(mutation(birds[selct_brd]))
            else:
                selct_brd_1 = random.randint(0, len(birds) - 1)
                selct_brd_2 = random.randint(0, len(birds) - 1)
                birds.append(crosover(birds[selct_brd_1],birds[selct_brd_2]))
        run = True
        # pygame.quit()
    # quit()


number_of_birds  = 50
itteration = 10
mut_prop = 10
main(number_of_birds,itteration,mut_prop)


