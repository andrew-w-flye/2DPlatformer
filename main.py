import pygame
import Levels as Lvl

vector = pygame.math.Vector2

pygame.init()
#Set game defaults
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 576
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
FPS = 60
clock = pygame.time.Clock()
tile_map = [Lvl.tile_map_1, Lvl.tile_map_2, Lvl.tile_map_3, Lvl.tile_map_4]
scroll = [0,0]

#Create Game class
class Game():
  def __init__(self, player, ruby_tiles):
    self.level_time = 30
    self.score = 0
    self.lvl_counter = 0
    self.frame_count = 0
    self.current_level_time = self.level_time
    self.ruby_tiles = ruby_tiles
    self.player = player
    create_tiles(tile_map[0])
    self.HUD_font = pygame.font.Font(None, 24)


  def update(self):
    self.frame_count += 1
    if self.frame_count % FPS == 0:
      self.current_level_time -= 1
      self.frame_count = 0

    self.level_finish()
    self.check_collisions()
    self.check_death()

  def draw(self):
    WHITE = (255, 255, 255)
    
    score_text = self.HUD_font.render('Score: ' + str(self.score), True, WHITE)
    score_rect = score_text.get_rect()
    score_rect.topleft = (10,WINDOW_HEIGHT-50)

    time_text = self.HUD_font.render('Time: ' + str(self.current_level_time), True, WHITE)
    time_rect = time_text.get_rect()
    time_rect.topright = (WINDOW_WIDTH-10, WINDOW_HEIGHT-50)

    display_surface.blit(score_text, score_rect)
    display_surface.blit(time_text, time_rect)


  
  def check_collisions(self):
    collision_dict = pygame.sprite.groupcollide(self.player, self.ruby_tiles, False, True)
    if collision_dict:
      for ruby in collision_dict.values():
        self.score += 1

  def level_finish(self):
    if self.score == 3:
      self.level_progress()

  def level_progress(self):
    my_player.kill()
    for tile in main_tile_group:
      tile.kill()
    self.lvl_counter += 1
    create_tiles(tile_map[self.lvl_counter])
    self.score = 0

  def check_death(self):
    if my_player.rect.y > WINDOW_HEIGHT-30:
      my_player.position = vector(my_player.starting_x, my_player.starting_y)
      my_player.velocity = vector(0,0)
      

class Tile(pygame.sprite.Sprite):
  def __init__(self, x, y, image_int, main_group, sub_group=""):
    super().__init__()
    self.x = x
    self.y = y
    if image_int == 1:
      self.image = pygame.image.load('Assets/dirt.png')
    elif image_int == 2:
      self.image = pygame.image.load('Assets/grass.png')
      self.mask = pygame.mask.from_surface(self.image)
      sub_group.add(self)
    elif image_int == 3:
      self.image = pygame.image.load('Assets/water.png')
      sub_group.add(self)
    elif image_int == 5:
      self.image = pygame.image.load('Assets/ruby.png')
      sub_group.add(self)
    elif image_int == 6:
      self.image = pygame.image.load('Assets/grass.png')
      sub_group.add(self)

    main_group.add(self)

    self.rect = self.image.get_rect()
    self.rect.topleft = (x,y)


#Create Player class
class Player(pygame.sprite.Sprite):
  def __init__(self,x,y, grass_tiles, water_tiles, ruby_tiles, wall_tiles):
    super().__init__()
    
    self.image = pygame.image.load('Assets/knight.png')
    self.rect = self.image.get_rect()
    self.rect.bottomleft = (x,y)
    self.starting_x = x
    self.starting_y = y
  

    self.grass_tiles = grass_tiles
    self.water_tiles = water_tiles
    self.ruby_tiles = ruby_tiles
    self.wall_tiles = wall_tiles

    self.position = vector(x,y)
    self.velocity = vector(0,0)
    self.acceleration = vector(0,0)
    self.Accel_x = 2
    self.Friction = 0.15
    self.Accel_y = 1.5
    self.jump_speed = 25

  def update(self):
    
    self.mask = pygame.mask.from_surface(self.image)
    
    self.move()
    self.check_collisions()


  def move(self):
    self.acceleration = vector(0,self.Accel_y)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
      self.acceleration.x = -1*self.Accel_x
    if keys[pygame.K_RIGHT]:
      self.acceleration.x = self.Accel_x


    #Calculate new values based on Physics
    self.acceleration.x -= self.velocity.x*self.Friction
    self.velocity += self.acceleration
    self.position += self.velocity + 0.5*self.acceleration

    #Update new rect 
    scroll[0] = self.velocity.x
    self.rect.bottomleft = self.position
    
  def check_collisions(self):
    #Check for collisions on grass
    collided_platforms = pygame.sprite.spritecollide(self, self.grass_tiles, False, pygame.sprite.collide_mask)
    if collided_platforms:
      if self.velocity.y > 0:
        self.position.y = collided_platforms[0].rect.top + 10
        self.velocity.y = 0
      
  #Check for collisions on water
    if pygame.sprite.spritecollide(self, self.water_tiles, False):
      self.position = vector(self.starting_x, self.starting_y)
      self.velocity = vector(0,0)

    #Check for wall collisions
    collided_walls = pygame.sprite.spritecollide(self, self.wall_tiles, False, pygame.sprite.collide_mask)
    if collided_walls:
      if self.velocity.x > 0:
        self.position.x = collided_walls[0].rect.left - 60
        self.velocity.x = 0
      elif self.velocity.x < 0:
        self.position.x = collided_walls[0].rect.right + 10
        self.velocity.x = 0
  
  def jump(self):
    if pygame.sprite.spritecollide(self, self.grass_tiles, False):
      self.velocity.y = -1*self.jump_speed


#Set up sprite groups

main_tile_group = pygame.sprite.Group()
grass_tile_group = pygame.sprite.Group()
water_tile_group = pygame.sprite.Group()
my_player_group = pygame.sprite.Group()
ruby_tile_group = pygame.sprite.Group()
wall_tile_group = pygame.sprite.Group()

def create_tiles(tile_map_1):
#Iterate through the tile map
  for i in range(len(tile_map_1)):
    for j in range(len(tile_map_1[i])):
      if tile_map_1[i][j] == 1:
        Tile(j*32-scroll[0],i*32,1,main_tile_group)
      elif tile_map_1[i][j] == 2:
        Tile(j*32-scroll[0],i*32,2,main_tile_group,grass_tile_group)
      elif tile_map_1[i][j] == 3:
        Tile(j*32-scroll[0],i*32,3,main_tile_group, water_tile_group)
      elif tile_map_1[i][j] == 4:
        global my_player
        my_player = Player(j*32-scroll[0],i*32+32, grass_tile_group, water_tile_group,ruby_tile_group, wall_tile_group)
        my_player_group.add(my_player)
      elif tile_map_1[i][j] == 5:
        Tile(j*32-scroll[0],i*32,5,main_tile_group, ruby_tile_group)
      elif tile_map_1[i][j] == 6:
        Tile(j*32-scroll[0],i*32,6,main_tile_group, wall_tile_group)


#Load background image
background_image = pygame.image.load("Assets/background.png")
background_rect = background_image.get_rect()
background_rect.topleft=(0,0)

def update_tile():
  for tile in main_tile_group:
    tile.rect.x -= scroll[0]
    tile.rect.y -= scroll[1]

running = True
my_game = Game(my_player_group, ruby_tile_group)

#Main game loop
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_UP:
        my_player.jump()



#Draw Background
  display_surface.blit(background_image,background_rect)
  
#Draw Tiles
  update_tile()
  main_tile_group.draw(display_surface)

#Draw and update player
  my_player_group.update()
  my_player_group.draw(display_surface)

#Update and draw the game
  my_game.update()
  my_game.draw()
  
  pygame.display.update()
  clock.tick(FPS)

pygame.quit()