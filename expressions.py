#!/usr/bin/env python2.7
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

import globals as G


class Monomial(object):
    """
    A simple monomial

    >>> m = Monomial('4x')
    >>> m
    4x

    >>> type(m), bool(m)
    (Monomial, True)

    >>> m == Monomial('4x')
    True

    >>> m = Monomial('x')
    >>> m == Monomial('+x')
    True

    >>> m == Monomial('-x')
    False

    >>> m = Monomial('')
    >>> m
    0

    >>> m == 0
    True

    >>> m == '0'
    True

    >>> bool(m)
    False
    """
    def __init__(self, data):

        self.parse_string(data)

    def parse_string(self, data):
        """
        Get all data from the string.

        For example, if the data is '2x^4':
            coefficient = 2
            degree = 4
            literal_part = x^4
            sign = '+'
        """
        data = data.replace('**', '^')
        data = data.replace(' ', '')
        _repr = None

        if 'x^' in data:
            coefficient = data.split('x')[0].split('+')[-1]
            if not coefficient:
                self.coefficient = 1

            else:
                sign = coefficient[0] if coefficient[0] in ['+', '-'] else '+'
                coefficient = coefficient[1:] if coefficient[0] in ['+', '-'] else coefficient
                try:
                    self.coefficient = int(sign + coefficient)
                except:
                    self.coefficient = 0
                    _repr = data

            try:
                self.degree = int(data.split('^')[1].split('+')[0])
            except:
                self.degree = 0

            self.literal_part = 'x^' + str(self.degree)

        elif 'x' in data and not '^' in data:
            coefficient = data.split('x')[0]
            if coefficient and coefficient[0] in ['+', '-']:
                sign = coefficient[0]
                coefficient = coefficient[1:]

            else:
                sign = '+'

            if coefficient and coefficient.isalnum():
                self.coefficient = float(sign + coefficient)

            else:
                self.coefficient = float(sign + '1')

            self.degree = 1
            self.literal_part = 'x'

        elif not 'x' in data:
            if '^' in data:
                data = data.replace('^', '**')

            try:
                self.coefficient = float(eval(data))
            except:
                self.coefficient = 0

            self.degree = 0
            self.literal_part = ''

        if self.coefficient < 0:
            self.coefficient = abs(self.coefficient)
            self.sign = '-'

        elif self.coefficient >= 0:
            self.sign = '+'

        if not _repr:
            self.repr = '%s%d%s' % (self.sign, self.coefficient, self.literal_part)
            if self.repr.startswith('+0x'):
                self.repr = '0'
                self.coefficient = 0
                self.literal_part = ''
                self.sign = '+'

        else:
            self.repr = _repr

        if int(self.coefficient) == self.coefficient:
            self.coefficient = int(self.coefficient)

    def __str__(self):
        return self.repr[1:] if self.repr.startswith('+') else self.repr

    def __eq__(self, monomial):
        if type(monomial) in [str, int]:
            monomial = Monomial(str(monomial))

        if type(monomial) != Monomial:
            return False

        return self.repr == monomial.repr

    def __ne__(self, monomial):
        return not self == monomial

    def __pos__(self):
        return Monomial(self.repr.replace('-', '+'))

    def __neg__(self):
        return Monomial(self.repr.replace('+', '-'))

    def __add__(self, monomial):
        if type(monomial) in [str, int]:
            monomial = Monomial(str(monomial))

        if type(monomial) != Monomial:
            raise TypeError("cannot concatenate 'Monomial' + %s objects" % str(type(monomial))[6:-1])

        if self.degree == monomial.degree:
            coefficient1 = self.coefficient
            coefficient2 = monomial.coefficient
            if self.sign == '-':
                coefficient1 *= -1

            if monomial.sign == '-':
                coefficient2 *= -1

            if self.degree == 0:
                return Monomial(str(coefficient1 + coefficient2))

            elif self.degree == 1:
                return Monomial(str(coefficient1 + coefficient2) + 'x')

            else:
                return Monomial(str(coefficient1 + coefficient2) + 'x^' + str(self.degree))

        else:
            if self.degree > monomial.degree:
                sign = '-' if self.sign == '-' else ''
                data = sign + str(self.coefficient) + self.literal_part + monomial.sign + str(monomial.coefficient) + monomial.literal_part
                return Polynomial(data)

            elif self.degree < monomial.degree:
                if self:
                    sign = self.sign if self.repr[0] not in ['+', '-'] else ''
                    data = monomial.repr + sign + self.repr
                    return Polynomial(data)

                else:
                    return Monomial(monomial.repr)

                #return Polynomial(data)

    def __sub__(self, monomial):
        if type(monomial) == Monomial:
            monomial = monomial.repr

        elif type(monomial) == int:
            monomial = str(monomial)

        elif type(monomial) != str:
            raise TypeError("unsupported operand type(s) for -: 'Monomial' and %s" % str(type(monomial))[6:-1])

        if monomial.startswith('+'):
            monomial = monomial[1:]

        _repr = self.repr + '-%s' % monomial
        if Monomial(monomial).degree == self.degree:
            polynomial = Polynomial(_repr)
            return Monomial(polynomial.repr)

        else:
            return Polynomial(_repr)

    def __mul__(self, monomial):
        if type(monomial) in [str, int]:
            monomial = Monomial(str(monomial))

        coefficient = monomial.coefficient * self.coefficient
        degree = monomial.degree + self.degree
        if degree == 0:
            return Monomial(str(coefficient))

        elif degree == 1:
            return Monomial(str(coefficient) + 'x')

        else:
            return Monomial(str(coefficient) + 'x^' + str(degree))

    def __div__(self, monomial):
        if type(monomial) in [str, int]:
            monomial = Monomial(str(monomial))

        degree = self.degree - monomial.degree
        if monomial.coefficient == self.coefficient:
            if degree == 1:
                return Monomial('x')

            else:
                return Monomial('x^%d' % degree)

        elif self.coefficient == 1 and monomial.coefficient != 1:
            if degree == 1:
                _monomial = '(x)'

            else:
                _monomial = '(x^%d)' % degree

            _monomial += '/%d' % monomial.coefficient
            return Monomial(_monomial)

        else:
            coefficient = self.coefficient / monomial.coefficient
            if degree == 1:
                _coefficient = str(coefficient) if coefficient != 1 else ''
                return Monomial('%sx' % _coefficient)

            elif degree == 0:
                return Monomial(coefficient)

            else:
                return Monomial('%dx^%d' % (coefficient, degree))

    def __pow__(self, other):
        if type(other) != int:
            raise TypeError("unsupported operand type(s) for ** or pow(): 'Monomial' and %s" % str(type(other))[6:-1])

        if self.degree == 0:
            return Monomial(str(int(self.repr) ** other))

        elif self.degree == 1:
            return Monomial(self.repr + '^' + str(other))

        else:
            degree = self.degree ** other
            _repr = self.repr.split('^')[0] + '^' + str(degree)
            return Monomial(_repr)

    def __and__(self, monomial):
        if type(monomial) == str:
            monomial = Monomial(monomial)

        return self.repr.strip() != '0' and monomial.repr.strip() != '0'

    def __or__(self, monomial):
        if type(monomial) == str:
            monomial = Monomial(monomial)

        return self.repr.strip() != '0' or monomial.repr.strip() != '0'

    def __nonzero__(self):
        return self.repr not in ['-0', '0', '+0']

    def __repr__(self):
        _repr = self.repr
        if _repr.startswith('+'):
            _repr = _repr[1:]

        if _repr.startswith('1x'):
            _repr = _repr[1:]

        if _repr.startswith('-1x'):
            _repr = '-x' + _repr[3:]

        return _repr


class Polynomial(object):
    """
    A polynomial, contains several monomials.

    >>> # Opperating with polunomials
    >>> p = Polynomial('3x^2 + 4x + 10 - 5')
    >>> p, bool(p)
    (3x^2 + 4x + 5, True)

    >>> p + 20
    3x^2 + 4x + 25

    >>> p += '20'
    >>> p
    3x^2 + 4x + 25

    >>> p + '4x'
    3x^2 + 8x + 5

    >>> p + '-2x^2'
    1x^2 + 4x + 25

    >>> # Compare polynomials
    >>> p1 = Polynomial('3x^2 + 4x + 5')  # Create using a string
    >>> p2 = Polynomial({0: ['5'], 1: ['4x'], 2: ['3x^2']})  # Create using a dictionary
    >>> p3 = Polynomial(4)  # Create using a integer
    >>> p1 == p2
    True

    >>> p1 -= 5
    >>> p1 == p2
    False

    >>> p1 == p2 == p3
    False

    >>> p = Polynomial('0')
    >>> p, bool(p)
    (0, False)
    """
    def __init__(self, data):

        if type(data) == int:
            data = str(data)

        if type(data) == str:
            self.parse_string(data)

        elif type(data) == dict:
            self.monomials = data
            self.parse_dict()

    def parse_string(self, data):
        """
        Transform a string to a understandable dictionary
        Example:
            '3x^2 + 4x + 5' = {0: ['5'], 1: ['4x'], 2: ['3x^2']}
            '2x' = {1: ['2x']}
            '10x^14 + 5x^6 - 3x^2' = {2: ['-3x^2'], 6: ['5x^6'], 14: ['10x^14']}
        """
        self.max_degree = 0
        if not data or not data.replace('0', '') or (data[0] in ['+', '-'] and not data[1:].replace('0', '')):
            self.monomials = {}
            self.degrees = []
            self.repr = '0'
            return

        order = [' ', '^+', '^-', '+', '-', 'DEGREE_POS', 'DEGREE_SUB']
        replaces = {' ': '',
                    '^+': 'DEGREE_POS',
                    '^-': 'DEGREE_SUB',
                    '+': 'SPLIT+',
                    '-': 'SPLIT-',
                    'DEGREE_POS': '^+',
                    'DEGREE_SUB': '^-'}

        for find in order:
            data = data.replace(find, replaces[find])

        _monomials = data.split('SPLIT')
        monomials = []
        for monomial in _monomials:
            if monomial in ['0', '+0', '-0']:
                continue

            monomials.append(monomial)

        self.monomials = {}

        for monomial in monomials:
            if monomial in ['+0', '-0', '0']:
                continue

            monomial = Monomial(monomial)
            if not monomial.degree in self.monomials:
                self.monomials[monomial.degree] = []

            self.monomials[monomial.degree].append(monomial)

        # Good orderer of monomials by her degree
        degrees = []
        for degree in self.monomials.keys():
            degrees.append(degree)

        _dict = {}
        _list = []

        for value in degrees:
            if not abs(value) in _dict:
                _dict[abs(value)] = []

            _dict[abs(value)].append(value)

        _degrees = _dict.keys()
        degrees = []
        for degree in _degrees:
            degrees.append(degree)

        degrees.sort()
        degrees.reverse()
        for degree in degrees:
            list = _dict[degree]
            list.sort()
            list.reverse()

            for value in list:
                _list.append(value)

        degrees = _list

        # Making the representation by the orderer monomials
        self.repr = ''
        for degree in degrees:
            _monomial = None
            for monomial in self.monomials[degree]:
                if not _monomial:
                    _monomial = monomial

                else:
                    _monomial += monomial

            _repr = _monomial.repr
            if not _repr.startswith('+') and not _repr.startswith('-'):
                _repr = '+' + _repr

            order = ['^+', '^-', '+', '-', ' + 0', 'DEGREE_POS', 'DEGREE_SUB']
            replaces = {'^+': 'DEGREE_POS',
                        '^-': 'DEGREE_SUB',
                        '+': ' + ',
                        '-': ' - ',
                        ' + 0': '',
                        'DEGREE_POS': '^+',
                        'DEGREE_SUB': '^-'}

            for find in order:
                _repr = _repr.replace(find, replaces[find])

            self.repr += _repr
            if abs(degree) > self.max_degree:
                self.max_degree = abs(degree)

        if self.repr.startswith(' + '):
            self.repr = self.repr[3:]  # 3 = len(' + ')

        if self.repr.startswith(' - '):
            self.repr = '-' + self.repr[3:]

        if not self.repr:
            self.repr = '0'

    def parse_dict(self):
        """
        Transform a dictionary to string(invert process of parse_string).
        """
        self.repr = ''
        for monomial in self:
            self.repr += monomial.sign + monomial.repr

        self.repr = self.repr.replace('+', ' + ')
        self.repr = self.repr.replace('-', ' - ')
        self.repr = self.repr.replace(' + 0', '')

        if self.repr.startswith(' + '):
            self.repr = self.repr[3:]  # 3 = len(' + ')

        if self.repr.startswith(' - '):
            self.repr = '-' + self.repr[3:]

        self.parse_string(self.repr)  # For when use string and not use Monomial

    def get_max_degree(self):
        return self.max_degree

    def __repr__(self):
        return self.repr

    def __str__(self):
        return self.repr

    def __add__(self, polynomial):
        if not self.repr.startswith('+') and not self.repr.startswith('-'):
            self.repr = '+' + self.repr

        if type(polynomial) == int:
            polynomial = str(polynomial)

        if type(polynomial) == str:
            if polynomial and not polynomial[0] in ['+', '-']:
                polynomial = '+ ' + polynomial

            return self + Polynomial(polynomial)

        elif type(polynomial) in [Polynomial, Monomial]:
            if polynomial.repr and not polynomial.repr[0] in ['+', '-']:
                polynomial.repr = '+ ' + polynomial.repr

            return Polynomial(self.repr + polynomial.repr)

    def __sub__(self, polynomial):
        if type(polynomial) in [Monomial, Polynomial]:
            polynomial = polynomial.repr

        elif type(polynomial) == int:
            polynomial = str(polynomial)

        elif type(polynomial) != str:
            raise TypeError("unsupported operand type(s) for -: 'Polynomial' and %s" % str(type(polynomial))[6:-1])

        if polynomial and polynomial[0] not in ['+', '-']:
            polynomial = '+' + polynomial

        polynomial = polynomial.replace('-', 'ADD')
        polynomial = polynomial.replace('+', 'SUB')
        polynomial = polynomial.replace('ADD', '+')
        polynomial = polynomial.replace('SUB', '-')

        return Polynomial(self.repr + polynomial)

    def __neg__(self):
        polynomial = self.repr
        polynomial = polynomial.replace(' ', '')
        polynomial = polynomial.replace('-', 'ADD')
        polynomial = polynomial.replace('+', 'SUB')
        polynomial = polynomial.replace('ADD', '+')
        polynomial = polynomial.replace('SUB', '-')
        if polynomial and polynomial[0] not in ['-', '+']:
            polynomial = '-' + polynomial

        p = Polynomial(polynomial)
        return Polynomial

    def __eq__(self, polynomial):
        if type(polynomial) != Polynomial:
            return False

        return self.repr == polynomial.repr

    def __nonzero__(self):
        return bool(self.monomials)

    def __iter__(self):
        degrees = []
        for degree in self.monomials.keys():
            degrees.append(degree)

        degrees.sort()
        degrees.reverse()
        for degree in degrees:
            for monomial in self.monomials[degree]:
                if type(monomial) == str:
                    monomial = Monomial(monomial)

                if monomial.repr.strip() in ['0', '+0', '-0']:
                    continue

                yield monomial


class Equation(object):
    """
    **************************
    ****** LACK FINISH *******
    **************************

    A Equations resolver, is necesary a Equation.
    You can pass as an argument polynomial (which is supposed to be a
    ranked Equation 0)
    Example:
        >>> p = Polynomial('3x^2-3x+10')
        >>> e = Equation(p)

    You can also take a string as an argument, unmatched or matched to any
    number (if not be matched, will be taken as equated to 0)
    Example:
        >>> p = '3x^2-3x+10'
        >>> e = Equation(p)

        >>> p = '3x^2+10=3x'  # This is equivalent to '3x^2 - 3x + 10 = 0'
        >>> e = Equation(p)

    Solve Equations:
        1° degree:
            # General expresion: ax = b
            >>> e = Equation('5x + 8 = 100')
            >>> e.solve()
            {92/5} = {18.4}

            >>> e = Ecuation('2x + 10')
            >>> e.solve()
            {10/2} = {5}

        2° degree:
            1° Case:
                >>> e = Equation('x^2 -9x + 8 = 0')
                >>> e.solve()
                {(8, 1)}

            2° Case:
            3° Case:
            4° Case:

    """
    def __init__(self, data):

        self.polynomial = None
        self.repr_solution = ''
        self.parse_data(data)

    def parse_data(self, data):
        # Get a string for both polynomials
        if type(data) == str:
            if '=' in data:
                data = data.split('=')

            else:
                data = (data, '0')

        elif type(data) in [Polynomial, Monomial]:
            data = (data.repr, '0')

        if type(data) in [tuple, list] and len(data) == 2:
            polynomial1, polynomial2 = data

            if type(polynomial1) in [Polynomial, Monomial]:
                polynomial1 = polynomial1.repr.replace(' ', '')

            elif type(polynomial1) == int:
                polynomial = str(polynomial1)

            elif type(polynomial1) != str:
                # 'error', polynomial1
                pass

            if type(polynomial2) in [Polynomial, Monomial]:
                polynomial2 = polynomial2.repr.replace(' ', '')

            elif type(polynomial2) == int:
                polynomial = str(polynomial2)

            elif type(polynomial2) != str:
                # 'error', polynomial2
                pass

        # Convert two polynomials in one
        if polynomial2.strip() != '0':
            polynomial2 = polynomial2.replace('-', 'ADD')
            polynomial2 = polynomial2.replace('+', 'SUB')
            polynomial2 = polynomial2.replace('ADD', '+')
            polynomial2 = polynomial2.replace('SUB', '-')

            if polynomial2 and polynomial2[0] not in ['+', '-']:
                polynomial2 = '-' + polynomial2

            polynomial1 += polynomial2

        # Make a Polynomial instance for futures operations
        self.polynomial = Polynomial(polynomial1)
        self.repr = self.polynomial.repr + ' = 0'
        self.degree = self.polynomial.get_max_degree()

    def solve(self):
        """
        Gets the degree of the equation and select the appropriate resolution
        """
        if self.degree == 1:
            return self.__solve_with_1_degree_methods()

        elif self.degree == 2:
            return self.__solve_with_2_degree_methods()

        return None

    def __solve_with_1_degree_methods(self):
        """
        Basic method of solving linear equations with one unknown:
            e = 3x - 10 = 2

            By the clearance method:
            3x = 2 + 10  --> 3x = 12
            x = 12 / 3
            x = 4
            S = {4}
        """
        polynomial = self.polynomial.repr.replace(' ', '')
        polynomial = polynomial.replace('+', 'SPLIT+')
        polynomial = polynomial.replace('-', 'SPLIT-')
        monomials = []
        _monomials = polynomial.split('SPLIT')
        for monomial in _monomials:
            if monomial:
                monomials.append(monomial)

        monomial1, monomial2 = monomials
        monomial1 = Monomial(monomial1)
        monomial2 = Monomial(monomial2)
        solution = '{'

        coefficient1 = str(float(monomial1.coefficient))
        coefficient2 = str(float(monomial2.coefficient))
        sign1 = monomial1.sign
        sign2 = '+' if monomial2.sign == '-' else '-'

        if sign1 != sign2:  # For signs rule
            if sign1 == '-':
                coefficient1 = '-' + coefficient1

            if sign2 == '-':
                coefficient2 = '-' + coefficient2

        if coefficient1.endswith('.0'):
            coefficient1 = coefficient1[:-2]

        if coefficient2.endswith('.0'):
            coefficient2 = coefficient2[:-2]

        r = str(float(coefficient2) / float(coefficient1)).split('.')
        r = r[0] + '.' + r[1]
        if len(r.split('.')[1]) > 2:
            other_solution = ''

        else:
            if r.endswith('.0'):
                r = r[:-2]

            other_solution = ' = {%s}' % (r)

        solution += coefficient2 + '/' + coefficient1 + '}' + other_solution
        self.repr_solution = solution
        return float(self.repr_solution.split(' = ')[1].replace('{', '').replace('}', ''))

    def __solve_with_2_degree_methods(self):
        """
        Quadratic equation
        """
        monomials = self.polynomial.monomials
        if 0 in monomials and 1 in monomials and 2 in monomials:
            # Is a complete second degree equation, apply bhaskaras and get
            # two values
            # Example of a cuadratic complete equation:
            #   x^2 -9x + 8 = 0

            a = float('%s%d' % (monomials[2][0].sign, monomials[2][0].coefficient))
            b = float('%s%d' % (monomials[1][0].sign, monomials[1][0].coefficient))
            c = float('%s%d' % (monomials[0][0].sign, monomials[0][0].coefficient))
            delta = (b ** 2) - (4 * a * c)

            if delta < 0:
                # Is impossible to calculate the square root of a
                # negative number, empty solution.
                self.repr_solution = 'Ø'

            # Calculating square root without 'math' module
            root = G.square_root(delta)
            x1 = (-b + root) / (2 * a)  # Positive root
            x2 = (-b - root) / (2 * a)  # Negative root
            self.repr_solution = '{(%f; %f)}' % (float(x1), float(x2))
            return [float(x1), float(x2)]

        # Incomplete equations
        elif 0 not in monomials and 1 not in monomials and 2 in monomials:
            # 2x^2 = 0
            self.repr_solution = '{(0, 0)}'
            return [0, 0]

        elif 0 not in monomials and 1 in monomials and 2 in monomials:
            # x^2 - 5x = 0
            # x(x - 5) = 0
            # Case 1:
            #   x = 0
            # Case 2:
            #   x - 5 = 0
            #   x = 5
            monomial = monomials[1][0]
            x1 = 0
            x2 = -int('%s%d' % (monomial.sign, monomial.coefficient))
            self.solution_repr = '%d; %d' % (x1, x2)
            return [x1, x2]

        elif 0 in monomials and 1 not in monomials and 2 in monomials:
            # x^2 - 25 = 0
            # x^2 = 25
            # x = +- SquareRoot(25)
            # x1 = 5
            # x2 = -5
            monomial1 = monomials[2][0]
            monomial2 = monomials[0][0]
            if monomial1.sign == monomial2.sign:
                self.repr_solution = 'Ø'
                return None

            root = G.square_root(monomial2.coefficient)
            self.repr = '{(%f, %f)}' % (float(root), float(-root))
            return [root, -root]

        return None

    def __repr__(self):
        return self.repr


class Function(object):
    def __init__(self, polynomial):

        if type(polynomial) == Monomial:
            polynomial = polynomial.repr

        if type(polynomial) == str:
            if polynomial.startswith('f(x) = '):
                polynomial = polynomial[7:]

            _repr = polynomial
            self.polynomial = Polynomial(polynomial)

        elif type(polynomial) == Polynomial:
            _repr = polynomial.repr
            self.polynomial = polynomial

        self.repr = 'f(x) = %s' % _repr
        self.degree = self.polynomial.get_max_degree()
        self.independent_term = 0

        if 0 in self.polynomial.monomials:
            monomial = self.polynomial.monomials[0][0]
            self.independent_term = monomial.coefficient
            if monomial.sign == '-':
                self.independent_term *= -1

    def to_graph(self):
        if self.degree == 1:
            pass

    def __repr__(self):
        return self.repr

    def __call__(self, value=0):
        _repr = self.polynomial.repr.replace('^', '**')
        for x in range(0, 10):
            _repr = _repr.replace('%dx' % x, '%d*x' % x)

        _repr = _repr.replace('x', str(value))
        return str(eval(_repr))


class Expression(object):
    """
    **************************
    ****** LACK FINISH *******
    **************************

    A class that handles deduce what a mathematical expression that is passed
    as an argument is.
    """

    def __init__(self, data):
        # FIXME: Add mathematical functions detector

        if type(data) in [Monomial, Polynomial, Equation, Function]:
            data = data.repr

        elif type(data) in [int, float]:
            data = str(data)

        if type(data) != str:
            raise TypeError('Type unknown')

        if '=' in data:
            if data.startswith('f(x)'):
                self.obj = Function(data)
                self.repr = self.obj.repr

            else:
                self.obj = Equation(data)
                self.repr = self.obj.repr + '   S={%s}' % str(self.obj.solve())

        else:
            self.obj = Polynomial(data)
            self.repr = self.obj.repr

    def is_monomial(self):
        return type(self.obj) == Monomial

    def is_polynomial(self):
        return type(self.obj) == Polynomial

    def is_equation(self):
        return type(self.obj) == Equation

    def is_function(self):
        return type(self.obj) == Function

    def __str__(self):
        return self.repr

    def __repr__(self):
        return self.repr
