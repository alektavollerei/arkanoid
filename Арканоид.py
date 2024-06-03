import os
import sys
import pygame
import random
import datetime

# функция, отвечающая за загрузку "карты уровня"
def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    return level_map

# функция генерации нового уровня, в неё передаётся "карта уровня"
def generate_level(level):
    x = 0
    y = 0
    k = 0
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 'g':
                b = Brick(x, y)
                bricks.add(b)
                k += 1
            x += 60
        y += 30
        x = 0
    return k

# функция, обрабатывающая столкновение мяча
def collision(obj1, obj2):
    if obj2.vx >= 0:
        xdelta = obj2.rect.right - obj1.rect.left
    elif obj2.vx < 0:
        xdelta = obj1.rect.right - obj2.rect.left
    if obj2.vy >= 0:
        ydelta = obj2.rect.bottom - obj1.rect.top
    elif obj2.vy < 0:
        ydelta = obj1.rect.bottom - obj2.rect.top
    if xdelta > ydelta:
        obj2.vy = -obj2.vy
    elif ydelta > xdelta:
        obj2.vx = -obj2.vx
    elif xdelta == ydelta:
        obj2.vy = -obj2.vy
        obj2.vx = -obj2.vx

# функция, отвечающая за загрузку изображения
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image

# класс кирпича (блока)
class Brick(pygame.sprite.Sprite):

    image = load_image("к.png")
    image = pygame.transform.scale(image, (60, 30))

    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = Brick.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y

    def update(self):
        global BRICKS_COUNT, SCORE
        if pygame.sprite.collide_mask(self, ball):
            sound = pygame.mixer.Sound('data/collision.mp3')
            sound.play()
            collision(self, ball)
            self.kill()
            BRICKS_COUNT -= 1
            SCORE += 5
            
# класс шарика
class Ball(pygame.sprite.Sprite):

    image = load_image("шарик.png")
    image = pygame.transform.scale(image, (25, 25))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Ball.image
        self.check = False
        self.rect = self.image.get_rect()
        self.vx = 0
        self.vy = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = platform.rect.x + platform.rect.width // 2 - 12
        self.rect.y = platform.rect.y - 25

    def update(self):
        global LIVES, RETURN
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
            # при пересечении нижней границы отнимается одна жизнь
            if self.rect.y >= 800 - 25:
                LIVES -= 1
                RETURN = True

        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx
        if self.check is False:
            self.rect.x = platform.rect.x + platform.rect.width // 2 - 12
            self.rect.y = platform.rect.y - 25
        if pygame.sprite.collide_mask(self, platform):
            collision(platform, ball)

# класс стенок
class Border(pygame.sprite.Sprite):

    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)

# класс платформы
class Platform(pygame.sprite.Sprite):

    image = load_image("платформа.png")
    image = pygame.transform.scale(image, (200, 25))

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Platform.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 200
        self.rect.y = 700

    def update(self, *args):
        if args != ():
            x = args[0][0]
            if x > 0:
                delta = self.rect.x + self.rect.width
                if delta + x > 1000:
                    self.rect.x = 1000 - self.rect.width
                else:
                    self.rect.x += x
            elif x < 0:
                delta = self.rect.x
                if abs(x) > delta:
                    self.rect.x = 0
                else:
                    self.rect.x = self.rect.x + x        
# стартовый экран
def start_screen():
    size = width, height = 560, 400
    pygame.display.set_caption('Арканоид')
    screen1 = pygame.display.set_mode(size)
    intro_text = "Нажмите для начала игры"
    fon = pygame.transform.scale(load_image('Escaball.png'), size)
    screen1.blit(fon, (0, 0))
    font = pygame.font.SysFont('kacstbook', 30)
    text_coord = 50
    string_rendered = font.render(intro_text, 1, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 10
    intro_rect.x = 10
    screen1.blit(string_rendered, intro_rect)
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(80)

# экран конца игры
def end_screen():
    if WIN is True:
        sound = pygame.mixer.Sound('data/win.mp3')
        sound.play()
    else:
        sound = pygame.mixer.Sound('data/game over.mp3')
        sound.play()
    size = width, height = 1000, 800
    pygame.display.set_caption('Арканоид')
    screen2 = pygame.display.set_mode(size)
    if WIN is True:
        fon = pygame.transform.scale(load_image('win_screen.png'), size)
    else:
        fon = pygame.transform.scale(load_image('lose_screen.png'), size)
    screen2.blit(fon, (0, 0))
    with open('data/SCORE.txt', 'a') as inp:
        print(str(SCORE), ' - ', str(datetime.datetime.now()),
              file=inp, end='\n')

    with open('data/SCORE.txt', 'r') as outp:
        total = [line.strip() for line in outp]
    total = ["Your last results:"] + total
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in total:
        string_rendered = font.render(line, 1, pygame.Color(76, 187, 23))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 40
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
        clock.tick(80)

# функция рисования на экране окошка счета и счетчика жизни
def draw(screen):
    font = pygame.font.Font(None, 27)
    text = font.render('SCORE: ' + str(SCORE), True, (100, 255, 100))
    text_x = 800
    text_y = 760
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                           text_w + 20, text_h + 20), 1)
    text = font.render('LIVES: ' + str(LIVES), True, (100, 255, 100))
    text_x = 700
    text_y = 760
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                           text_w + 20, text_h + 20), 1)
# далее следует создание главного окна и всех необходимых групп спрайтов,
# а также сам игровой цикл
if __name__ == '__main__':
    pygame.init()
    start_screen()
    size = width, height = 1000, 800
    pygame.display.set_caption('Арканоид')
    screen = pygame.display.set_mode(size)
    screen.fill('black')
    running = True
    fps = 80
    screen_rect = (0, 0, width, height)
    bricks = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    platform = Platform()
    ball = Ball()
    all_sprites.add(ball)
    Border(0, 0, width, 0)
    Border(0, height, width, height)
    Border(0, 0, 0, height)
    Border(width, 0, width, height)
    clock = pygame.time.Clock()
    LIVES = 3
    SCORE = 0
    WIN = False
    CURRENT_LEVEL = 1
    BRICKS_COUNT = generate_level(load_level('level ' +
                                             str(CURRENT_LEVEL) + '.txt'))
    RETURN = False
    draw(screen)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                platform.update(event.rel)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ball.check is False:
                    ball.check = True
                    ball.vx = random.choice([3, 4, 5, 6, 7])
                    ball.vy = 10 - ball.vx
        screen.fill('black')
        draw(screen)
        bricks.update()
        bricks.draw(screen)
        all_sprites.update()
        all_sprites.draw(screen)
        # потеря жизни
        if RETURN is True:
            sound = pygame.mixer.Sound('data/live lost.mp3')
            sound.play()
            bricks = pygame.sprite.Group()
            boosts = pygame.sprite.Group()
            platform.kill()
            platform = Platform()
            ball.check = False
            BRICKS_COUNT = generate_level(load_level(
                'level ' + str(CURRENT_LEVEL) + '.txt'))
            RETURN = False
        # потеря всех трёх жизней
        if LIVES == 0:
            platform.kill()
            platform = Platform()
            bricks = pygame.sprite.Group()
            boosts = pygame.sprite.Group()
            ball.check = False
            CURRENT_LEVEL = 1
            end_screen()
        # ситуация, когда уничтожены все кирпичи (переход на новый уровень)
        if BRICKS_COUNT == 0:
            platform.kill()
            platform = Platform()
            bricks = pygame.sprite.Group()
            boosts = pygame.sprite.Group()
            ball.check = False
            if CURRENT_LEVEL == 3:
                WIN = True
                end_screen()
            else:
                CURRENT_LEVEL += 1
                sound = pygame.mixer.Sound('data/next level.mp3')
                sound.play()
                BRICKS_COUNT = generate_level(load_level(
                    'level ' + str(CURRENT_LEVEL) + '.txt'))
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
