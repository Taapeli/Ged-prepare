#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016      TimNal
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Gramps registration file
"""

#------------------------------------------------------------------------
#
#  Import / Database Processing / Import place hierarchies from cvs file 
#
#------------------------------------------------------------------------

register(IMPORT, 
    id    = 'Import Places',
    name  = _("Reference Place hierarchies with optional tags from a csv file"),
    description =  _("Import Reference Place hierarchies with optional tags from a csv file"),
    version = '0.1',
    gramps_target_version = "4.2",
    status = STABLE,
    fname = 'importplaces.py',
    import_function = 'importPlaceHierarchy',
    extension = 'pcsv'
)
