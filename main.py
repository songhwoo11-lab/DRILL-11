from pico2d import *
import random

from boy import Boy # boy: 모듈 이름, Boy: 클래스 이름
from grass import Grass # grass: 모듈 이름, Grass: 클래스 이름

# Game object class here

pressed_directions = set()


def handle_events():
    global running, pressed_directions

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        elif event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            if event.key not in pressed_directions:
                pressed_directions.add(event.key)
                boy.dir = -1 if event.key == SDLK_LEFT else 1
                boy.face_dir = boy.dir
                if boy.state in ('IDLE', 'SLEEP'):
                    boy.start_running()
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            pressed_directions.discard(event.key)
            if boy.state == 'RUN':
                boy.stop_running()
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and boy.state == 'SLEEP'
        ):
            boy.wake_up()


def reset_world():
    global world
    global boy

    world = []
    pressed_directions.clear()

    grass = Grass()
    world.append(grass)

    boy = Boy()
    world.append(boy)



def update_world():
    for o in world:
        o.update()
    pass


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


running = True

open_canvas()
reset_world()
# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)
# finalization code
close_canvas()
