#!/usr/bin/env python3
import curses
import time
import random

TIME_STEP_LEFT_RIGHT = 200
"""Time step for a left or right move, in milliseconds."""

TIME_STEP_UP_DOWN = round(TIME_STEP_LEFT_RIGHT * 10/6)
"""Time step for a up or down move, in milliseconds."""
# todo: make TIME_STEP stuff better (e.g. would be nice to set just one number)

STDSCR = None
"""Set when main is called."""

UP_KEY = curses.KEY_UP
DOWN_KEY = curses.KEY_DOWN
LEFT_KEY = curses.KEY_LEFT
RIGHT_KEY = curses.KEY_RIGHT
EMPTY_CH = b" "
HEAD_CH = b"s"
DEAD_CH = b"x"
FOOD_CH = b"o"
TAIL_CHS = {
    UP_KEY: {
        UP_KEY: "│",
        DOWN_KEY: "│",
        LEFT_KEY: "┐",
        RIGHT_KEY: "┌"
    },
    DOWN_KEY: {
        UP_KEY: "│",
        DOWN_KEY: "│",
        LEFT_KEY: "┘",
        RIGHT_KEY: "└"
    },
    LEFT_KEY: {
        UP_KEY: "└",
        DOWN_KEY: "┌",
        LEFT_KEY: "─",
        RIGHT_KEY: "─"
    },
    RIGHT_KEY: {
        UP_KEY: "┘",
        DOWN_KEY: "┐",
        LEFT_KEY: "─",
        RIGHT_KEY: "─"
    }
}
"""Maps the last direction of travel and the new direction of travel to a
suitable character for the tail of the snek.
"""


def init():
    """Set up the curses library and screen."""
    curses.curs_set(0)  # invisible cursor
    STDSCR.border()

    max_y, max_x = STDSCR.getmaxyx()
    STDSCR.move(max_y // 2, max_x // 2)
    generate_food()
    STDSCR.refresh()


def generate_food():
    y, x = STDSCR.getyx()
    max_y, max_x = STDSCR.getmaxyx()

    found_space = False
    while not found_space:
        food_y = random.randrange(1, max_y)
        food_x = random.randrange(1, max_x)
        found_space = STDSCR.instr(food_y, food_x, 1) == EMPTY_CH

    STDSCR.addch(food_y, food_x, FOOD_CH)
    STDSCR.move(y, x)  # restore cursor position


# todo: fix TIME_STEP comments
def get_direction(last_direction):
    """Will block for up to TIME_STEP milliseconds and return a valid direction.
    If no direction is chosen, returns last_direction.
    """
    # set timeout
    if last_direction in {UP_KEY, DOWN_KEY}:
        STDSCR.timeout(TIME_STEP_UP_DOWN)
    elif last_direction in {LEFT_KEY, RIGHT_KEY}:
        STDSCR.timeout(TIME_STEP_LEFT_RIGHT)

    # wait for direction press
    direction = STDSCR.getch()
    if direction in {UP_KEY, DOWN_KEY, LEFT_KEY, RIGHT_KEY}:
        return direction
    else:
        return last_direction


def move(tail, last_direction, direction):
    """Execute a move in the given direction.
    Maintains the cursor on the head of the snek.
    """
    y, x = STDSCR.getyx()

    # draw tail over previous head
    STDSCR.addch(TAIL_CHS[last_direction][direction])
    tail.append((y, x))

    # calculate new co-ordinates
    if direction == UP_KEY:
        y -= 1
        STDSCR.timeout(TIME_STEP_UP_DOWN)
    elif direction == DOWN_KEY:
        y += 1
        STDSCR.timeout(TIME_STEP_UP_DOWN)
    elif direction == LEFT_KEY:
        x -= 1
        STDSCR.timeout(TIME_STEP_LEFT_RIGHT)
    elif direction == RIGHT_KEY:
        x += 1
        STDSCR.timeout(TIME_STEP_LEFT_RIGHT)

    ### move
    # max_y, max_x = STDSCR.getmaxyx()
    # end = len(tail) == (max_y - 2) * (max_x - 2)  # move this code
    ### move

    end = False
    # food detection
    collision = STDSCR.instr(y, x, 1)
    if collision == FOOD_CH:
        # don't remove last tail character
        # check for win condition (board is all tail)
        max_y, max_x = STDSCR.getmaxyx()
        if len(tail) + 1 == (max_y - 2) * (max_x - 2):
            end = True  # win
        else:
            generate_food()
    else:
        # remove last tail character
        remove_y, remove_x = tail.pop(0)
        STDSCR.addch(remove_y, remove_x, EMPTY_CH)

    # collision detection
    # collision may have changed if last tail character was there
    collision = STDSCR.instr(y, x, 1)
    if collision not in {EMPTY_CH, FOOD_CH}:
        end = True  # lose
        STDSCR.addch(y, x, DEAD_CH)
    else:
        STDSCR.addch(y, x, HEAD_CH)

    STDSCR.move(y, x)  # keep cursor at head
    STDSCR.refresh()
    return tail, end


def main(stdscr):
    global STDSCR
    STDSCR = stdscr

    init()
    direction = RIGHT_KEY
    tail = []
    end = False
    while not end:
        last_direction = direction
        direction = get_direction(last_direction)
        tail, end = move(tail, last_direction, direction)

    curses.beep()
    time.sleep(3)


if __name__ == "__main__":
    curses.wrapper(main)
