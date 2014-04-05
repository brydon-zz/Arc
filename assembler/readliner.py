"""
A basic class that implements the readline interface.
Useful for working with Tokenizer.
It takes a single line string as an argument and places it in the object.
The readline function then just returns that line.

    Copyright (C) 2014 Brydon Eastman

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA. Or by
    email to brydon.eastman@gmail.com.
"""


class ReadLiner(object):
    """ ReadLiner(string) creates an object compatible with the readline
    interface. Such that the first call to ReadLiner.readline() returns string
    and any subsequent calls return an empty string.
    """

    def __init__(self, string):
        self.string = string
        self.EOF = False

    def readline(self, size=-1):
        if self.EOF:
            return ""

        self.EOF = True

        if size == -1:
            return self.string
        else:
            try:
                self.string[size]
                return self.string[size]
            except IndexError:
                return self.string
