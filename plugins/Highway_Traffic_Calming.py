#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyright Osmose Contributors 2026                                    ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

from modules.OsmoseTranslation import T_
from modules.Stablehash import stablehash
from plugins.Plugin import Plugin


class Highway_Traffic_Calming(Plugin):

    crossing_tags = (
        ("footway", "crossing"),
        ("cycleway", "crossing"),
        ("path", "crossing"),
    )

    def init(self, logger):
        Plugin.init(self, logger)
        self.errors[20901] = self.def_class(item = 2090, level = 3, tags = ['tag', 'highway', 'fix:survey'],
            title = T_('Traffic calming tag on crossing way'),
            detail = T_(
'''A crossing way is tagged with `traffic_calming=*`.

Traffic calming describes a feature affecting vehicle traffic. A separately
mapped crossing way describes the pedestrian, bicycle, or path crossing
geometry.'''),
            fix = T_(
'''If this is a raised crossing, move `traffic_calming=*` to the node or road
where the traffic calming physically applies.

If the tag was added to the crossing way by mistake and there is no traffic
calming feature to map elsewhere, remove `traffic_calming=*` from the crossing
way.'''),
            trap = T_(
'''Do not remove the tag without checking whether a traffic calming feature still
needs to be mapped on a node or road.'''))

    def way(self, data, tags, nds):
        if 'traffic_calming' not in tags:
            return []

        if not any(tags.get(k) == v for k, v in self.crossing_tags):
            return []

        return [{
            'class': 20901,
            'subclass': stablehash(tags['traffic_calming']),
            'text': T_("traffic_calming={0} on crossing way", tags['traffic_calming'])
        }]


###########################################################################
from plugins.Plugin import TestPluginCommon


class Test(TestPluginCommon):
    def test(self):
        a = Highway_Traffic_Calming(None)
        self.set_default_config(a)
        a.init(None)

        for crossing_key in ("footway", "cycleway", "path"):
            tags = {crossing_key: "crossing", "traffic_calming": "table"}
            self.check_err(a.way(None, tags, None), tags, expected={"class": 20901})

        self.check_not_err(a.way(None, {"highway": "residential", "traffic_calming": "hump"}, None))
        self.check_not_err(a.way(None, {"highway": "service", "traffic_calming": "chicane"}, None))
        self.check_not_err(a.way(None, {"highway": "footway", "footway": "traffic_island", "traffic_calming": "island"}, None))
        self.check_not_err(a.way(None, {"highway": "footway", "footway": "crossing", "crossing": "uncontrolled"}, None))
        self.check_not_err(a.way(None, {"highway": "cycleway", "cycleway": "crossing", "crossing": "uncontrolled"}, None))
