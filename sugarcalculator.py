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

import os

from gi.repository import Gtk
from gi.repository import Gdk

from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton

from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.activity import activity

from expressions import Expression

from widgets import Entry
from widgets import ButtonSimple
from widgets import ButtonOperator
from widgets import ButtonSpecial

import globals as G


class Calculator(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('#4C4C4C'))

        self.vbox = Gtk.VBox()
        self.vbox.set_border_width(10)

        self.entry = Entry(sugar=True)
        self.entry.connect('activate', self.calculate)
        self.vbox.pack_start(self.entry, False, False, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(1000)

        self.stack_switcher = Gtk.StackSwitcher()
        self.stack_switcher.set_stack(self.stack)
        self.stack_switcher.set_hexpand(True)
        self.stack_switcher.set_halign(Gtk.Align.CENTER)
        self.vbox.pack_start(self.stack_switcher, False, False, 10)
        self.vbox.pack_start(self.stack, True, True, 0)

        self.make_buttons()
        self.make_toolbar()

        self.set_canvas(self.vbox)
        self.show_all()

    def calculate(self, entry):
        expression = str(Expression(self.entry.get_text()))
        self.entry.set_text('0' + expression if expression[0] == '.' else expression)

    def make_buttons(self):
        grid = Gtk.Grid()
        self.stack.add_titled(grid, 'simple', 'Simple')

        text = self.entry.get_text()
        buttons = [['7', '8', '9'],
                   ['4', '5', '6'],
                   ['1', '2', '3'],
                   ['.', '0', '=']]

        n_row = 0
        for row in buttons:
            columna = 0
            for signo in row:
                button = self.make_button(signo, _class=ButtonSimple)
                grid.attach(button, columna, n_row, 1, 1)

                columna += 1

            n_row += 1

        self.vbox_operators = Gtk.VBox()
        grid.attach(self.vbox_operators, 4, 0, 1, 4)

        button = self.make_button(G.SYMBOL_DEL, _class=ButtonOperator)
        self.vbox_operators.add(button)

        for operator in G.OPERATORS:
            button = self.make_button(operator, _class=ButtonOperator)
            self.vbox_operators.add(button)

        hbox = Gtk.HBox()
        self.stack.add_titled(hbox, 'complex', 'Complex')

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
        stack.set_transition_duration(1000)

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        stack_switcher.set_halign(Gtk.Align.CENTER)
        hbox.pack_start(stack, True, True, 0)
        hbox.pack_end(stack_switcher, False, False, 10)

        grid = Gtk.Grid()
        stack.add_titled(grid, 'first', '')

        buttons = [['sen', 'cos', 'tan', 'In'],
                   ['log', '!', 'PI', 'e'],
                   ['^', '(', ')', 'V'],
                   ['¡', '%', 'x', 'f(x) = ']]

        n_row = 0
        for row in buttons:
            columna = 0
            for signo in row:
                button = self.make_button(signo, _class=ButtonSpecial)
                grid.attach(button, columna, n_row, 1, 1)

                columna += 1

            n_row += 1

        grid = Gtk.Grid()
        stack.add_titled(grid, 'second', '')

        buttons = [['A', 'B', 'C'],
                   ['D', 'E', 'F'],
                   ['Dec', 'Hex', 'Bin']]

        n_row = 0
        for row in buttons:
            columna = 0
            for signo in row:
                button = self.make_button(signo, _class=ButtonSpecial)
                grid.attach(button, columna, n_row, 1, 1)

                columna += 1

            n_row += 1

        button1, button2 = stack_switcher.get_children()
        stack_switcher.remove(button1)
        stack_switcher.remove(button2)

        buttonbox = Gtk.VButtonBox()
        buttonbox.set_layout(Gtk.ButtonBoxStyle.CENTER)
        hbox.pack_end(buttonbox, False, False, 10)

        buttonbox.add(button1)
        buttonbox.add(button2)

    def make_button(self, label, _class=None):
        button = _class(label) if _class else Gtk.Button(label)
        button.set_hexpand(True)
        button.set_vexpand(True)

        if label in ['sen', 'cos', 'tan', 'In', 'log']:
            label += '()'

        button.connect('clicked', self.insert_from_button, label)
        return button

    def make_toolbar(self):
        toolbarbox = ToolbarBox()

        activity_button = ActivityToolbarButton(self)
        toolbarbox.toolbar.insert(activity_button, 0)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbarbox.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        stop_button.props.accelerator = '<Ctrl>Q'
        toolbarbox.toolbar.insert(stop_button, -1)

        self.set_toolbar_box(toolbarbox)

    def insert_from_button(self, button, label):
        if label != G.SYMBOL_DEL:
            self.entry.insert_at_cursor(label)

        else:
            self.entry.backspace()
