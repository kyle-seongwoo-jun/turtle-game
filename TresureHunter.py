import turtle
import random
import os
import tkinter as tk
import pygame
from dotenv import load_dotenv

class Game(turtle.Turtle):                              # 부모 클래스 (상속)
    def __init__(self):    # 초기화
        turtle.Turtle.__init__(self)                    # 부모 클래스의 초기화 가져오기
        self.penup()
        self.hideturtle()
        self.speed(0)
        self.color("black")
        self.goto(200, 200)
        self.score = 0
        self.is_running = True
        self.is_win = False

        self.showturtle()
        self.speed(1)

    def scoring(self):
        self.clear()
        global jewel_count
        if jewel_count == 0:
            self.goto(0, 0)
            self.write("Success /Score: %d" % self.score, align="center", font=("Arial", 40, "bold"))
            for enemy in game_manager.enemys:
                enemy.run_speed = 0
            game_manager.my.run_speed = 0
            self.is_running = False
            self.is_win = True
        elif self.score < 0:
            self.goto(0, 0)
            self.write("Failed", align="center", font=("Arial", 40, "bold"))
            for enemy in game_manager.enemys:
                enemy.run_speed = 0
            game_manager.my.run_speed = 0
            self.is_running = False
            self.is_win = False
        else:
            self.write("Score :%d" % self.score, align="left")

    def plus_score(self, point: int):
        self.score = self.score + point
        self.scoring()

class My(turtle.Turtle):
    def __init__(self, speed=1.0, has_image=False):
        turtle.Turtle.__init__(self)
        self.penup()
        self.shape("my" if has_image else "turtle")
        self.color("green")
        self.run_speed = speed
        self.speed2 = self.run_speed

    def move(self):
        self.forward(self.run_speed)
        if self.xcor() > 250 and self.heading() == 0:
            self.run_speed = 0
        elif self.xcor() < -250 and self.heading() == 180:
            self.run_speed = 0
        elif self.ycor() > 250 and self.heading() == 90:
            self.run_speed = 0
        elif self.ycor() < -250 and self.heading() == 270:
            self.run_speed = 0
        else:
            self.run_speed = self.speed2

    def collision(self):
        for enemy in game_manager.enemys:
            if self.distance(enemy) < 10:
                enemy.run_speed = 0
                enemy.goto(500, 500)
                game_manager.game.score -= 10

    def up(self):
        self.setheading(90)

    def down(self):
        self.setheading(270)

    def left(self):
        self.setheading(180)

    def right(self):
        self.setheading(0)

class Enemy(turtle.Turtle):
    def __init__(self, speed=1.0, has_image=False):
        turtle.Turtle.__init__(self)
        self.penup()
        self.color(colors[random.randint(0, 5)])
        self.shape("enemy" if has_image else "turtle")
        self.run_speed = speed
        self.goto(random.randint(-250, 250), random.randint(-250, 250))

    def move(self):
        self.forward(self.run_speed)
        if self.xcor() > 250:
            self.setheading(180)
        elif self.xcor() < -250:
            self.setheading(0)
        elif self.xcor() > 250:
            self.setheading(270)
        elif self.ycor() < -250:
            self.setheading(90)

        if random.randint(1, 1000) == 1:
            self.setheading(self.towards(game_manager.my))

colors = ["beige", "yellow", "pink", "orange", "red", "black"]

class Jewel(turtle.Turtle):
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.penup()
        self.color("red")
        self.shape("square")
        self.goto(random.randint(-250, 250), random.randint(-250, 250))

    def twinkle(self):
        self.color(colors[random.randint(0, 5)])

    def eat(self):
        global jewel_count
        if self.distance(game_manager.my) < 15:
            self.goto(500, 500)
            game_manager.game.plus_score(10)
            jewel_count = jewel_count - 1
            if game_manager.hit_sound:
                effect_sound = pygame.mixer.Sound(game_manager.hit_sound)
                effect_sound.play()

def load_image(path: str) -> tk.PhotoImage:
    new_size = (20, 30)
    photo_image = tk.PhotoImage(file=path)
    return photo_image.subsample(int(photo_image.width() / new_size[0]), int(photo_image.height() / new_size[1]))

class GameManager:
    def __init__(self,
                 my_speed: int,
                 enemy_count: int, 
                 enemy_speed: int, 
                 jewel_count: int, 
                 background_image: str | None, 
                 background_music: str | None,
                 my_image: str | None = None,
                 enemy_image: str | None = None,
                 win_music: str | None = None,
                 lose_music: str | None = None,
                 hit_sound: str | None = None,
                ):
        self.screen = turtle.Screen()
        self.screen.title("프로젝트 게임")
        if background_image:
            self.screen.bgpic(background_image)

        pygame.mixer.init()
        self.background_music = background_music
        self.win_music = win_music
        self.lose_music = lose_music
        self.hit_sound = hit_sound
        if background_music:
            pygame.mixer.music.load(background_music)
            pygame.mixer.music.play()

        self.my_speed = my_speed / 10
        self.enemy_count = enemy_count
        self.enemy_speed = enemy_speed / 10
        self.jewel_count = jewel_count
        
        if my_image:
            turtle.register_shape("my", turtle.Shape('image', load_image(my_image)))
        if enemy_image:
            turtle.register_shape("enemy", turtle.Shape('image', load_image(enemy_image)))

        self.my = My(my_speed, has_image=my_image != None)
        self.enemys = [Enemy(enemy_speed, has_image=enemy_image != None) for _ in range(enemy_count)]
        self.game = Game()
        self.jewels = [Jewel() for _ in range(jewel_count)]

    def start(self):
        turtle.onkeypress(self.my.up, "Up")
        turtle.onkeypress(self.my.down, "Down")
        turtle.onkeypress(self.my.left, "Left")
        turtle.onkeypress(self.my.right, "Right")

        turtle.listen()
        self.screen.tracer(0)

        while self.game.is_running:
            self.screen.update()
            self.my.move()
            self.game.scoring()
            self.my.collision()
            for enemy in self.enemys:
                enemy.move()

            for jewel in self.jewels:
                jewel.twinkle()

            for jewel in self.jewels:
                jewel.eat()
        self.screen.update()

        if self.background_music:
            pygame.mixer.music.stop()
        
        if self.game.is_win and self.win_music:
            pygame.mixer.music.load(self.win_music)
            pygame.mixer.music.play()
        elif not self.game.is_win and self.lose_music:
            pygame.mixer.music.load(self.lose_music)
            pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.quit()

load_dotenv()
my_speed = int(os.getenv('MY_SPEED') or 1)
my_image = os.getenv('MY_IMAGE')
enemy_count = int(os.getenv('ENEMY_COUNT') or 1)
enemy_speed = int(os.getenv('ENEMY_SPEED') or 1)
enemy_image = os.getenv('ENEMY_IMAGE')
jewel_count = int(os.getenv('JEWEL_COUNT') or 1)
background_image = os.getenv('BACKGROUND_IMAGE')
background_music = os.getenv('BACKGROUND_MUSIC')
win_music = os.getenv('WIN_MUSIC')
lose_music = os.getenv('LOSE_MUSIC')
hit_sound = os.getenv('HIT_SOUND')

game_manager = GameManager(
    my_speed, 
    enemy_count, 
    enemy_speed, 
    jewel_count, 
    background_image, 
    background_music, 
    my_image, 
    enemy_image,
    win_music,
    lose_music,
    hit_sound,
)
game_manager.start()
