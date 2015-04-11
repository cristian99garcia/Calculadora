#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015, Cristian García <cristian99garcia@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import math
from gi.repository import Gdk

PI = 3.141592653589793238462643383279502884196406286208998628034825342117067982

EXPRESSIONS = [['**', '^'],
               ['/', '÷'],
               ['*', '×'],
               ['True', 'Correct'],
               ['False', 'Incorrect'],
               ['PI', str(PI)],
               ['π', str(PI)]]

SYMBOL_DEL = 'DEL'
SYMBOL_INFINITY = '∞'
OPERATOR_DIV = '÷'
OPERATOR_MUL = '×'
OPERATOR_ADD = '+'
OPERATOR_SUB = '-'
OPERATORS = [OPERATOR_DIV,
             OPERATOR_MUL,
             OPERATOR_ADD,
             OPERATOR_SUB]

SPECIAL_FUNCTIONS = ['sin', 'cos', 'tan', 'In', 'log', 'factorial']
SPECIAL_OPERATORS = {'!': 'factorial'}


def clean_string(text):
    text = text.lower()
    for expression in EXPRESSIONS:
        text = text.replace(expression[1], expression[0])

    for x in range(0, 10):
        text = text.replace('%d(' % x, '%d*(' % x)
        text = text.replace(')%d' % x, ')*%d' % x)

    return text


def square_root(number):
    return(math.sqrt(abs(number)))


def factorial(x):
    n1 = x
    n2 = 1
    result = 1
    while n2 < n1:
        result *= n2
        n2 += 1

    result *= x
    return result


def radians_to_degrees(x):
    return x * 180.0 / PI


def degrees_to_radians(x):
    return x / 180.0 * PI


def sin(x, in_radians=False):
    """
    # sen x = x - x ^ 3/3! + x ^ 5/5! - x ^ 7/7! ...
    if not in_radians:
        x = degrees_to_radians(x)

    string = 'x'
    sign = '-'
    n = 3
    while n < x:
        string += sign + 'x**(%d/factorial(%d))' % (n, n)
        sign = '+' if sign == '-' else '-'
        n += 2

    return eval(string)
    """
    return math.sin(x)


def cos(x):
    return math.cos(x)


def tan(x):
    return math.tan(x)


def In(x):
    return x


def log(x):
    return math.log(x)


def simplify(data, clean=True):
    if clean:
        data = clean_string(data)

    data = data.replace('+', 'SPLIT+')
    data = data.replace('-', 'SPLIT-')
    data = data.replace('(SPLIT', '(')
    _monomials = data.split('SPLIT')
    monomials = []
    final = ''

    for monomial in _monomials:
        if not monomial:
            continue

        has_operator = False

        for operator in list(SPECIAL_OPERATORS.keys()):
            if operator in monomial:
                has_operator = True

                _number = monomial.split(operator)[0]
                n = -1
                number = ''
                while True:
                    if not _number[n].isalnum() and _number.strip() not in ['', '(']:
                        break

                    number = _number[n] + number
                    n -= 1

                monomials.append(monomial.replace(number + operator, str(eval('%s(%s)' % (SPECIAL_OPERATORS[operator], number)))))

        if not has_operator:
            monomials.append(str(eval(monomial)))

    for x in monomials:
        if x[0] not in ['+', '-']:
            x = '+' + x

        x = str(eval(x))
        final += ('+' if not x[0] in ['+', '-'] else '') + x

    return str(eval(final))



def color_hex_to_cairo(color):
    if color[0] == '#':
        color = color[1:]

    (r, g, b) = (int(color[:2], 16),
                 int(color[2:4], 16),
                 int(color[4:], 16))

    return color_rgb_to_cairo((r, g, b))


def color_cairo_to_hex(color):
    r, g, b = color_cairo_to_rgb(color)
    r = hex(r)[2:]
    g = hex(g)[2:]
    b = hex(b)[2:]

    r = ('0' + r) if len(r) != 2 else r
    g = ('0' + g) if len(g) != 2 else g
    b = ('0' + b) if len(b) != 2 else b

    return '#' + r + g + b


def color_rgb_to_cairo(color):
    return (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)


def color_cairo_to_rgb(color):
    return (color[0] * 255, color[1] * 255, color[2] * 255)


def color_cairo_to_gdk(color):
    return Gdk.Color(color[0] * 65535, color[1] * 65535, color[2] * 65535)


def color_gdk_to_cairo(color):
    return (color.red / 65535.0, color.green / 65535.0, color.blue / 65535.0)
