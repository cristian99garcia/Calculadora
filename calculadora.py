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

        if 'x^' in data:
            coefficient = data.split('x')[0].split('+')[-1]
            sign = '+'
            if coefficient and coefficient[0] in ['+', '-']:
                sign = coefficient[0]
                coefficient = coefficient[1:]

            if coefficient and coefficient.isalnum():
                self.coefficient = int(sign + coefficient)

            else:
                self.coefficient = int(sign + '1')

            self.degree = int(data.split('^')[1].split('+')[0])
            self.literal_part = 'x^' + str(self.degree)

        elif 'x' in data and not '^' in data:
            coefficient = data.split('x')[0]
            if coefficient and coefficient[0] in ['+', '-']:
                sign = coefficient[0]
                coefficient = coefficient[1:]

            else:
                sign = '+'

            if coefficient and coefficient.isalnum():
                self.coefficient = int(sign + coefficient)

            else:
                self.coefficient = int(sign + '1')

            self.degree = 1
            self.literal_part = 'x'

        elif not 'x' in data:
            if '^' in data:
                data = data.replace('^', '**')

            try:
                self.coefficient = int(eval(data))
            except:
                self.coefficient = 0

            self.degree = 0
            self.literal_part = ''

        if self.coefficient < 0:
            self.coefficient = abs(self.coefficient)
            self.sign = '-'

        elif self.coefficient >= 0:
            self.sign = '+'

        self.repr = '%s%d%s' % (self.sign, self.coefficient, self.literal_part)
        if self.repr.startswith('+0x'):
            self.repr = '0'
            self.coefficient = 0
            self.literal_part = ''
            self.sign = '+'

    def __str__(self):
        return self.repr[1:] if self.repr.startswith('+') else self.repr

    def __eq__(self, monomial):
        if type(monomial) == int:
            monomial = str(monomial)

        if type(monomial) == str:
            monomial = Monomial(monomial)

        elif type(monomial) != Monomial:
            return False

        return self.repr == monomial.repr

    def __ne__(self, monomial):
        return not self == monomial

    def __pos__(self):
        return Monomial(self.repr.replace('-', '+'))

    def __neg__(self):
        return Monomial(self.repr.replace('+', '-'))

    def __add__(self, monomial):
        if type(monomial) == int:
            monomial = str(monomial)

        if type(monomial) == str:
            monomial = Monomial(monomial)

        elif not type(monomial) == Monomial:
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
        if type(monomial) == str:
            monomial = str(monomial)

        if type(monomial) == str:
            monomial = Monomial(monomial)

        if self.degree == monomial.degree:
            coefficient1 = self.coefficient
            coefficient2 = monomial.coefficient
            if self.sign == '-':
                coefficient1 *= -1

            if monomial.sign == '-':
                coefficient2 *= -1

            coefficient = coefficient1 * coefficient2
            degree = self.degree + monomial.degree
            if degree > 1:
                literal_part = 'x^%d' % degree

            else:
                literal_part = ''

            return Monomial(str(coefficient) + literal_part)

        else:
            return Polynomial(self.repr + '*' + monomial.repr)

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
        if self.repr.startswith('+'):
            return self.repr[1:]

        return self.repr


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
        if not data or not data.replace('0', '') or (data[0] in ['+', '-'] and not data[1:].replace('0', '')):
            self.monomials = {}
            self.degrees = []
            self.repr = '0'
            return

        data = data.replace(' ', '')

        # Add positive sign at the beginning of the monomials
        data = ('+' + data) if data[0] not in ['-', '+'] else data
        data = data.replace('+', 'SPLIT+')
        data = data.replace('-', 'SPLIT-')
        _monomials = data.split('SPLIT')
        monomials = []
        for monomial in _monomials:
            if not monomial:
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

        degrees = self.monomials.keys()
        degrees.sort()
        degrees.reverse()

        self.repr = ''
        for degree in degrees:
            _monomial = Monomial('0')
            for monomial in self.monomials[degree]:
                #print monomial
                _monomial += monomial

            _repr = _monomial.repr
            if not _repr.startswith('+') and not _repr.startswith('-'):
                _repr = '+' + _repr

            _repr = _repr.replace('+', ' + ')
            _repr = _repr.replace('-', ' - ')
            _repr = _repr.replace(' + 0', '')
            self.repr += _repr

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
        degrees = self.monomials.keys()
        degrees.sort()
        degrees.reverse()
        for degree in degrees:
            for monomial in self.monomials[degree]:
                if type(monomial) == str:
                    monomial = Monomial(monomial)

                if monomial.repr.strip() in ['0', '+0', '-0']:
                    continue

                yield monomial


class Ecuation(object):
    """
    **************************
    ****** LACK FICNISH ******
    **************************

    A ecuations resolver, is necesary a ecuation.
    You can pass as an argument polynomial (which is supposed to be a
    ranked ecuation 0)
    Example:
        >>> p = Polynomial('3x^2-3x+10')
        >>> e = Ecuation(p)

    You can also take a string as an argument, unmatched or matched to any
    number (if not be matched, will be taken as equated to 0)
    Example:
        >>> p = '3x^2-3x+10'
        >>> e = Ecuation(p)

        >>> p = '3x^2+10=3x'  # This is equivalent to '3x^2-3x+10=0'
        >>> e = Ecuation(p)
    """
    def __init__(self, data):

        self.polynomial = None
        self.parse_data(data)

    def parse_data(self, data):
        if type(data) in [tuple, list] and len(data) == 2:
            polynomial1, polynomial2 = data
            if type(polynomial1) == type(polynomial2):
                if type(polynomial1) == str:
                    if polynomial2.strip() != '0':
                        polynomial1 += '-(%s)' % polynomial2

                    self.polynomial = Polynomial(polynomial1)

                elif type(polynomial1) == Polynomial:
                    if str(polynomial2).strip() != '0':
                        self.polynomial = Polynomial(polynomial1) - Polynomial(polynomial2)

                    else:
                        self.polynomial = polynomial1

        elif type(data) == str:
            data = data.replace(' ', '')
            if not '=' in data:
                self.polynomial = Polynomial(data)

            elif '=' in data and data.count('=') == 1:
                polynomial1, polynomial2 = data.split('=')
                if polynomial2.strip() != '0':
                    polynomial1 += '-(%s)' % polynomial2

                self.polynomial = Polynomial(polynomial1)

        elif type(data) == Polynomial:
            self.polynomial = data

    def __repr__(self):
        return self.polynomial.repr + ' = 0'
