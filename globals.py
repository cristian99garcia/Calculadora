#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

PI = 3.141592653589793238462643383279502884196406286208998628034825342117067982

EXPRESSIONS = [['**', '^'],
               ['/', '÷'],
               ['*', '×'],
               ['True', 'Correct'],
               ['False', 'Incorrect'],
               ['PI', str(PI)],
               ['π', str(PI)]]

SYMBOL_DEL = 'DEL'
OPERATOR_DIV = '÷'
OPERATOR_MUL = '×'
OPERATOR_ADD = '+'
OPERATOR_SUB = '-'
OPERATORS = [OPERATOR_DIV,
              OPERATOR_MUL,
              OPERATOR_ADD,
              OPERATOR_SUB]


def clean_string(text):
    text = text.lower()
    for expression in EXPRESSIONS:
        text = text.replace(expression[1], expression[0])

    return text


def square_root(number):
    number = float(number)
    root = number
    i = 0
    while i != root:
        i = root
        root = (number / root + root) / 2

    return root


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


def sen(x, in_radians=False):
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
    return math.sen(x)


def cos(x):
    return math.cos(x)


def tan(x):
    return math.tan(x)


def In(x):
    return x


def log(x):
    return math.log(x)
