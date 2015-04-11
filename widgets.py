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
        self.menu = None
        self.f_cursor_pos = (0.0, 0.0)
        self.i_cursor_pos = (0, 0)

        self.add_events(Gdk.EventMask.SCROLL_MASK |
                        Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)

        self.connect('scroll-event', self.__scroll_event_cb)
        self.connect('button-press-event', self.__button_press_event_cb)
        self.connect('button-release-event', self.__button_release_event_cb)
        self.connect('motion-notify-event', self.__button_motion_event_cb)
        self.connect('draw', self.__draw_cb)

    def __scroll_event_cb(self, widget, event):
        scroll = event.get_scroll_direction()[1]
        if scroll == Gdk.ScrollDirection.UP:
            if self.unit_space < 200:
                self.unit_space += 10

        elif scroll == Gdk.ScrollDirection.DOWN:
            if self.unit_space > 20:
                self.unit_space -= 10

        self.font_size = self.unit_space / 2.0
        GObject.idle_add(self.queue_draw)

    def __button_press_event_cb(self, widget, event):
        if event.button == 1:
            self.drag_point = (event.x - self.init_x, event.y - self.init_y)

        elif event.button == 3:
            self.make_menu(event.x, event.y)
            self.menu.popup(None, None, None, None, event.button, event.time)
            return True

    def __button_release_event_cb(self, widget, event):
        self.drag_point = None

    def __button_motion_event_cb(self, widget, event):
        fx, fy = self.get_symbolic_point(event.x, event.y)
        self.f_cursor_pos = (fx, fy)
        self.i_cursor_pos = (int(round(fx)), int(round(fy)))

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

    def make_menu(self, x, y):
        fx, fy = self.f_cursor_pos
        ix, iy = self.i_cursor_pos
        self.menu = Gtk.Menu()

        item = Gtk.MenuItem('Go to (0.0)')
        item.connect('activate', lambda item: self.go_to(0, 0, True))
        self.menu.append(item)

        if not (ix, iy) in self.points:
            item = Gtk.MenuItem('Make a point to (%d; %d)' % (ix, iy))
            item.connect('activate', lambda item: self.add_point(ix, iy))

        else:
            item = Gtk.MenuItem('Remove point (%d; %d)' % (ix, iy))
            item.connect('activate', lambda item: self.remove_point(ix, iy))

        self.menu.append(item)

        item = Gtk.MenuItem('Make a point to (%f; %f)' % (fx, fy))
        item.connect('activate', lambda item: self.add_point(fx, fy))

        self.menu.append(item)
        self.menu.show_all()

    def go_to(self, x, y, from_menu=True):
        if from_menu:
            self.unit_space = 50
            self.font_size = 25.0

        self.init_x = x
        self.init_y = y
        GObject.idle_add(self.queue_draw)

    def add_function(self, function, update=True):
        if type(function) == str:
            function = Function(function)
            color = self.line_color

        if type(function) == Function:
            self.functions.append(function)
            if update:
                GObject.idle_add(self.queue_draw)

    def remove_function(self, function, update=True):
        if function in self.functions:
            self.functions.remove(function)
            if update:
                GObject.idle_add(self.queue_draw)

    def add_point(self, x, y, update=True):
        if not (x, y) in self.points:
            self.points.append((x, y))
            if update:
                GObject.idle_add(self.queue_draw)

    def remove_point(self, x, y, update=True):
        if (x, y) in self.points:
            self.points.remove((x, y))
            if update:
                GObject.idle_add(self.queue_draw)

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
        self.context.set_font_size(self.font_size)

        _x = x + self.axis_width / 2.0
        n = 0
        while _x < self.width + 2:
            _x += self.unit_space
            self.context.set_source_rgb(*self.grid_color)
            self.context.move_to(_x, 0)
            self.context.line_to(_x, self.height)

            self.context.set_source_rgb(*self.font_color)
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
        color = function.color
        if function.degree in [0, 1]:
            # Draw a line
            # General expresion:
            #   ax + b
            x1, y1 = self.get_real_point(float(self.max_x), float(function(self.max_x)))
            x2, y2 = self.get_real_point(float(self.min_x), float(function(self.min_x)))

            self.context.set_source_rgb(*color)
            self.context.set_line_width(self.line_width)
            self.context.move_to(x1, y1)
            self.context.line_to(x2, y2)
            self.context.stroke()

            self.add_point(0, float(function(0)))

        elif function.degree == 2:
            # Draw a parable
            # General expresion:
            #   ax^2 + bx + c

            a = function.get_coefficient(2)
            b = function.get_coefficient(1)
            c = function.get_coefficient(0)

            m = 1 if a >= 0 else -1
            vx, vy = function.get_vertex()

            self.context.set_line_width(self.line_width)
            self.context.set_source_rgb(*function.color)
            self.context.move_to(*self.get_real_point(*function.get_vertex()))

            n1 = self.min_x - 2
            n2 = self.max_x + 2

            self.context.move_to(*self.get_real_point(n1, function(n1)))

            for e in range(n1, n2):
                for i in range(0, 11):
                    x = e + (i * 0.1) - (abs(b) * m)
                    y = function(x)
                    _x, _y = self.get_real_point(x, y)
                    if _y > self.unit_space * -2 and _y < self.height + self.unit_space * 2:
                        self.context.line_to(_x, _y)

                    else:
                        self.context.move_to(_x, _y)

            self.context.stroke()

    def draw_point(self, x, y, color=None, size=None):
        x, y = self.get_real_point(x, y)
        if color is None:
            color = self.point_color

        if len(color) == 3:
            color += (1.0,)

        if not size:
            size = self.point_width

        self.context.set_source_rgba(*color)
        self.context.arc(x, y, size, 0, 2 * G.PI)
        self.context.fill()

    def draw_curve(self, x1, y1, x2, y2, x3, y3, color=None, line_width=None):
        x1, y1 = self.get_real_point(x1, y1)
        x2, y2 = self.get_real_point(x2, y2)
        x3, y3 = self.get_real_point(x3, y3)

        if not color:
            color = self.line_color

        if not line_width:
            line_width = self.line_width

        self.context.set_source_rgb(*color)
        self.context.set_line_width(self.line_width)

        self.context.move_to(x1, y1)
        self.context.curve_to(x1, y1, x2, y2, x3, y3)
        self.context.stroke()

    def get_real_point(self, x, y):
        _x = x * self.unit_space
        _x += self.width / 2.0
        _x += self.init_x
        if x != 0:
            _x += self.axis_width / 2.0 if x > 0 else self.axis_width / - 2.0

        _y = y * -self.unit_space
        _y += self.height / 2.0
        _y += self.init_y
        if y != 0:
            _y -= self.axis_width / 2.0 if y > 0 else self.axis_width / - 2.0

        return (_x, _y)

    def get_symbolic_point(self, x, y):
        _x = x
        _y = y

        _x -= self.width / 2.0
        _x -= self.init_x
        if x != 0:
            _x -= self.axis_width / 2.0 if x > 0 else self.axis_width / - 2.0
        _x /= self.unit_space

        _y -= self.height / 2.0
        _y -= self.init_y
        if y != 0:
            _y -= self.axis_width / 2.0 if y > 0 else self.axis_width / - 2.0

        _y /= -self.unit_space

        return (_x, _y)


class GraphList(Gtk.ScrolledWindow):

    __gsignals__ = {
        'remove-function': (GObject.SIGNAL_RUN_FIRST, None, [object]),
        'update-request': (GObject.SIGNAL_RUN_FIRST, None, []),
    }

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.rows = {}

        self.listbox = Gtk.ListBox()
        self.add(self.listbox)
        self.set_size_request(200, -1)

    def add_function(self, function):
        color = G.color_cairo_to_gdk(function.color)

        row = Gtk.ListBoxRow()
        self.rows[function] = row
        self.listbox.add(row)

        hbox = Gtk.HBox()
        row.add(hbox)

        label = Gtk.Label(function.polynomial.repr)
        label.modify_fg(Gtk.StateType.NORMAL, color)
        hbox.pack_start(label, False, False, 0)

        image = Gtk.Image.new_from_stock(Gtk.STOCK_REMOVE, Gtk.IconSize.BUTTON)
        button = Gtk.Button(image=image)
        button.connect('clicked', self._remove_function, function)
        hbox.pack_end(button, False, False, 10)

        button = Gtk.ColorButton()
        button.set_color(color)
        button.connect('color-set', self.choice_color, function)
        hbox.pack_end(button, False, False, 0)

        self.show_all()

    def remove_function(self, function):
        self.listbox.remove(self.rows[function])

    def _remove_function(self, button, function):
        self.emit('remove-function', function)

    def choice_color(self, color, function):
        if type(color) == Gtk.ColorButton:
            color = G.color_gdk_to_cairo(color.get_color())

        function.color = color


class GraphManager(Gtk.HBox):

    def __init__(self):
        Gtk.HBox.__init__(self)

        self.area = GraphArea()
        self.list = GraphList()

        self.list.connect('remove-function', lambda w, f: self.remove_function(f))
        self.list.connect('update-request', self.update_request)

        self.pack_start(self.area, True, True, 0)
        self.pack_end(self.list, False, False, 0)

    def add_function(self, function):
        self.area.add_function(function)
        self.list.add_function(function)

    def remove_function(self, function):
        self.area.remove_function(function)
        self.list.remove_function(function)

    def update_request(self, *args):
        self.area.queue_draw()


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
