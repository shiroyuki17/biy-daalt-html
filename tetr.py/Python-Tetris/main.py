import pygame
import random

SCREEN_WIDTH = 300     
SCREEN_HEIGHT = 600    
BLOCK_SIZE = 30         
FPS = 60                           

GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE   
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE 

BLACK = (0, 0, 0)      
GRAY = (128, 128, 128) 
WHITE = (255, 255, 255)

SHAPES = [
    [[0, 1], [1, 1], [2, 1], [3, 1]],   
    [[0, 0], [0, 1], [1, 1], [1, 0]],     
    [[0, 1], [1, 1], [2, 1], [1, 0]],     
    [[0, 1], [1, 1], [1, 0], [2, 0]],    
    [[0, 0], [1, 0], [1, 1], [2, 1]],     
    [[0, 0], [0, 1], [1, 1], [2, 1]],     
    [[0, 1], [1, 1], [2, 1], [2, 0]]       
]

SHAPE_COLORS = [
    (0, 255, 255),  
    (255, 255, 0),
    (128, 0, 128),    
    (0, 255, 0),    
    (255, 0, 0),   
    (0, 0, 255), 
    (255, 127, 0)  
]
class Grid:
    def __init__(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def is_valid_position(self, shape):
        for block in shape.blocks:
            x = shape.x + block[0]  
            y = shape.y + block[1]  

            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return False

            if y >= 0 and self.grid[y][x] != BLACK:
                return False

        return True

    def add_shape(self, shape):
        for block in shape.blocks:
            x = shape.x + block[0]
            y = shape.y + block[1]
            if y >= 0:
                self.grid[y][x] = shape.color

    def clear_full_rows(self):
        full_rows = 0
        for y in range(GRID_HEIGHT - 1, -1, -1):
            if BLACK not in self.grid[y]:
                full_rows += 1
                del self.grid[y] 
                self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        return full_rows

     
class Shape:
    def __init__(self, x, y, type_idx=None):

        if type_idx is None:
            self.type_idx = random.randint(0, len(SHAPES) - 1)
        else:
            self.type_idx = type_idx

        self.blocks = [list(block) for block in SHAPES[self.type_idx]]

        self.color = SHAPE_COLORS[self.type_idx]

        self.x = x
        self.y = y

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1 

    def move_down(self):
        self.y += 1 

    def move_up(self):
        self.y -= 1

    def rotate(self):
        if self.color == (255, 255, 0):
            return

        pivot = self.blocks[1]
        new_blocks = []

        for block in self.blocks:
            rx = block[0] - pivot[0]
            ry = block[1] - pivot[1]
            nx, ny = -ry, rx
            new_blocks.append([nx + pivot[0], ny + pivot[1]])

        self.blocks = new_blocks

    def undo_rotate(self):
        for _ in range(3):
            self.rotate()

def draw_grid(screen, grid_obj):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid_obj.grid[y][x] != BLACK:
                pygame.draw.rect(
                    screen,
                    grid_obj.grid[y][x],
                    (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                )

    for i in range(GRID_WIDTH):
        pygame.draw.line(screen, GRAY, (i * BLOCK_SIZE, 0), (i * BLOCK_SIZE, SCREEN_HEIGHT))
    for i in range(GRID_HEIGHT):
        pygame.draw.line(screen, GRAY, (0, i * BLOCK_SIZE), (SCREEN_WIDTH, i * BLOCK_SIZE))


def draw_shape(screen, shape):
    for block in shape.blocks:
        x = (shape.x + block[0]) * BLOCK_SIZE
        y = (shape.y + block[1]) * BLOCK_SIZE
        if y >= 0:
            pygame.draw.rect(screen, shape.color, (x, y, BLOCK_SIZE, BLOCK_SIZE))

class TetrisGame:
    def __init__(self, screen):
        self.screen = screen
        self.running = True

        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(300, 50)

        self.grid = Grid()

        self.current_shape = Shape(GRID_WIDTH // 2 - 1, 0)

        self.held_shape = None
        self.can_hold = True

        self.fall_time = 0
        self.fall_speed = 200
        self.score = 0
    def run(self):
        while self.running:
            self.fall_time += self.clock.get_rawtime()
            self.clock.tick(FPS)

            self.handle_events()
            self.update()
            self.draw()

    def lock_piece(self):
        self.current_shape.move_up()
        self.grid.add_shape(self.current_shape)
        self.grid.clear_full_rows()

        self.can_hold = True

        self.current_shape = Shape(GRID_WIDTH // 2 - 1, 0)

        if not self.grid.is_valid_position(self.current_shape):
            print("Game Over!")
            self.running = False

    def toggle_hold(self):
        if not self.can_hold:
            return

        if self.held_shape is None:
            self.held_shape = self.current_shape
            self.current_shape = Shape(GRID_WIDTH // 2 - 1, 0)
        else:
            temp_idx = self.current_shape.type_idx
            self.current_shape = Shape(GRID_WIDTH // 2 - 1, 0, self.held_shape.type_idx)
            self.held_shape = Shape(GRID_WIDTH // 2 - 1, 0, temp_idx)

        self.can_hold = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.current_shape.move_left()
                    if not self.grid.is_valid_position(self.current_shape):
                        self.current_shape.move_right()

                elif event.key == pygame.K_RIGHT:
                    self.current_shape.move_right()
                    if not self.grid.is_valid_position(self.current_shape):
                        self.current_shape.move_left()

                elif event.key == pygame.K_UP:
                    self.current_shape.rotate()
                    if not self.grid.is_valid_position(self.current_shape):
                        self.current_shape.undo_rotate()

                elif event.key == pygame.K_DOWN:
                    self.current_shape.move_down()
                    if not self.grid.is_valid_position(self.current_shape):
                        self.current_shape.move_up()
                    else:
                        self.fall_time = 0

                elif event.key == pygame.K_SPACE:
                    while self.grid.is_valid_position(self.current_shape):
                        self.current_shape.move_down()
                    self.lock_piece()

                elif event.key == pygame.K_c:
                    self.toggle_hold()

    def update(self):
        if self.fall_time >= self.fall_speed:
            self.current_shape.move_down()
            if not self.grid.is_valid_position(self.current_shape):
                self.lock_piece()
            self.fall_time = 100

    def draw(self):
        self.screen.fill(BLACK)

        draw_grid(self.screen, self.grid)
        draw_shape(self.screen, self.current_shape)

        if self.held_shape:
            pygame.draw.rect(self.screen, WHITE, (5, 5, 80, 50), 1)
            for block in self.held_shape.blocks:
                x = 20 + block[0] * 15
                y = 20 + block[1] * 15
                pygame.draw.rect(self.screen, self.held_shape.color, (x, y, 14, 14))
        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris - Python 3.12")

    game = TetrisGame(screen)
    game.run()

    pygame.quit()