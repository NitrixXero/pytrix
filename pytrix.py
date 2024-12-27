# Copyright 2023 Elijah Gordon (NitrixXero) <nitrixxero@gmail.com>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import random
import time
import argparse
from colorama import init, Fore, Style
import shutil
import string

init(autoreset=True)

COLORS = {
    "green": Fore.GREEN,
    "red": Fore.RED,
    "blue": Fore.BLUE,
    "yellow": Fore.YELLOW,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "white": Fore.WHITE,
    "black": Fore.BLACK,
}

class MatrixColumn:
    def __init__(self, x, screen_height, bold, char_set, rainbow_mode, default_color):
        self.x = x
        self.screen_height = screen_height
        self.head = 0
        self.tail_start = -1
        self.tail_length = random.randint(screen_height // 4, screen_height // 2)
        self.done = False
        self.bold = bold
        self.char_set = char_set
        self.rainbow_mode = rainbow_mode
        self.default_color = default_color

    def step(self):
        if self.done:
            return False

        self.head += 1
        if self.head >= self.screen_height:
            self.done = True

        return True

    def get_character_at(self, y):
        color = random.choice(list(COLORS.values())) if self.rainbow_mode else self.default_color
        style = Style.BRIGHT if self.bold else Style.NORMAL

        if y == self.head:
            return random.choice(self.char_set), Fore.WHITE + style
        elif self.tail_start <= y < self.head:
            return random.choice(self.char_set), color + style
        elif y == self.tail_start - 1:
            return ' ', Fore.BLACK
        return None, None

    def update_tail(self):
        if self.tail_start < self.head:
            self.tail_start += 1
        return self.tail_start < self.screen_height


class MatrixAnimation:
    def __init__(self, max_columns, frame_delay, char_set, bold, rainbow_mode, color):
        self.max_columns = max_columns
        self.frame_delay = frame_delay
        self.bold = bold
        self.char_set = char_set
        self.rainbow_mode = rainbow_mode
        self.color = COLORS.get(color, Fore.GREEN)
        self.columns = []
        self.screen_width, self.screen_height = self.get_terminal_size()

    def get_terminal_size(self):
        return shutil.get_terminal_size()

    def add_column(self):
        if len(self.columns) < self.max_columns:
            x = random.randint(0, self.screen_width - 1)
            if all(column.x != x for column in self.columns):
                self.columns.append(MatrixColumn(x, self.screen_height, self.bold, self.char_set, self.rainbow_mode, self.color))

    def update_columns(self):
        for column in self.columns[:]:
            if not column.step() and not column.update_tail():
                self.columns.remove(column)

    def draw_frame(self):
        frame = [[' ' for _ in range(self.screen_width)] for _ in range(self.screen_height)]
        colors = [['' for _ in range(self.screen_width)] for _ in range(self.screen_height)]

        for column in self.columns:
            for y in range(self.screen_height):
                char, color = column.get_character_at(y)
                if char:
                    frame[y][column.x] = char
                    colors[y][column.x] = color

        print('\033c', end='')
        for y in range(self.screen_height):
            line = ''.join(colors[y][x] + frame[y][x] for x in range(self.screen_width))
            print(line)

    def run(self):
        try:
            while True:
                current_width, current_height = self.get_terminal_size()

                if current_width != self.screen_width or current_height != self.screen_height:
                    self.screen_width, self.screen_height = current_width, current_height
                    self.columns = []

                self.add_column()
                self.update_columns()
                self.draw_frame()
                time.sleep(self.frame_delay)
        except KeyboardInterrupt:
            print('\033c', end='')


def parse_arguments():
    parser = argparse.ArgumentParser(description="Matrix-style animation in Python.")
    parser.add_argument("-b", action="store_true", help="Enable bold characters")
    parser.add_argument("-V", action="store_true", help="Print version and exit")
    parser.add_argument("-u", type=int, choices=range(0, 11), default=4, help="Screen update delay (0-10, default 4)")
    parser.add_argument("-C", type=str, choices=list(COLORS.keys()), default="green", help="Matrix color (default green)")
    parser.add_argument("-r", action="store_true", help="Rainbow mode")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    if args.V:
        print("Matrix terminal animation Version 1.0")
        exit()

    char_set = list(string.printable[:-6])

    animation = MatrixAnimation(
        max_columns=20,
        frame_delay=args.u / 40,
        char_set=char_set,
        bold=args.b,
        rainbow_mode=args.r,
        color=args.C,
    )

    animation.run()
