#!/usr/bin/env python
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
from .Analyser_Osmosis import Analyser_Osmosis


sql10 = """
SELECT
    id,
    ST_AsText(way_locate(linestring)),
    tags->'traffic_calming'
FROM
    {0}ways
WHERE
    tags?'traffic_calming' AND
    (
        tags->'footway' = 'crossing' OR
        tags->'cycleway' = 'crossing' OR
        tags->'path' = 'crossing'
    )
"""


class Analyser_Osmosis_Highway_Traffic_Calming(Analyser_Osmosis):

    requires_tables_full = ['ways']
    requires_tables_diff = ['touched_ways']

    def __init__(self, config, logger = None):
        Analyser_Osmosis.__init__(self, config, logger)
        self.classs_change[1] = self.def_class(item = 2090, level = 3, tags = ['tag', 'highway', 'fix:survey'],
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

        self.callback10 = lambda res: {
            "class": 1, "data": [self.way_full, self.positionAsText],
            "text": T_("traffic_calming={0} on crossing way", res[2])
        }

    def analyser_osmosis_full(self):
        self.run(sql10.format(""), self.callback10)

    def analyser_osmosis_diff(self):
        self.run(sql10.format("touched_"), self.callback10)


###########################################################################

from .Analyser_Osmosis import TestAnalyserOsmosis


class Test(TestAnalyserOsmosis):
    @classmethod
    def setup_class(cls):
        from modules import config
        TestAnalyserOsmosis.setup_class()
        cls.analyser_conf = cls.load_osm("tests/osmosis_highway_traffic_calming.osm",
                                         config.dir_tmp + "/tests/osmosis_highway_traffic_calming.test.xml",
                                         {"proj": 2154})

    def test_classes(self):
        with Analyser_Osmosis_Highway_Traffic_Calming(self.analyser_conf, self.logger) as a:
            a.analyser()

        self.root_err = self.load_errors()
        self.check_err(cl="1", elems=[("way", "100")])
        self.check_err(cl="1", elems=[("way", "110")])
        self.check_err(cl="1", elems=[("way", "120")])
        self.check_num_err(3)
