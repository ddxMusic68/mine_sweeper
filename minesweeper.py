import pygame
import random
pygame.init()
pygame.font.init()

def grid_to_list(r, c, cols):
    return r*cols + c

class Tile():
    # BOARD VARIABLES
    resume = True
    width = 600
    height = 600
    tile_list = []
    tile_grid = []
    grid_rows = 0 # initialised in create_tile_list
    grid_cols = 0 # initialised in create_tile_list
    tile_size = 0 # initialised in create_tile_list
    max_bombs = 0
    FONT = pygame.font.SysFont('awadeeui', 40)
    WIN_FONT = pygame.font.SysFont('awadeeui', 200)


    # BOARD FUNCTIONS
    def create_tile_list(rows, cols): # creates grid
        Tile.grid_rows = rows
        Tile.grid_cols = cols
        for r in range(rows):
            for c in range(cols):
                tile = Tile(r, c)
                Tile.tile_list.append(tile)
        if Tile.height/rows < Tile.width/cols: # takes smallest tile_size between hieght and width
            Tile.tile_size = Tile.width/rows
        else:
            Tile.tile_size = Tile.height/cols

    def check_win():
        text = None
        flagged_bombs = 0
        wrong_flagged = False
        tile: Tile
        for tile in Tile.tile_list:
            if tile.marked and tile.bomb:
                text = Tile.WIN_FONT.render("You Lose!", 1, 'red')
                Tile.resume = False
            elif tile.flagged and tile.bomb:
                flagged_bombs += 1
            if tile.flagged and tile.bomb == False:
                wrong_flagged = True
        if Tile.max_bombs == flagged_bombs and not wrong_flagged:
            text = Tile.WIN_FONT.render("You Win!", 1, 'green')
            Tile.resume = False
        return text

    def update_bombs_near_grid() -> None:
        tile: Tile
        for tile in Tile.tile_list:
            tile.update_bombs_near_tile()

    def draw_tiles(window: pygame.Surface, border_color: tuple = (105, 105, 105), fill_color = (220, 220, 220)):
        tile: Tile
        for tile in Tile.tile_list:
            rect = tile.get_rect()
            pygame.draw.rect(window, border_color, rect)
            rect.height -= 1
            rect.width -= 1 # shrinks rect so it adds a border
            pygame.draw.rect(window, fill_color, rect)
            if not Tile.resume and tile.bomb:
                window.blit(tile.draw_bomb_num(), (rect.centerx - 5, rect.centery - 10))
            elif tile.bombs_near == 0 and tile.marked and tile.bomb == False:
                pygame.draw.rect(window, border_color, rect)
            elif tile.marked or tile.flagged:
                window.blit(tile.draw_bomb_num(), (rect.centerx - 5, rect.centery - 10))

    def add_bombs(starting_point, max_bombs: int) -> None:
        Tile.max_bombs = max_bombs
        new_tile_list = Tile.tile_list.copy()
        row = starting_point.row
        col = starting_point.col
        indeces = []
        for r in range(-2, 2+1):
            for c in range(-2, 2+1):
                index = grid_to_list(r+row, c+col, Tile.grid_cols)
                if index>=0 and index <= (len(Tile.tile_list)-1):
                    indeces.append(index)
        for i in sorted(indeces, reverse=True): # reverse so popping doesnt change position of pop after
            new_tile_list.pop(i)

        for _ in range(max_bombs): # adds bombs in at random till maxbombs
            tile: Tile = new_tile_list[random.randint(0, len(new_tile_list)-1)]
            tile.bomb = True
            new_tile_list.remove(tile)


    # TILE FUNCTIONS
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.bomb = False
        self.flagged = False
        self.marked = False
        self.bombs_near = 0

    def marked_spread(self):
        if self.bombs_near == 0:
            for r in range(-1, 1+1):
                for c in range(-1, 1+1):
                    nr, nc = self.row + r, self.col + c
                    if not (r == 0 and c == 0) and (0 <= nr < Tile.grid_rows) and (0 <= nc < Tile.grid_cols): # if we are not the current tile or out of bounds
                        tile: Tile = Tile.tile_list[grid_to_list(nr, nc, Tile.grid_cols)]
                        if (tile.marked == False) and not tile.bomb:
                            tile.marked = True
                            tile.marked_spread()

    def get_rect(self) -> pygame.Rect:
        tile_size = Tile.tile_size
        return pygame.Rect((self.col*tile_size, self.row*tile_size), (tile_size, tile_size))

    def update_bombs_near_tile(self) -> None:
        bombs = 0
        for r in range(-1, 1+1):
            for c in range(-1, 1+1):
                nr, nc = self.row + r, self.col + c
                if not (r == 0 and c == 0) and (0 <= nr < Tile.grid_rows) and (0 <= nc < Tile.grid_cols): # if we are not the current tile or out of bounds
                    tile: Tile = Tile.tile_list[grid_to_list(nr, nc, Tile.grid_cols)]
                    if tile.bomb:
                        bombs += 1
        self.bombs_near = bombs

    def draw_bomb_num(self):
        if self.flagged:
            text = Tile.FONT.render('F', 1, 'orange')
        elif self.bomb:
            text = Tile.FONT.render('B', 1, 'black')
        else:
            if self.bombs_near == 0:
                text = Tile.FONT.render("0", 1, 'green')
            else:
                text = Tile.FONT.render(str(self.bombs_near), 1, 'red')
        return text


# MAINLOOP
def mainloop():
    Tile.create_tile_list(30, 30) # creates board

    WIDTH, HEIGHT = 600, 600
    window = pygame.display.set_mode((WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    FPS = 60

    first_click = True

    run = True
    while run:
        clock.tick(FPS) # caps framerate
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if Tile.resume: # if game is unpause
                if event.type == pygame.MOUSEBUTTONDOWN:
                    left_click, right_click = pygame.mouse.get_pressed()[0], pygame.mouse.get_pressed()[2]
                    mouse_pos = pygame.mouse.get_pos()
                    x = int(mouse_pos[0]//Tile.tile_size)
                    y = int(mouse_pos[1]//Tile.tile_size)
                    tile: Tile = Tile.tile_list[grid_to_list(y, x, Tile.grid_cols)]
                    if left_click and not tile.flagged:
                        if first_click:
                            Tile.add_bombs(tile, max_bombs=150)
                            Tile.update_bombs_near_grid() # updates bombs
                            first_click = False
                        tile.marked_spread()
                        tile.marked = True
                    if right_click:
                        if tile.flagged:
                            tile.flagged = False
                        elif not tile.marked:
                            tile.flagged = True

        window.fill('black') # refreshes screen
        Tile.draw_tiles(window) # draws tiles & nums
        if not first_click and not Tile.check_win() == None: # check win or loss after bombs spawned in
            window.blit(Tile.check_win(), (0, 0))
        pygame.display.update() # updates screen

    pygame.quit() # quits pygame

if __name__ == "__main__":
    mainloop()

    
# TODO 
# - CLEAN CODE
# - add gui if ur feeling fancy