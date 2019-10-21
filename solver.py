#!/usr/bin/python

from enum import Enum
from colorama import Fore
from colorama import Style

WIDTH = 9
HEIGHT = 9

class Type(Enum):
    VALUE = 1
    OPTIONS = 2
    SET_VALUE = 3

class Value:
    type: Type = Type.OPTIONS
    value: int = 0
    options: None

    def __init__(self):
        self.options = []

class Solver:
    map: None

    def __init__(self):
        self.map = []

###
# Init functions
###

    def read(self, filename):
        self.map = [Value() for _ in range(WIDTH * HEIGHT)]
        file = open(filename, 'r')
        lines = file.read().splitlines()

        row_num = line_num = 0
        for line in lines:
            row_num = 0
            for symb in line:
                if symb != '.':
                    self.map[line_num * WIDTH + row_num].type = Type.VALUE
                    self.map[line_num * WIDTH + row_num].value = int(symb)
                row_num += 1
            line_num += 1

###
# Print functions
###

    def __print_element(self, value, num):
        if value.type == Type.OPTIONS:
            if len(value.options) == 0:
                if num == 0 or num == 2:
                    print('   ', end=' ')
                else:
                    print(' . ', end=' ')
            else:
                for option in range(1 + num * 3, 4 + num * 3):
                    if option in value.options:
                        print(f"{Fore.WHITE}%d{Style.RESET_ALL}" % option, end = '')
                    else:
                        print(".", end = '')
                print(" ", end = '')
        else:
            if num == 0 or num == 2:
                print("   ", end = ' ')
            else:
                print(" ", end = '')
                if value.type == Type.VALUE:
                    print(f"{Fore.GREEN}%d{Style.RESET_ALL}" % value.value, end = '')
                else:
                    print(f"{Fore.RED}%d{Style.RESET_ALL}" % value.value, end = '')
                print(" ", end = ' ')

    def __print_line(self, values):
        num = 0
        for i in range(3):
            for value in values:
                if num % 3 == 0:
                    print("|", end=" ")
                num += 1
                self.__print_element(value, i)
            print("|")

    def print_data(self):
        for line_num in range(HEIGHT):
            if line_num % 3 == 0:
                print('-------------------------------------------')
            self.__print_line(self.__get_line(line_num))
            print('|             |             |             |')
        print('-------------------------------------------')

###
# Utils functions
###

    def __get_line(self, line_num):
        ret = []
        for row_num in range(WIDTH):
            tmp = self.map[line_num * WIDTH + row_num]
            ret.append(tmp)
        return ret

    def __get_row(self, row_num):
        ret = []
        for line_num in range(HEIGHT):
            tmp = self.map[line_num * WIDTH + row_num]
            ret.append(tmp)
        return ret

    def __get_block(self, block_num):
        ret = []
        row_offset = (block_num % 3) * 3
        line_offset = (block_num // 3) * 3
        for line_num in range(3):
            for row_num in range(3):
                line = line_num + line_offset
                row = row_num + row_offset
                tmp = self.map[line * WIDTH + row]
                ret.append(tmp)
        return ret

    def __get_options_from_array(self, values_raw):
        ret = [i for i in range(1, 10)]
        for value in values_raw:
            if value.type != Type.OPTIONS:
                ret.remove(value.value)
        return ret


###
# Fill options functions
###

    def __flush_options(self):
        for element in self.map:
            if element.type == Type.OPTIONS:
                element.options = []

    def __fill_options_for_element(self, line_num, row_num):
        if self.map[line_num * WIDTH + row_num].type != Type.OPTIONS:
            return

        block_num = ((line_num // 3) * 3) + (row_num // 3)

        line  = self.__get_options_from_array(self.__get_line(line_num))
        row   = self.__get_options_from_array(self.__get_row(row_num))
        block = self.__get_options_from_array(self.__get_block(block_num))

        res = list(set(line).intersection(row).intersection(block))
        res.sort()
        self.map[line_num * WIDTH + row_num].options = res

    def __simple_fill_options(self):
        for line_num in range(HEIGHT):
            for row_num in range(WIDTH):
                if self.map[line_num * WIDTH + row_num].type == Type.OPTIONS:
                    self.__fill_options_for_element(line_num, row_num)

    def __find_pairs(self, values):
        ret = 0
        list_numbers = []
        list_pairs = []
        for number in range(1,10):
            tmp_list = []
            for value in values:
                if value.type == Type.OPTIONS:
                    if number in value.options:
                        tmp_list.append(value)
            if len(tmp_list) == 2:
                # Go though all elements and search option that exist only in two cells
                list_numbers.append(number)
                list_pairs.append(tmp_list)

        # If we find 2 or more element
        # possibly we have pair
        if len(list_pairs) >= 2:
            for i in range(0, len(list_pairs) - 1):
                for j in range(i + 1, len(list_pairs)):
                    if list_pairs[i][0] == list_pairs[j][0] and list_pairs[i][1] == list_pairs[j][1] :
                        # If two cell have two same element - it's pair
                        if len(list_pairs[i][0].options) != 2:
                            # If cell how more than two option, remove others
                            ret = 1
                            list_pairs[i][0].options = [list_numbers[i], list_numbers[j]]
                        if len(list_pairs[i][1].options) != 2:
                            # If cell how more than two option, remove others
                            ret = 1
                            list_pairs[i][1].options = [list_numbers[i], list_numbers[j]]
        return ret

    def fill_options(self):
        self.__flush_options()
        self.__simple_fill_options()

        # Search pairs
        while 1:
            ret = 0
            for i in range(HEIGHT):
                if self.__find_pairs(self.__get_line(i)) == 1:
                    ret = 1
            for i in range(HEIGHT):
                if self.__find_pairs(self.__get_row(i)) == 1:
                    ret = 1
            for i in range(HEIGHT):
                if self.__find_pairs(self.__get_block(i)) == 1:
                    ret = 1
            if ret == 0:
                break


###
# Solver functions
###

    def __set_one_options(self):
        # Run though all element and if exist
        # only ony option in cell - set it
        ret = 0
        for element in self.map:
            if element.type == Type.OPTIONS and len(element.options) == 1:
                ret = 1
                element.type = Type.SET_VALUE
                element.value = element.options[0]
        return ret

    def __set_only_one_option_in_array(self, values):
        ret = 0
        for i in range(1, 10):
            count = 0
            element = None
            for value in values:
                if value.type == Type.OPTIONS and i in value.options:
                    count += 1
                    element = value
            if count == 1:
                ret = 1
                element.type = Type.SET_VALUE
                element.value = i
        return ret


    def solve_step(self):
        if self.__set_one_options() == 1:
            return 1
        for i in range(HEIGHT):
            if self.__set_only_one_option_in_array(self.__get_line(i)) == 1:
                return 1
        for i in range(WIDTH):
            if self.__set_only_one_option_in_array(self.__get_row(i)) == 1:
                return 1
        for i in range(9):
            if self.__set_only_one_option_in_array(self.__get_block(i)) == 1:
                return 1
        return 0

solver = Solver()

solver.read('hard')
solver.print_data()

while 1:
    solver.fill_options()

    if solver.solve_step() == 1:
        continue

    break

solver.print_data()
