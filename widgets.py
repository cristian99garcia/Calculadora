#!/usr/bin/python2
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

import cairo

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject

from expressions import Monomial
from expressions import Polynomial
from expressions import Equation
from expressions import Function

import globals as G


class GraphArea(Gtk.DrawingArea):

    def __init__(self, functions=[]):
        Gtk.DrawingArea.__init__(self)

        self.functions = []
        for function in functions:
            if type(function) == str:
                function = Function(function)

            if type(function) == Function:
                self.functions.append(function)

        self.context = None
        self.background_color = (1, 1, 1)
        self.axis_color = (0, 0, 0)
        self.grid_color = (0.8, 0.8, 0.8)
        self.line_color = (0, 0, 1)
        self.line_width = 2
        self.axis_width = 4
        self.grid_width = 1
        self.unit_space = 50
        self.font_size = self.unit_space / 2.0
        self.font_color = (0.4, 0.4, 0.4)
        self.points = []
        self.point_color = (1, 0, 0)
        self.point_width = 5
        self.init_x = 0
        self.init_y = 0
        self.drag_point = None
        self.min_x = 0
        self.max_x = 0
        self.min_y = 0
        self.max_y = 0

        self.set_can_focus(True)
        self.add_events(Gdk.EventMask.SCROLL_MASK |
                        Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.BUTTON_MOTION_MASK)

        self.connect('scroll-event', self.__scroll_event_cb)
        self.connect('button-press-event', self.__button_press_event_cb)
        self.connect('button-release-event', self.__button_release_event_cb)
        self.connect('motion-notify-event', self.__button_motion_event_cb)
        self.connect('draw', self.__draw_cb)

    def __scroll_event_cb(self, widget, event):
        scroll = event.get_scroll_direction()[1]
        if scroll == Gdk.ScrollDirection.UP:
            if self.unit_space < 150:
                self.unit_space += 10

        elif scroll == Gdk.ScrollDirection.DOWN:
            if self.unit_space > 20:
                self.unit_space -= 10

        GObject.idle_add(self.queue_draw)

    def __button_press_event_cb(self, widget, event):
        self.drag_point = (event.x - self.init_x, event.y - self.init_y)

    def __button_release_event_cb(self, widget, event):
        self.drag_point = None

    def __button_motion_event_cb(self, widget, event):
        if self.drag_point:
            self.init_x = event.x - self.drag_point[0]
            self.init_y = event.y - self.drag_point[1]

            GObject.idle_add(self.queue_draw)

    def __draw_cb(self, widget, context):
        allocation = self.get_allocation()
        self.context = context
        self.width = allocation.width
        self.height = allocation.height

        self.render()

    def add_function(self, function):
        if type(function) == str:
            function = Function(function)

        if type(function) == Function:
            self.functions.append(function)

    def remove_function(self, function):
        if function in self.functions:
            self.functions.remove(function)

    def add_point(self, x, y):
        self.points.append((x, y))

    def remove_point(self, x, y):
        if (x, y) in self.points:
            self.points.remove((x, y))

    def render(self):
        self.render_background()
        self.render_grid()
        self.render_axis()

        for function in self.functions:
            self.render_graph(function)

        for point in self.points:
            self.draw_point(*point)

    def render_background(self):
        self.context.set_source_rgb(*self.background_color)
        self.context.rectangle(0, 0, self.width, self.height)
        self.context.fill()

    def render_grid(self):
        x = self.init_x + self.width / 2.0
        y = self.height / 2.0 + self.init_y

        self.context.set_line_width(self.grid_width)

        _x = x + self.axis_width / 2.0
        n = 0
        while _x < self.width:
            _x += self.unit_space
            self.context.set_source_rgb(*self.grid_color)
            self.context.move_to(_x, 0)
            self.context.line_to(_x, self.height)

            self.context.set_source_rgb(*self.font_color)
            self.context.set_font_size(self.font_size)
            self.context.move_to(_x - self.unit_space, self.height / 2.0 + self.init_y + self.unit_space / 2.0)
            self.context.show_text(str(n))

            n += 1
            self.max_x = n + 2

        _x = x - self.axis_width / 2.0
        n = 0
        while _x > 0:
            self.context.set_source_rgb(*self.grid_color)
            _x -= self.unit_space
            self.context.move_to(_x, 0)
            self.context.line_to(_x, self.height)

            if n != 0:
                self.context.set_source_rgb(*self.font_color)
                self.context.set_font_size(self.font_size)
                self.context.move_to(_x + self.unit_space, self.height / 2.0 + self.init_y + self.unit_space / 2.0)
                self.context.show_text('-' + str(n))

            n += 1
            self.min_x = -n - 2

        self.min_x
        _y = y + self.axis_width / 2.0
        n = 0
        while _y < self.height:
            _y += self.unit_space
            self.context.move_to(0, _y)
            self.context.line_to(self.width, _y)

            if n != 0:
                self.context.set_source_rgb(*self.font_color)
                self.context.set_font_size(self.font_size)
                self.context.move_to(self.width / 2.0 + self.init_x + self.font_size / 3.0, _y - self.unit_space / 2.0)
                self.context.show_text('-' + str(n))

            n += 1
            self.min_y = -n - 2

        _y = y - self.axis_width / 2.0
        n = 0
        while _y > 0:
            _y -= self.unit_space
            self.context.move_to(0, _y)
            self.context.line_to(self.width, _y)

            if n != 0:
                self.context.set_source_rgb(*self.font_color)
                self.context.set_font_size(self.font_size)
                self.context.move_to(self.width / 2.0 + self.init_x + self.font_size / 3.0, _y + self.unit_space * 3 / 2.0)
                self.context.show_text(str(n))

            n += 1
            self.max_y = n + 2

        self.context.stroke()

    def render_axis(self):
        self.context.set_source_rgb(*self.axis_color)
        self.context.set_line_width(self.axis_width)
        self.context.move_to(0, self.height / 2.0 + self.init_y)
        self.context.line_to(self.width, self.height / 2.0 + self.init_y)
        self.context.move_to(self.width / 2.0 + self.init_x, 0)
        self.context.line_to(self.width / 2.0 + self.init_x, self.height)
        self.context.stroke()

    def render_graph(self, function):
        if function.degree in [0, 1]:
            # Draw a line
            # General expresion:
            #   ax + b
            max_x = float(self.max_x)
            max_y = float(function(max_x))
            min_x = float(self.min_x)
            min_y = float(function(min_x))
            _x1 = 0
            _y1 = 0
            _x2 = 0
            _y2 = 0
            if max_x != 0:
                _x1 = (self.grid_width * (-0.5 if min_x > 0 else 0.5)) + (self.line_width * (-0.5 if max_x > 0 else 0.5))

            if max_y != 0:
                _y1 = (self.grid_width * (-0.5 if min_y > 0 else 0.5)) + (self.line_width * (-0.5 if max_y > 0 else 0.5))

            if min_x != 0:
                _x2 = (self.grid_width * (-0.5 if min_x > 0 else 0.5)) + (self.line_width * (-0.5 if min_x > 0 else 0.5))

            if min_y != 0:
                _y2 = (self.grid_width * (-0.5 if min_y > 0 else 0.5)) + (self.line_width * (-0.5 if min_y > 0 else 0.5))

            x1 = self.width / 2.0 + self.init_x + min_x * self.unit_space + _x1
            y1 = self.height / 2.0 + self.init_y - min_y * self.unit_space + _y1
            x2 = self.width / 2.0 + self.init_x + max_x * self.unit_space + _x2
            y2 = self.height / 2.0 + self.init_y - max_y * self.unit_space + _y2

            self.context.set_source_rgb(*self.line_color)
            self.context.set_line_width(self.line_width)
            self.context.move_to(x1, y1)
            self.context.line_to(x2, y2)
            self.context.stroke()

            self.add_point(0, float(function(0)))

        elif function.degree == 2:
            # Draw a parable
            # General expresion:
            #   ax^2 + bx + c
            monomials = function.polynomial.monomials
            a = int(monomials[2][0].sign + str(monomials[2][0].coefficient))
            b = int(monomials[1][0].sign + str(monomials[1][0].coefficient)) if 1 in monomials else 0
            c = int(monomials[0][0].sign + str(monomials[0][0].coefficient)) if 0 in monomials else 0

            # Vertex
            x = -(b / 2.0 * a)
            y = float(function(x))
            self.draw_point(x, y)

            #print(function(self.width / 2.0 / self.unit_space))
            x1 = 1.0
            y1 = float(function(x1))
            x2 = -1.0
            y2 = y1
            x3 = 2.0
            y3 = float(function(x3))
            x4 = -2.0
            y4 = y3

            # FIXME: NO FUNCIONAAAA, porque cairo acorta la distancia, sin pasar por todos los puntos especificados
            self.draw_point(x1, y1)
            self.draw_point(x2, y2)
            self.draw_point(x3, y3)
            self.draw_point(x4, y4)

            self.draw_curve(x3, y3, x, y, x4, y4)
            #self.draw_curve(x4, y4, x2, y2, x, y)
            #self.draw_curve(x3, y3, x1, y1, x, y)

    def draw_point(self, x, y):
        x = self.width / 2.0 + self.init_x + (float(x) * self.unit_space)
        if x > self.init_x + self.width / 2.0:
            x += self.axis_width / 2.0

        elif x < self.init_x + self.width / 2.0:
            x -= self.axis_width / 2.0

        y = self.height / 2.0 + self.init_y - (float(y) * self.unit_space)
        if y > self.init_y + self.height / 2.0:
            y += self.axis_width / 2.0

        elif y < self.init_y + self.height / 2.0:
            y -= self.axis_width / 2.0

        self.context.set_source_rgb(*self.point_color)
        self.context.arc(x, y, self.point_width, 0, 2 * G.PI)
        self.context.fill()

    def draw_curve(self, x1, y1, x2, y2, x3, y3):
        """
        x1 = self.width / 2.0 + x1 * self.unit_space
        y1 = self.height / 2.0 - self.init_y - y1 * self.unit_space
        x2 = self.width / 2.0 + x2 * self.unit_space
        y2 = self.height / 2.0 - self.init_y - y2 * self.unit_space
        x3 = self.width / 2.0 + x3 * self.unit_space
        y3 = self.height / 2.0 - self.init_y - y3 * self.unit_space

        #print(x1, y1, x2, y2, x3, y3)
        self.context.curve_to(x1, y1, x2, y2, x3, y3)
        self.context.stroke()
        """

class Entry(Gtk.ScrolledWindow):

    __gsignals__ = {
        'activate': (GObject.SIGNAL_RUN_FIRST, None, []),
        'changed': (GObject.SIGNAL_RUN_FIRST, None, []),
    }

    __gtype_name__ = 'Entry'

    def __init__(self, sugar=False):
        Gtk.ScrolledWindow.__init__(self)

        self.__view = Gtk.TextView()
        self.__buffer = self.__view.get_buffer()

        font = 'Bold 25' if not sugar else 'Bold 60'
        size = 45 if not sugar else 100
        self.__view.modify_font(Pango.FontDescription(font))
        self.__view.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('#303030'))
        self.__view.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse('#CCCCCC'))
        self.__view.modify_bg(Gtk.StateType.SELECTED, Gdk.color_parse('#AAAAAA'))
        self.__view.modify_fg(Gtk.StateType.SELECTED, Gdk.color_parse('#FFFFFF'))

        self.set_size_request(-1, size)
        self.add_events(Gdk.EventMask.KEY_RELEASE_MASK)
        self.connect('key-release-event', self.__key_release_event_cb)
        self.__buffer.connect('changed', self.__changed_cb)

        self.add(self.__view)

    def __key_release_event_cb(self, textview, event):
        if event.keyval == 65293:  # 65293 = Enter
            self.backspace()
            self.emit('activate')
            return False

    def __changed_cb(self, buffer):
        self.emit('changed')

    def set_text(self, texto):
        self.__buffer.set_text(texto)

    def get_text(self):
        start, end = self.__buffer.get_bounds()
        return self.__buffer.get_text(start, end, 0)

    def insert_at_cursor(self, text):
        insert_parenthesis = False
        if text.endswith('()'):
            text = text[:-1]
            insert_parenthesis = True

        self.__buffer.insert_at_cursor(text)

        if insert_parenthesis:
            pos = self.__buffer.get_property('cursor-position')
            text = self.get_text()
            text = text[:pos] + ')' + text[pos:]
            self.set_text(text)
            textiter = self.__buffer.get_iter_at_offset(pos)
            self.__buffer.place_cursor(textiter)

    def backspace(self):
        pos = self.__buffer.get_property('cursor-position')
        textiter = self.__buffer.get_iter_at_offset(pos)
        self.__buffer.backspace(textiter, True, True)


class ButtonBase(Gtk.DrawingArea):

    __gsignals__ = {
        'clicked': (GObject.SIGNAL_RUN_FIRST, None, []),
    }

    def __init__(self, label):
        Gtk.DrawingArea.__init__(self)

        self.context = None
        self.limit = 0
        self.processes = {}  # {(x, y): progress}
        self.width = 0
        self.height = 0
        self.label = label
        self.label_size = 30
        self.label_font = 'Bold'
        self.label_color = (1, 1, 1)
        self.effect_color = (0.5, 0.5, 0.5)
        self.mouse_in_color = (0.075, 0.075, 0.075)
        self.mouse_out_color = (0.3, 0.3, 0.3)
        self.insensitive_color = (0.5, 0.5, 0.5)
        self.background_color = self.mouse_out_color
        self.__mouse_in = False

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.ENTER_NOTIFY_MASK |
                        Gdk.EventMask.LEAVE_NOTIFY_MASK)

        self.connect('draw', self.__draw_cb)
        self.connect('button-release-event', self.__button_release_event_cb)
        self.connect('enter-notify-event', self.__enter_notify_event_cb)
        self.connect('leave-notify-event', self.__leave_notify_event_cb)

    def __draw_cb(self, area, context):
        allocation = self.get_allocation()
        self.context = context
        self.width = allocation.width
        self.height = allocation.height

        self.limit = max(self.width, self.height)
        self.label_size = min(self.width, self.height) / 2.0

        self.context.set_source_rgb(*self.background_color)
        self.context.rectangle(0, 0, self.width, self.height)
        self.context.fill()

        self.__render()

    def __button_release_event_cb(self, area, event):
        if event.button == 1:
            self.processes[(event.x, event.y)] = 0
            self.emit('clicked')

    def __enter_notify_event_cb(self, area, event):
        self.background_color = self.mouse_in_color
        self.__mouse_in = True
        self.__render()

    def __leave_notify_event_cb(self, area, event):
        self.background_color = self.mouse_out_color
        self.__mouse_in = False
        self.__render()

    def remove_processes(self, lista):
        if not lista:
            return

        backup = self.processes
        self.processes = {}

        for coords, progress in backup.items():
            if not coords in lista:
                self.processes[coords] = progress

    def __render(self):
        if not self.context:
            return

        if self.label:
            self.context.set_font_size(self.label_size)
            self.context.select_font_face(self.label_font,
                                          cairo.FONT_SLANT_NORMAL,
                                          cairo.FONT_WEIGHT_NORMAL)

            w = self.context.text_extents(self.label)[2]
            h = self.context.text_extents(self.label)[3]
            x = (self.width - w) / 2.0
            y = (self.height + h) / 2.0

            self.context.move_to(x, y)
            self.context.set_source_rgb(*self.label_color)
            self.context.show_text(self.label)

        processes_to_remove = []
        for coords, progress in self.processes.items():
            transparency = 1.0 - (1.0 / self.limit * progress)
            color = self.effect_color + (transparency,)
            self.context.set_source_rgba(*color)
            self.context.arc(coords[0], coords[1], progress, 0, 2 * G.PI)
            self.context.fill()

            self.processes[coords] = progress + 5

            if self.processes[coords] >= self.limit:
                processes_to_remove.append(coords)

        self.remove_processes(processes_to_remove)

        GObject.idle_add(self.queue_draw)


class ButtonSimple(ButtonBase):

    def __init__(self, etiqueta):
        ButtonBase.__init__(self, etiqueta)

        self.label_size = 30
        self.label_color = (1, 1, 1)
        self.effect_color = (0.6, 0.6, 0.6)
        self.mouse_in_color = (0.4, 0.4, 0.4)
        self.mouse_out_color = (
            0.2980392156862745, 0.2980392156862745, 0.2980392156862745)
        self.background_color = self.mouse_out_color


class ButtonOperator(ButtonBase):

    def __init__(self, etiqueta):
        ButtonBase.__init__(self, etiqueta)

        self.label_color = (1, 1, 1)
        self.effect_color = (1.0, 1.0, 1.0)
        self.mouse_in_color = (0.2, 0.3, 0.8)
        self.mouse_out_color = (0.38, 0.52, 1.0)
        self.background_color = self.mouse_out_color


class ButtonSpecial(ButtonBase):

    def __init__(self, etiqueta):
        ButtonBase.__init__(self, etiqueta)

        self.label_color = (1, 1, 1)
        self.effect_color = (1.0, 1.0, 1.0)
        self.mouse_in_color = (0.4, 1.0, 0.8)
        self.mouse_out_color = (
            0.25098039215686274, 0.7411764705882353, 0.6196078431372549)
        self.insensitive_color = (0.35, 0.84, 0.72)
        self.background_color = self.mouse_out_color























"""
class Calculator(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.entry = Gtk.Entry()
        self.entry.connect('changed', self.__text_changed_cb)
        self.pack_start(self.entry, False, False, 2)

    def __text_changed_cb(self, entry):
        print(self.entry.get_text())


win = Gtk.Window()
calc = Calculator()
#area = GraphArea('f(x) = 3x^2')

win.connect('destroy', Gtk.main_quit)

win.add(calc)
win.show_all()

Gtk.main()
"""
