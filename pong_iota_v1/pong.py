import os
import pygame
import sys
import time
import math
import random
import string
from pygame.locals import * #pygame
import socket
import select
from thread import *
import qrcode #qrcode
from random import SystemRandom
import urllib2
import json
import requests
from iota import Iota, Transaction, TryteString #pyota
import thread

alphabet = u'9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
pygame.init()
os.system('cls' if os.name == 'nt' else 'clear')
mode = 0
difficulty = 5
lifes = 5
FPS = 30

price_cat1= 50000
price_cat2= 100000
price_cat3= 200000
price_cat4= 500000
price_cat5_1= 10000
price_cat5_2= 20000
price_cat5_3= 40000
price_cat5_4= 100000
price_basic= 10000
price_total=0

toggle1 = toggle2 = toggle3 = toggle4 = toggle5 = False
toggle6 = toggle7 = toggle8 = toggle9 = toggle10 = False
toggle11 = toggle12 = toggle13 = toggle14 = toggle15 =False
toggle16 = toggle17 = toggle18 = False

client = False

node = "https://papa.iota.family:14267"
pong_server= "159.69.197.98"
pong_port = 5555
scr_size = (width,height) = (600,400)
clock = pygame.time.Clock()

black = (0,0,0)
white = (255,255,255)
grey = (122,122,122)
red = (255,0,0)
green = (0,150,0)
blue = (0,206,209)
pink = (255,20,147)

screen = pygame.display.set_mode(scr_size)
pygame.display.set_caption('Pong meets IOTA')

def displaytext(text,fontsize,x,y,color):
    font = pygame.font.SysFont('sawasdee', fontsize, True)
    text = font.render(text, 1, color)
    textpos = text.get_rect(centerx=x, centery=y)
    screen.blit(text, textpos)

def cpumove(cpu,ball):
    global difficulty
    if ball.movement[0] > 0:
        if ball.rect.bottom > cpu.rect.bottom + cpu.rect.height/difficulty:
            cpu.movement[1] = 12
        elif ball.rect.top < cpu.rect.top - cpu.rect.height/difficulty:
            cpu.movement[1] = -12
        else:
            cpu.movement[1] = 0
    else:
        cpu.movement[1] = 0

class Paddle(pygame.sprite.Sprite):
    def __init__(self,x,y,sizex,sizey,color):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.sizex = sizex
        self.sizey = sizey
        self.color = color
        self.image = pygame.Surface((sizex,sizey),pygame.SRCALPHA,32)
        self.image = self.image.convert_alpha()
        pygame.draw.rect(self.image,self.color,(0,0,sizex,sizey))
        self.rect = self.image.get_rect()
        self.rect.left = self.x
        self.rect.top = self.y
        self.points = 0
        self.movement = [0,0]

    def checkbounds(self):
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > height:
            self.rect.bottom = height
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > width:
            self.rect.right = width

    def update(self):
        self.rect = self.rect.move(self.movement)
        self.checkbounds()

    def draw(self):
        screen.blit(self.image,self.rect)

class Ball(pygame.sprite.Sprite):
    def __init__(self,x,y,size,color,movement=[0,0]):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.movement = movement
        self.image = pygame.Surface((size,size),pygame.SRCALPHA,32)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image,self.color,(int(self.rect.width/2),int(self.rect.height/2)),int(size/2))
        self.rect.centerx = x
        self.rect.centery = y
        self.maxspeed = 10
        self.score = 0
        self.movement = movement

    def checkbounds(self):
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > height:
            self.rect.bottom = height
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > width:
            self.rect.right = width

    def update(self):

        if self.rect.top == 0 or self.rect.bottom == height:
            self.movement[1] = -1*self.movement[1]
        if self.rect.left == 0:
            self.rect.centerx = width/2
            self.rect.centery = height/2
            self.movement = [random.randrange(-1,2,2)*4,random.randrange(-1,2,2)*4]
            self.score = 1

        if self.rect.right == width:
            self.rect.centerx = width/2
            self.rect.centery = height/2
            self.movement = [random.randrange(-1,2,2)*4,random.randrange(-1,2,2)*4]
            self.score = -1

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

    def draw(self):
        pygame.draw.circle(self.image,self.color,(int(self.rect.width/2),int(self.rect.height/2)),int(self.size/2))
        screen.blit(self.image,self.rect)

def text_objects(text, font):
    textSurface = font.render(text, True, white)
    return textSurface, textSurface.get_rect()

def text_objects_green(text, font):
    textSurface = font.render(text, True, green)
    return textSurface, textSurface.get_rect()

def get_address():
    global pong_server,pong_port
    get_addr = True
    address = ''
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((pong_server, pong_port))

    sockets_list = [sys.stdin, server]

    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])
    while get_addr == True:
        for socks in read_sockets:
            if socks == server:
                message = socks.recv(2048)
                if message != 'Connected to the PONG Server':
                    address = message
                    get_addr = False

    server.close()
    return address

def waiting_for_payment(address_with_checksum,price_total):
    waiting = True
    while waiting == True:
        time.sleep(2)
        global node
        api = Iota(node)
        find_transaction = api.findTransactions(addresses=[bytes(address_with_checksum)])

        try:
            hash_as_bytes = str(bytes(find_transaction["hashes"][0]))
            trytes_call = api.get_trytes([hash_as_bytes])
            trytes = trytes_call['trytes'][0]
            txn = Transaction.from_tryte_string(trytes)
            if txn.value >= price_total:
                waiting = False
        except:
            print("Waiting..")
    os.system('cls' if os.name == 'nt' else 'clear')
    return True

def game_start():
        global red,green,white,blue,pink
        global difficulty,lifes
        global price_cat1,price_cat2,price_cat3,price_cat4,price_total
        global price_cat5_1,price_cat5_2,price_cat5_3,price_cat5_4,price_basic
        global toggle1,toggle2,toggle3,toggle4,toggle5,toggle6,toggle7
        global toggle8,toggle9,toggle10,toggle11,toggle12,toggle13
        global toggle14,toggle15,toggle16,toggle17,toggle18
        price_total = price_total + price_basic
        if toggle1==True or toggle2 == True or toggle3 == True or toggle4 == True:
            price_total=price_cat1+price_total
        if toggle5==True or toggle6 == True or toggle7 == True or toggle8 == True:
            price_total=price_cat2+price_total
        if toggle9==True or toggle10 == True:
            price_total=price_cat3+price_total
        if toggle11==True or toggle12 == True or toggle13 == True or toggle14 == True:
            price_total=price_cat4+price_total
        if toggle15==True:
            price_total=price_cat5_1+price_total
        if toggle16 == True:
            price_total=price_cat5_2+price_total
        if toggle17 == True:
            price_total=price_cat5_3+price_total
        if toggle18 == True:
            price_total=price_cat5_4+price_total
        start_game_singleplayer = False
        gameOver = False

        if toggle9 == True:
            paddle = Paddle(width/10,height/2,width/120,height/5,white)
        elif toggle10 == True:
            paddle = Paddle(width/10,height/2,width/120,height/12,white)
        else:
            paddle=Paddle(width/10,height/2,width/120,height/8,white)

        cpu = Paddle(width - width/10,height/2,width/120,height/8,white)

        if toggle1 == True:
            ball_color=blue
            ball_characteristics = [5,3]
        elif toggle2 == True:
            ball_color=red
            ball_characteristics = [2,6]
        elif toggle3 == True:
            ball_color=green
            ball_characteristics = [6,2]
        elif toggle4 == True:
            ball_color=pink
            ball_characteristics = [3,5]
        else:
            ball_color=white
            ball_characteristics = [4,4]

        if toggle5 == True:
            ball_size = 6
        elif toggle6 == True:
            ball_size = 10
        elif toggle7 == True:
            ball_size = 14
        elif toggle8 == True:
            ball_size = 18
        else:
            ball_size = 12

        if toggle11==True:
            difficulty = 10
        elif toggle12==True:
            difficulty=15
        elif toggle13==True:
            difficulty=20
        elif toggle14==True:
            difficulty=25
        else:
            difficulty=5

        if toggle15==True:
            lifes = lifes + 5
        elif toggle16 == True:
            lifes = lifes +10
        elif toggle17 == True:
            lifes = lifes + 20
        elif toggle18 == True:
            lifes = 10000000000
        else:
            lifes = 5


        ball = Ball(width*0.3,height*0.6,ball_size,ball_color,ball_characteristics)
        pygame.draw.rect(screen,green,(0,3*height/8,width,height/8*2))

        largeText = pygame.font.Font('freesansbold.ttf',20)
        TextSurf, TextRect = text_objects("Creating IOTA Payment Address", largeText)
        TextRect.center = ((width/2),(height/2))
        screen.blit(TextSurf, TextRect)
        pygame.display.update()
        pygame.event.get()
        address_with_checksum=str(get_address())
        address = address_with_checksum[:-9]
        create_qr_code(address_with_checksum,'payment_request_singleplayer.jpg')
        pygame.draw.rect(screen,green,(0,3*height/8,width,height/8*2))
        largeText = pygame.font.Font('freesansbold.ttf',20)
        response = requests.get("https://api-pub.bitfinex.com/v2/tickers?symbols=tIOTUSD")
        obj = response.json()
        json_dumps = json.dumps(obj)
        iota_price =  float(json.loads(json_dumps)[0][7])

        screen.fill(green)
        TextSurf, TextRect = text_objects("payment process..", largeText)
        TextRect.center = ((width/2),(width/8))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("Total price: "+str(float(price_total)/1000000)+"Mi ("+str(float(iota_price)*float(price_total)/1000000)+" USD)", largeText)
        TextRect.center = ((width/2),(height/3))
        screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("Basic price per game: "+str(float(price_basic)/1000000)+"Mi ("+str(float(iota_price)*float(price_basic)/1000000)+" USD)", largeText)
        TextRect.center = ((width/2),(height/3+20))
        screen.blit(TextSurf, TextRect)

        payment_request_singleplayer_img = pygame.image.load("payment_request_singleplayer.jpg")
        payment_request_singleplayer_img = pygame.transform.scale(payment_request_singleplayer_img, (int(width*0.21), int(width*0.21)))
        screen.blit(payment_request_singleplayer_img,(int(width/2-0.5*0.21*width),int(height/3+0.21*0.5*width)))
        pygame.display.update()
        pygame.event.get()

        waiting_for_payment(address,mode)
        pygame.draw.rect(screen,green,(0,3*height/8,width,height/8*2))
        largeText = pygame.font.Font('freesansbold.ttf',20)
        TextSurf, TextRect = text_objects("loading..", largeText)
        TextRect.center = ((width/2),(height/2))
        screen.blit(TextSurf, TextRect)
        pygame.display.update()
        pygame.event.get()
        while not gameOver:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        paddle.movement[1] = -12
                    elif event.key == pygame.K_DOWN:
                        paddle.movement[1] = 12
                if event.type == pygame.KEYUP:
                    paddle.movement[1] = 0

            cpumove(cpu,ball)

            screen.fill(black)
            paddle.draw()
            cpu.draw()
            ball.draw()

            displaytext(str(paddle.points)+"/"+str(lifes),20,width/8,25,(255,255,255))
            displaytext(str(cpu.points)+"/"+str(lifes),20,width - width/8,25,(255,255,255))

            if pygame.sprite.collide_mask(paddle,ball):
                ball.movement[0] = -1*ball.movement[0]
                ball.movement[1] = ball.movement[1] - int(0.1*random.randrange(5,10)*paddle.movement[1])
                if ball.movement[1] > ball.maxspeed:
                    ball.movement[1] = ball.maxspeed
                if ball.movement[1] < -1*ball.maxspeed:
                    ball.movement[1] = -1*ball.maxspeed

            if pygame.sprite.collide_mask(cpu,ball):
                ball.movement[0] = 1 + ball.movement[0]
                ball.movement[1] = 1 + ball.movement[1]
                ball.maxspeed = ball.maxspeed+1

                ball.movement[0] = -1*(ball.movement[0])
                ball.movement[1] = (ball.movement[1]) - int(0.1*random.randrange(5,10)*cpu.movement[1])
                if ball.movement[1] > ball.maxspeed:
                    ball.movement[1] = ball.maxspeed
                if ball.movement[1] < -1*ball.maxspeed:
                    ball.movement[1] = -1*ball.maxspeed

            if ball.score == 1:
                cpu.points += 1
                ball.score = 0
            elif ball.score == -1:
                paddle.points += 1
                ball.score = 0
            if cpu.points== lifes or paddle.points==lifes:
                if cpu.points==lifes:
                    ball.movement[1]= 0
                    ball.movement[0]=0
                    pygame.draw.rect(screen,red,(0,1*height/4,width,height/4*2))
                    largeText = pygame.font.Font('freesansbold.ttf',20)
                    TextSurf, TextRect = text_objects("YOU LOST", largeText)
                    TextRect.center = ((width/2),(height/2))
                    screen.blit(TextSurf, TextRect)
                    largeText = pygame.font.Font('freesansbold.ttf',10)
                    TextSurf, TextRect = text_objects("Press C to continue", largeText)
                    TextRect.center = ((width/2),(height/2+0.15*height))
                    screen.blit(TextSurf, TextRect)
                    pygame.display.update()

                    game_lost_singleplayer = True
                    while game_lost_singleplayer:
                        pygame.event.pump()
                        pressed = pygame.key.get_pressed()
                        if pressed[pygame.K_c]:
                            game_lost_singleplayer = False
                            paddle.points = 0
                            cpu.points = 0
                            gameOver=True
                            game_menu()
                if paddle.points==lifes:
                    ball.movement[1]= 0
                    ball.movement[0]=0
                    pygame.draw.rect(screen,green,(0,1*height/4,width,height/4*2))
                    largeText = pygame.font.Font('freesansbold.ttf',20)
                    TextSurf, TextRect = text_objects("YOU WON", largeText)
                    TextRect.center = ((width/2),(height/2))
                    screen.blit(TextSurf, TextRect)
                    largeText = pygame.font.Font('freesansbold.ttf',10)
                    TextSurf, TextRect = text_objects("Press C to continue", largeText)
                    TextRect.center = ((width/2),(height/2+0.15*height))
                    screen.blit(TextSurf, TextRect)
                    pygame.display.update()
                    game_won_singleplayer = True
                    while game_won_singleplayer:
                        pygame.event.pump()
                        pressed = pygame.key.get_pressed()
                        if pressed[pygame.K_c]:
                            game_won_singleplayer = False
                            paddle.points = 0
                            cpu.points = 0
                            gameOver=True
                            game_menu()

            while start_game_singleplayer==False:
                largeText = pygame.font.Font('freesansbold.ttf',20)
                TextSurf, TextRect = text_objects("Press 'c' to start the game", largeText)
                TextRect.center = ((width/2),(height/2))
                screen.blit(TextSurf, TextRect)
                pygame.display.update()
                while start_game_singleplayer==False:
                        pygame.event.pump()
                        pressed = pygame.key.get_pressed()
                        if pressed[pygame.K_c]:
                            start_game_singleplayer=True


            paddle.update()
            ball.update()
            cpu.update()

            pygame.display.update()

            clock.tick(FPS)
            time.sleep(0.01)

def game_intro():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    intro = True
    screen.fill(black)
    largeText = pygame.font.Font('freesansbold.ttf',50)
    TextSurf, TextRect = text_objects("PONG", largeText)
    TextRect.center = ((width/2),(height/5))
    screen.blit(TextSurf, TextRect)
    largeText = pygame.font.Font('freesansbold.ttf',30)
    TextSurf, TextRect = text_objects("meets", largeText)
    TextRect.center = ((width/2),(height/5+70))
    screen.blit(TextSurf, TextRect)
    IOTA_LOGO_img = pygame.image.load("IOTA.png")
    screen.blit(IOTA_LOGO_img,(int(width/2-125),int(height*0.5)))
    pygame.display.update()
    pygame.event.get()
    largeText = pygame.font.Font('freesansbold.ttf',50)

    clock.tick(FPS)
    if os.path.exists('pong.conf')==False:
        f = open("pong.conf","w+")
        generator = SystemRandom()
        random_seed=u''.join(generator.choice(alphabet) for _ in range(81))
        f.write("SEED:"+str(random_seed))
        f.close()
    time.sleep(5)

def create_qr_code(address_with_checksum,filename):
    qr = qrcode.QRCode(
        version = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_H,
        box_size = 2,
        border = 4,
    )
    data = "{\"address\":\""+address_with_checksum+"\",\"amount\":"+str(price_total)+",\"message\":"+" \"\"}"
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image()
    qr_img.save(filename)
    del qr



def game_menu():
    menu = True
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        screen.fill(black)
        largeText = pygame.font.Font('freesansbold.ttf',30)
        TextSurf, TextRect = text_objects("Please press a key", largeText)
        TextRect.center = ((width/2),(width/15))
        screen.blit(TextSurf, TextRect)

        largeText = pygame.font.Font('freesansbold.ttf',20)
        TextSurf, TextRect = text_objects("A - Start game", largeText)
        TextRect.center = ((width/2),(width/15+50))
        screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("B - Shop", largeText)
        TextRect.center = ((width/2),(width/15+100))
        screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("E - Exit", largeText)
        TextRect.center = ((width/2),(width/15+150))
        screen.blit(TextSurf, TextRect)

        largeText = pygame.font.Font('freesansbold.ttf',14)
        TextSurf, TextRect = text_objects("If you liked this game, please consider to leave a donation", largeText)
        TextRect.center = ((width/2),(height-20))
        screen.blit(TextSurf, TextRect)
        payment_request_singleplayer_img = pygame.image.load("donation_address.png")
        payment_request_singleplayer_img = pygame.transform.scale(payment_request_singleplayer_img, (int(width*0.18), int(width*0.18)))
        screen.blit(payment_request_singleplayer_img,(int(width/2-0.5*0.15*width),int(height/2+0.15*0.5*width)))
        pygame.display.update()


        clock.tick(FPS)
        menu_var_2 = True
        while menu_var_2:
            pygame.event.pump()
            pressed = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            if pressed[pygame.K_a]:
                menu_var_2=False
                menu = False
                game_start()
            if pressed[pygame.K_b]:
                menu_var_2=False
                menu = False
                shop_start()
            if pressed[pygame.K_e]:
                quit()
            time.sleep(0.1)
        time.sleep(0.1)

def get_ball_position_multiplayer(server,opponent_id):
    #while True:
        message = "get"
    #    server.send(str(opponent_id)+' '+message)
        time.sleep(1)

def shop_start():
    global toggle1,toggle2,toggle3,toggle4,toggle5,toggle6,toggle7
    global toggle8,toggle9,toggle10,toggle11,toggle12,toggle13
    global toggle14,toggle15,toggle16,toggle17,toggle18
    toggle1=toggle2=toggle3=toggle4=toggle5=toggle6=toggle7=False
    toggle8=toggle9=toggle10=toggle11=toggle12=toggle13=False
    toggle14=toggle15=toggle16=toggle17=toggle18
    screen.fill(black)
    ball0 = Ball(width*0.3,height*0.3,6,white,[2,4])
    ball1 = Ball(width*0.3,height*0.4,10,white,[6,4])
    ball2 = Ball(width*0.3,height*0.5,14,white,[4,2])
    ball3 = Ball(width*0.3,height*0.6,18,white,[4,6])
    ball4 = Ball(width*0.1,height*0.3,12,blue,[4,4])
    ball5 = Ball(width*0.1,height*0.4,12,red,[4,4])
    ball6 = Ball(width*0.1,height*0.5,12,green,[4,4])
    ball7 = Ball(width*0.1,height*0.6,12,pink,[4,4])
    paddle0 = Paddle(width*0.5,height*0.29,width/120,height/5,white)
    paddle1 = Paddle(width*0.5,height*0.55,width/120,height/12,white)
    ball0.draw()
    ball1.draw()
    ball2.draw()
    ball3.draw()
    ball4.draw()
    ball5.draw()
    ball6.draw()
    ball7.draw()
    paddle0.draw()
    paddle1.draw()
    largeText = pygame.font.Font('freesansbold.ttf',15)
    TextSurf, TextRect = text_objects(str(float(price_cat1)/1000000)+"Mi", largeText)
    TextRect.center = ((width*0.1),(height*0.2))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- A", largeText)
    TextRect.center = ((width*0.1+30),(height*0.3))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- B", largeText)
    TextRect.center = ((width*0.1+30),(height*0.4))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- C", largeText)
    TextRect.center = ((width*0.1+30),(height*0.5))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- D", largeText)
    TextRect.center = ((width*0.1+30),(height*0.6))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects(str(float(price_cat2)/1000000)+"Mi", largeText)
    TextRect.center = ((width*0.3),(height*0.2))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- E", largeText)
    TextRect.center = ((width*0.3+30),(height*0.3))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- F", largeText)
    TextRect.center = ((width*0.3+30),(height*0.4))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- G", largeText)
    TextRect.center = ((width*0.3+30),(height*0.5))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- H", largeText)
    TextRect.center = ((width*0.3+30),(height*0.6))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects(str(float(price_cat3)/1000000)+"Mi", largeText)
    TextRect.center = ((width*0.5),(height*0.2))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- I", largeText)
    TextRect.center = ((width*0.5+30),(height*0.29+height/10))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- J", largeText)
    TextRect.center = ((width*0.5+30),(height*0.55+height/24))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects(str(float(price_cat4)/1000000)+"Mi", largeText)
    TextRect.center = ((width*0.75),(height*0.2))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("MEDIUM", largeText)
    TextRect.center = ((width*0.75),(height*0.3))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("HARD", largeText)
    TextRect.center = ((width*0.75),(height*0.4))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("VERY HARD", largeText)
    TextRect.center = ((width*0.75),(height*0.5))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("UNBEATABLE", largeText)
    TextRect.center = ((width*0.75),(height*0.6))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- K", largeText)
    TextRect.center = ((width*0.75+90),(height*0.3))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- L", largeText)
    TextRect.center = ((width*0.75+90),(height*0.4))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- M", largeText)
    TextRect.center = ((width*0.75+90),(height*0.5))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("- N", largeText)
    TextRect.center = ((width*0.75+90),(height*0.6))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("+5 lifes", largeText)
    TextRect.center = ((width*0.1),(height*0.75))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects(str(float(price_cat5_1)/1000000)+"Mi", largeText)
    TextRect.center = ((width*0.1),(height*0.8))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("+10 lifes", largeText)
    TextRect.center = ((width*0.3),(height*0.75))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects(str(float(price_cat5_2)/1000000)+"Mi", largeText)
    TextRect.center = ((width*0.3),(height*0.8))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("+20 lifes", largeText)
    TextRect.center = ((width*0.5),(height*0.75))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects(str(float(price_cat5_3)/1000000)+"Mi", largeText)
    TextRect.center = ((width*0.5),(height*0.8))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("-1-", largeText)
    TextRect.center = ((width*0.1),(height*0.70))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("-2-", largeText)
    TextRect.center = ((width*0.3),(height*0.7))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("-3-", largeText)
    TextRect.center = ((width*0.5),(height*0.70))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("-4-", largeText)
    TextRect.center = ((width*0.75),(height*0.7))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("infinity lifes", largeText)
    TextRect.center = ((width*0.75),(height*0.75))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects(str(float(price_cat5_4)/1000000)+"Mi", largeText)
    TextRect.center = ((width*0.75),(height*0.8))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("To leave press ENTER", largeText)
    TextRect.center = ((width/2),(height-20))
    screen.blit(TextSurf, TextRect)
    TextSurf, TextRect = text_objects("To clear selection press backspace", largeText)
    TextRect.center = ((width/2),(height-40))
    screen.blit(TextSurf, TextRect)

    largeText = pygame.font.Font('freesansbold.ttf',15)
    TextSurf, TextRect = text_objects("PONG meets IOTA - Micropayment Shop", largeText)
    TextRect.center = ((width/2),(40))
    screen.blit(TextSurf, TextRect)
    pygame.display.update()
    pygame.event.get()
    shop_var=True
    time.sleep(0.5)
    while shop_var:

        pygame.event.pump()
        pressed = pygame.key.get_pressed()


        if pressed[pygame.K_RETURN]:
            shop_var=False
            game_menu()

        if pressed[pygame.K_BACKSPACE]:
            clear_select_shop_cat_1()
            clear_select_shop_cat_2()
            clear_select_shop_cat_3()
            clear_select_shop_cat_4()
            clear_select_shop_cat_5()
            toggle1=toggle2=toggle3=toggle4=toggle5=toggle6=False
            toggle7=toggle8=toggle9=toggle10=toggle11=toggle12=False
            toggle13=toggle14=toggle15=toggle16=toggle17=toggle18=False


        if pressed[pygame.K_a]:
            toggle1=True
            toggle2 =toggle3 = toggle4=False
            clear_select_shop_cat_1()
            TextSurf, TextRect = text_objects_green("- A", largeText)
            TextRect.center = ((width*0.1+30),(height*0.3))
            screen.blit(TextSurf, TextRect)


        if pressed[pygame.K_b]:
            toggle2=True
            toggle1=toggle3=toggle4=False
            clear_select_shop_cat_1()
            TextSurf, TextRect = text_objects_green("- B", largeText)
            TextRect.center = ((width*0.1+30),(height*0.4))
            screen.blit(TextSurf, TextRect)
        if pressed[pygame.K_c]:
            toggle3=True
            toggle1=toggle2=toggle4=False
            clear_select_shop_cat_1()
            TextSurf, TextRect = text_objects_green("- C", largeText)
            TextRect.center = ((width*0.1+30),(height*0.5))
            screen.blit(TextSurf, TextRect)
        if pressed[pygame.K_d]:
            toggle4=True
            toggle1=toggle2=toggle3=False
            clear_select_shop_cat_1()
            TextSurf, TextRect = text_objects_green("- D", largeText)
            TextRect.center = ((width*0.1+30),(height*0.6))
            screen.blit(TextSurf, TextRect)

        if pressed[pygame.K_e]:
            toggle5=True
            toggle6=toggle7=toggle8=False
            clear_select_shop_cat_2()
            TextSurf, TextRect = text_objects_green("- E", largeText)
            TextRect.center = ((width*0.3+30),(height*0.3))
            screen.blit(TextSurf, TextRect)
        if pressed[pygame.K_f]:
            toggle6=True
            toggle5=toggle7=toggle8=False
            clear_select_shop_cat_2()
            TextSurf, TextRect = text_objects_green("- F", largeText)
            TextRect.center = ((width*0.3+30),(height*0.4))
            screen.blit(TextSurf, TextRect)
        if pressed[pygame.K_g]:
            toggle7=True
            toggle5=toggle6=toggle8=False
            clear_select_shop_cat_2()
            TextSurf, TextRect = text_objects_green("- G", largeText)
            TextRect.center = ((width*0.3+30),(height*0.5))
            screen.blit(TextSurf, TextRect)
        if pressed[pygame.K_h]:
            toggle8=True
            toggle5=toggle6=toggle7=False
            clear_select_shop_cat_2()
            TextSurf, TextRect = text_objects_green("- H", largeText)
            TextRect.center = ((width*0.3+30),(height*0.6))
            screen.blit(TextSurf, TextRect)

        if pressed[pygame.K_i]:
            toggle9=True
            toggle10=False
            clear_select_shop_cat_3()
            TextSurf, TextRect = text_objects_green("- I", largeText)
            TextRect.center = ((width*0.5+30),(height*0.29+height/10))
            screen.blit(TextSurf, TextRect)
        if pressed[pygame.K_j]:
            toggle10=True
            toggle9=False
            clear_select_shop_cat_3()
            TextSurf, TextRect = text_objects_green("- J", largeText)
            TextRect.center = ((width*0.5+30),(height*0.55+height/24))
            screen.blit(TextSurf, TextRect)

        if pressed[pygame.K_k]:
            toggle11=True
            toggle12=toggle13=toggle14=False
            clear_select_shop_cat_4()
            TextSurf, TextRect = text_objects_green("- K", largeText)
            TextRect.center = ((width*0.75+90),(height*0.3))
            screen.blit(TextSurf, TextRect)
        if pressed[pygame.K_l]:
            toggle12=True
            toggle11=toggle13=toggle14=False
            clear_select_shop_cat_4()
            TextSurf, TextRect = text_objects_green("- L", largeText)
            TextRect.center = ((width*0.75+90),(height*0.4))
            screen.blit(TextSurf, TextRect)
        if pressed[pygame.K_m]:
            toggle13=True
            toggle11=toggle12=toggle14=False
            clear_select_shop_cat_4()
            TextSurf, TextRect = text_objects_green("- M", largeText)
            TextRect.center = ((width*0.75+90),(height*0.5))
            screen.blit(TextSurf, TextRect)
        if pressed[pygame.K_n]:
            toggle14=True
            toggle11=toggle12=toggle13=False
            clear_select_shop_cat_4()
            TextSurf, TextRect = text_objects_green("- N", largeText)
            TextRect.center = ((width*0.75+90),(height*0.6))
            screen.blit(TextSurf, TextRect)

        if pressed[pygame.K_1]:
            toggle15=True
            toggle16=toggle17=toggle18=False
            clear_select_shop_cat_5()
            TextSurf, TextRect = text_objects_green("-1-", largeText)
            TextRect.center = ((width*0.1),(height*0.70))
            screen.blit(TextSurf, TextRect)
        if pressed[pygame.K_2]:
            toggle16=True
            toggle15=toggle17=toggle18=False
            clear_select_shop_cat_5()
            TextSurf, TextRect = text_objects_green("-2-", largeText)
            TextRect.center = ((width*0.3),(height*0.7))
            screen.blit(TextSurf, TextRect)
        if pressed[pygame.K_3]:
            toggle17=True
            toggle15=toggle16=toggle18=False
            clear_select_shop_cat_5()
            TextSurf, TextRect = text_objects_green("-3-", largeText)
            TextRect.center = ((width*0.5),(height*0.70))
            screen.blit(TextSurf, TextRect)
        if pressed[pygame.K_4]:
            toggle18=True
            toggle15=toggle16=toggle17=False
            clear_select_shop_cat_5()
            TextSurf, TextRect = text_objects_green("-4-", largeText)
            TextRect.center = ((width*0.75),(height*0.7))
            screen.blit(TextSurf, TextRect)

        pygame.display.update()
        pygame.event.get()

def clear_select_shop_cat_1():
        largeText = pygame.font.Font('freesansbold.ttf',15)
        TextSurf, TextRect = text_objects("- A", largeText)
        TextRect.center = ((width*0.1+30),(height*0.3))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("- B", largeText)
        TextRect.center = ((width*0.1+30),(height*0.4))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("- C", largeText)
        TextRect.center = ((width*0.1+30),(height*0.5))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("- D", largeText)
        TextRect.center = ((width*0.1+30),(height*0.6))
        screen.blit(TextSurf, TextRect)

def clear_select_shop_cat_2():
        largeText = pygame.font.Font('freesansbold.ttf',15)
        TextSurf, TextRect = text_objects("- E", largeText)
        TextRect.center = ((width*0.3+30),(height*0.3))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("- F", largeText)
        TextRect.center = ((width*0.3+30),(height*0.4))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("- G", largeText)
        TextRect.center = ((width*0.3+30),(height*0.5))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("- H", largeText)
        TextRect.center = ((width*0.3+30),(height*0.6))
        screen.blit(TextSurf, TextRect)

def clear_select_shop_cat_3():
        largeText = pygame.font.Font('freesansbold.ttf',15)
        TextSurf, TextRect = text_objects("- I", largeText)
        TextRect.center = ((width*0.5+30),(height*0.29+height/10))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("- J", largeText)
        TextRect.center = ((width*0.5+30),(height*0.55+height/24))
        screen.blit(TextSurf, TextRect)

def clear_select_shop_cat_4():
        largeText = pygame.font.Font('freesansbold.ttf',15)
        TextSurf, TextRect = text_objects("- K", largeText)
        TextRect.center = ((width*0.75+90),(height*0.3))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("- L", largeText)
        TextRect.center = ((width*0.75+90),(height*0.4))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("- M", largeText)
        TextRect.center = ((width*0.75+90),(height*0.5))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("- N", largeText)
        TextRect.center = ((width*0.75+90),(height*0.6))
        screen.blit(TextSurf, TextRect)

def clear_select_shop_cat_5():
        largeText = pygame.font.Font('freesansbold.ttf',15)
        TextSurf, TextRect = text_objects("-1-", largeText)
        TextRect.center = ((width*0.1),(height*0.70))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("-2-", largeText)
        TextRect.center = ((width*0.3),(height*0.7))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("-3-", largeText)
        TextRect.center = ((width*0.5),(height*0.70))
        screen.blit(TextSurf, TextRect)
        TextSurf, TextRect = text_objects("-4-", largeText)
        TextRect.center = ((width*0.75),(height*0.7))
        screen.blit(TextSurf, TextRect)


def start_multiplayer():
    global client
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(("159.69.197.98", 5555))

    screen.fill(black)
    largeText = pygame.font.Font('freesansbold.ttf',20)
    TextSurf, TextRect = text_objects("PONGIOTA Multiplayer Instructions", largeText)
    TextRect.center = ((width/2),(40))
    screen.blit(TextSurf, TextRect)
    largeText = pygame.font.Font('freesansbold.ttf',15)
    TextSurf, TextRect = text_objects("Enter your Opponents ID into the Terminal", largeText)
    TextRect.center = ((width/2),(40+50))
    screen.blit(TextSurf, TextRect)
    pygame.display.update()
    pygame.event.get()
    opponent_id = str(raw_input("Opponent ID:"))
    print opponent_id
    sockets_list = [sys.stdin, server]

    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

    thread.start_new_thread(start_multiplayer_server, (opponent_id,server, ) )
    screen.fill(black)
    clock.tick(FPS)
    largeText = pygame.font.Font('freesansbold.ttf',20)
    TextSurf, TextRect = text_objects("PONGIOTA Multiplayer Instructions", largeText)
    TextRect.center = ((width/2),(40))
    screen.blit(TextSurf, TextRect)
    largeText = pygame.font.Font('freesansbold.ttf',15)
    TextSurf, TextRect = text_objects("waiting for Opponent..", largeText)
    TextRect.center = ((width/2),(40+50))
    screen.blit(TextSurf, TextRect)
    pygame.display.update()
    pygame.event.get()
    while client == False:
        print client
        time.sleep(1)
    largeText = pygame.font.Font('freesansbold.ttf',15)
    TextSurf, TextRect = text_objects("Opponent found!", largeText)
    TextRect.center = ((width/2),(40+50))
    screen.blit(TextSurf, TextRect)
    pygame.display.update()
    pygame.event.get()
    time.sleep(5)

def main():
    game_intro()
    game_menu()

main()
