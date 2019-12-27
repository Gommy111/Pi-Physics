import sys
import tkinter
import pygame

floor_height = 70


class Block:
    def __init__(self, location, width, height, start_speeds, mass=None, color=(255, 255, 255)):
        self.location = location
        self.width = width
        self.height = height
        self.speeds = start_speeds
        if mass is None:
            self.mass = self.width*self.height/10
        else:
            self.mass = mass
        self.color = color

    def move(self, update_time):
        for i in range(len(self.location)):
            self.location[i] += self.speeds[i] * update_time

    def collision_block(self, other_block):
        clacker.clack()
        other_block_speeds, self_speeds = list(other_block.speeds), list(self.speeds)
        for i in range(len(other_block_speeds)):
            other_block.speeds[i] = (other_block_speeds[i] * (other_block.mass - self.mass) +
                                     2 * self.mass * self_speeds[i]) / (other_block.mass + self.mass)
            self.speeds[i] = (self_speeds[i] * (self.mass - other_block.mass) +
                              2 * other_block.mass * other_block_speeds[i]) / (other_block.mass + self.mass)

    def draw(self, draw_face):
        pygame.draw.rect(draw_face, self.color, (int(self.location[0]), int(self.location[1]), self.width, self.height))
        pygame_win.blit(comic_sans_20.render(str(self.mass), True, (255, 255, 255)),
                        (int(self.location[0]), int(self.location[1]+self.height)))

    def update_size(self):
        size = int(self.mass**(1/6)*25)
        self.width, self.height = size, size
        global floor_height
        self.location[1] = (window_height - floor_height) - self.height


class Clacker:
    def __init__(self, max_same_time):
        self.channels = max_same_time
        self.channel_index = 0
        pygame.mixer.init()
        pygame.mixer.set_num_channels(self.channels)  # default is 8
        self.effect = pygame.mixer.Sound('clack.wav')

    def clack(self):
        pygame.mixer.Channel(self.channel_index).play(self.effect)
        self.channel_index += 1
        if self.channel_index >= self.channels:
            self.channel_index = 0


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


loop_time = 0
collisions = 0


def update_simulation():
    global loop_time
    global collisions
    time_blocks = ((small_block.location[0] + small_block.width) - large_block.location[0]) /\
                  (large_block.speeds[0] - small_block.speeds[0])
    if small_block.speeds[0] == 0:
        time_edge = -999999
    else:
        time_edge = (small_block.location[0]) / (small_block.speeds[0] * -1)

    if time_blocks <= 0 and time_edge <= 0:
        small_block.move(1)
        large_block.move(1)
        loop_time += 1
    elif time_edge <= 0:
        if time_blocks > 1 and between_animation:
            small_block.move(1)
            large_block.move(1)
            loop_time += 1
        else:
            small_block.move(time_blocks)
            large_block.move(time_blocks)
            loop_time += time_blocks
            small_block.collision_block(large_block)
            collisions += 1
    elif time_blocks <= 0:
        if time_edge > 1 and between_animation:
            small_block.move(1)
            large_block.move(1)
            loop_time += 1
        else:
            small_block.move(time_edge)
            large_block.move(time_edge)
            loop_time += time_edge
            small_block.speeds[0] *= -1
            clacker.clack()
            collisions += 1
    else:
        if time_edge > time_blocks:
            if time_blocks > 1 and between_animation:
                small_block.move(1)
                large_block.move(1)
                loop_time += 1
            else:
                small_block.move(time_blocks)
                large_block.move(time_blocks)
                loop_time += time_blocks
                small_block.collision_block(large_block)
                collisions += 1
        else:
            if time_edge > 1 and between_animation:
                small_block.move(1)
                large_block.move(1)
                loop_time += 1
            else:
                small_block.move(time_edge)
                large_block.move(time_edge)
                loop_time += time_edge
                small_block.speeds[0] *= -1
                clacker.clack()
                collisions += 1

    # There seems to be a rounding error
    # which causes the small block to be lefter than the wall or righter than the large block
    if small_block.location[0] < 0:
        small_block.location[0] = 0
    if small_block.location[0] + small_block.width > large_block.location[0]:
        small_block.location[0] = large_block.location[0] - small_block.width


run = False


def start():
    global run
    run = True


def pause():
    global run
    run = False


small_block, large_block = None, None


def reset():
    global run
    run = False
    global small_block
    global large_block
    small_block = Block([100, 80], 40, 40, [0, 0], mass=float(small_mass_entry.get()), color=(255, 10, 10))
    large_block = Block([300, 70], 60, 60, [-1, 0], mass=float(large_mass_entry.get()), color=(0, 230, 0))
    global collisions
    collisions = 0
    global loop_time
    loop_time = 0


closing = False


def close():
    global closing
    closing = True
    pygame.quit()
    sys.exit()


window_width, window_height = 400, 200
pygame.init()
pygame_win = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
pygame.display.set_caption("Pi Physics")
pygame.font.init()
comic_sans_50 = pygame.font.SysFont('Comic Sans MS', 50)
comic_sans_20 = pygame.font.SysFont('Comic Sans MS', 20)
clacker = Clacker(1)

tkinter_win = tkinter.Tk()
tkinter_win.title("Pi Control")
tkinter_win.geometry("300x200")
tkinter_win.protocol('WM_DELETE_WINDOW', close)
small_entry_text = tkinter.Label(tkinter_win, text="Red's mass:")
small_entry_text.pack()
small_mass_entry = tkinter.Entry(tkinter_win)
small_mass_entry.insert(0, 1)
small_mass_entry.pack()
large_entry_text = tkinter.Label(tkinter_win, text="Green's mass:")
large_entry_text.pack()
large_mass_entry = tkinter.Entry(tkinter_win)
large_mass_entry.insert(0, 100)
large_mass_entry.pack()
speed_text = tkinter.Label(tkinter_win, text="")
speed_text.pack()
start_button = tkinter.Button(tkinter_win, text="Start", command=start)
pause_button = tkinter.Button(tkinter_win, text="Pause", command=pause)
reset_button = tkinter.Button(tkinter_win, text="Reset", command=reset)
reset_button.pack()

between_animation = True

reset()

last_draw = 0
while not closing:
    if isfloat(small_mass_entry.get()) and isfloat(large_mass_entry.get()) and \
            not run and small_block.location[0] < window_width:
        start_button.pack()
    else:
        start_button.pack_forget()
    if isfloat(small_mass_entry.get()):
        small_block.mass = float(small_mass_entry.get())
        small_block.update_size()
    if isfloat(large_mass_entry.get()):
        large_block.mass = float(large_mass_entry.get())
        large_block.update_size()

    if run:
        pause_button.pack()
        update_simulation()
    else:
        pause_button.pack_forget()
        loop_time += 1

    if loop_time > last_draw + 1:
        #  Draw
        pygame_win.fill((0, 0, 0))
        pygame.draw.rect(pygame_win, (99, 99, 99), (0, (window_height - floor_height), window_width, floor_height))
        if 0 <= small_block.speeds[0] <= large_block.speeds[0] and large_block.speeds[0] >= 0:
            pygame_win.blit(comic_sans_50.render("Done", True, (255, 255, 255)), (20, window_height-floor_height+20))
        large_block.draw(pygame_win)
        small_block.draw(pygame_win)
        pygame_win.blit(comic_sans_50.render(str(collisions), True, (255, 255, 255)), (20, 20))
        pygame.display.update()
        pygame.time.delay(int(1000 / 60))
        last_draw = loop_time

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    close()

            if event.type == pygame.VIDEORESIZE:
                window_width, window_height = event.w, event.h
                surface = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)

    tkinter_win.update()
