'''
Created on 27.7.2017

@author: TimNal
'''
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
Filter rule to match persons having a personal event with a specified role.
"""
#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

import logging
LOG = logging.getLogger("filters")
LOG.setLevel(logging.INFO)

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ....lib.eventroletype import EventRoleType
from .. import Rule

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasEventRole(Rule):
    """Rule that checks for a person having a personal event with a specified role"""

    labels      = [ _('Role:'), ]
    name        =  _('People having personal events with a specified role')
    description = _("Matches people having a personal event with a specified role ")

    def apply(self, dbase, person):
        for event_ref in person.get_event_ref_list():
            if not event_ref:
                continue
#            if event_ref.role == EventRoleType.CUSTOM :
            LOG.debug('Event role = %s and argument role is %s ' % (event_ref.role, self.list[0]))
            if event_ref.role == self.list[0] :
                # Only match unknown
                return True
        return False