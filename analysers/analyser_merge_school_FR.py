#!/usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frédéric Rodrigo 2012-2020, Noémie Lehuby 2025             ##
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
from .Analyser_Merge import Analyser_Merge_Point, SourceOpenDataSoft, CSV, Load_XY, Conflate, Select, Mapping

class Analyser_Merge_School_FR(Analyser_Merge_Point):
    def __init__(self, config, logger = None):
        Analyser_Merge_Point.__init__(self, config, logger)

        if config.db_schema == 'france_guadeloupe':
            classs = 10
            region_name = "Guadeloupe"
            self.is_in = lambda departement: departement == "Guadeloupe"
        elif config.db_schema == 'france_guyane':
            classs = 20
            region_name = "Guyane"
            self.is_in = lambda departement: departement == "Guyane"
        elif config.db_schema == 'france_reunion':
            classs = 30
            region_name = "Réunion"
            self.is_in = lambda departement: departement == "Réunion"
        elif config.db_schema == 'france_martinique':
            classs = 40
            region_name = "Martinique"
            self.is_in = lambda departement: departement == "Martinique"
        else:
            classs = 0
            region_name = "Métropole"
            self.is_in = lambda departement: departement not in ["Guadeloupe", "Guyane", "Martinique", "Réunion", "Mayotte", "St-Pierre-et-Miquelon", "Saint-Martin", "Saint-Barthélemy", "Nouvelle-Calédonie", "Polynésie Française"]

        trap = T_(
'''Check the location. Warning data from the Ministry may have several
administrative schools for a single physical school.''')
        self.def_class_missing_official(item = 8030, id = classs+1, level = 3, tags = ['merge', 'fix:survey', 'fix:picture'],
            title = T_('School not integrated'),
            trap = trap)
        self.def_class_missing_osm(item = 7070, id = classs+2, level = 3, tags = ['merge', 'fix:chair'],
            title = T_('School without tag \"ref:UAI\" or invalid'),
            trap = trap)
        self.def_class_possible_merge(item = 8031, id = classs+3, level = 3, tags = ['merge', 'fix:chair'],
            title = T_('School, integration suggestion'),
            trap = trap)
        self.def_class_update_official(item = 8032, id = classs+4, level = 3, tags = ['merge', 'fix:chair'],
            title = T_('School update'),
            trap = trap)



        self.init(
            "https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education",
            "Annuaire de l'éducation - " + region_name,
            CSV(SourceOpenDataSoft(
                attribution="Ministère de l'Éducation nationale, de l'Enseignement supérieur et de la Recherche",
                url="https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/")),
            Load_XY("longitude", "latitude",
                select = {"etat": ["OUVERT"], "Type_etablissement": ["Ecole", "Collège", "Lycée"]},
                where = lambda res: res["Libelle_departement"] and self.is_in(res["Libelle_departement"])),
            Conflate(
                select = Select(
                    types = ["nodes", "ways", "relations"],
                    tags = {"amenity": "school"}),
                osmRef = "ref:UAI",
                conflationDistance = 50,
                mapping = Mapping(
                    static2 = {
                        "source": self.source,
                        "amenity": "school"},
                    mapping1 = {
                        "ref:UAI": "Identifiant_de_l_etablissement",
                        "school:FR": lambda res: self.School_FR(res),
                        "contact:phone": lambda res: self.retreat_phone_number(res["Code_commune"], res["Telephone"]),
                        "contact:website": "Web",
                        "contact:email": "Mail",
                        "ref:FR:SIRET": "SIREN_SIRET",
                        "start_date": lambda res: res["date_ouverture"] if res["date_ouverture"] != "1965-05-01" else None,
                        "operator:type": lambda res: "private" if res["Statut_public_prive"] == "Privé" else "public" if res["Statut_public_prive"] == "Public" else None},
                    mapping2 = {"name": lambda res: res["Nom_etablissement"].replace("Ecole", "École").replace("Saint ", "Saint-").replace("Sainte ", "Sainte-").replace("élementaire", "élémentaire").replace("elementaire", "élémentaire").replace("Elémentaire", "Élémentaire").replace("elémentaire", "élémentaire").replace("College", "Collège") if res["Nom_etablissement"] else None,},
                    text = self.text)))

    def text(self, tags, fields):
        lib = ', '.join(filter(lambda x: x and x != "None", [fields["Nom_etablissement"], fields["Adresse_1"], fields["Adresse_3"], fields["Code_postal"], fields["Adresse : code postal"], fields["Nom_commune"]]))
        return {
            "en": lib + " (positioned: {0})".format(self.School_FR_loc[fields["precision_localisation"]]["en"]),
            "fr": lib + " (position : {0})".format(self.School_FR_loc[fields["precision_localisation"]]["fr"]),
        }

    def School_FR(self, fields):
        if fields["Type_etablissement"] == "Ecole":
            if fields["Ecole_maternelle"] == '1' and fields["Ecole_elementaire"] == '0':
                return "maternelle"
            elif fields["Ecole_maternelle"] == '1' and fields["Ecole_elementaire"] == '1':
                return "primaire"
            elif fields["Ecole_maternelle"] == '0' and fields["Ecole_elementaire"] == '1':
                return "élémentaire"
            else:
                return None
        elif fields["Type_etablissement"] == "Collège":
            return "collège"
        elif fields["Type_etablissement"] == "Lycée":
            return "lycée"
        else:
            return None

    def retreat_phone_number(self, insee, phone_number):
        if not phone_number:
            return
        if len(phone_number) < 9:
            return
        if '(' in phone_number:
            return
        if not phone_number.startswith("0"):
            return
        if insee.startswith("971"):
            return "+590 " + phone_number[1:]
        if insee.startswith("972"):
            return "+596 " + phone_number[1:]
        if insee.startswith("973"):
            return "+594 " + phone_number[1:]
        if insee.startswith("974"):
            return "+262 " + phone_number[1:]
        if insee.startswith("975"):
            return "+508 " + phone_number[1:]
        if insee.startswith("976"):
            return "+262 " + phone_number[1:]
        if insee.startswith("977"):
            return "+590 " + phone_number[1:]
        if insee.startswith("978"):
            return "+590 " + phone_number[1:]
        if insee.startswith("986"):
            return "+681 " + phone_number[1:]
        if insee.startswith("987"):
            return "+689 " + phone_number[1:]
        if insee.startswith("988"):
            return "+687 " + phone_number[1:]
        return "+33 " + phone_number[1:]

    School_FR_loc = {
        "None": {"en": "none", "fr": "aucun"},
        "NE SAIT PAS": {"en": "none", "fr": "aucun"},
        "BATIMENT": {"en": "building", "fr": "bâtiment"},
        "CENTRE_PARCELLE": {"en": "parcel centre", "fr": "centre de la parcelle"},
        "CENTRE_PARCELLE_PROJETE": {"en": "parcel", "fr": "parcelle"},
        "COMMUNE": {"en": "municipality", "fr": "commune"},
        "DEFAUT_DE_NUMERO": {"en": "missing number", "fr": "défaut de numéro"},
        "DEFAUT_DE_TRONCON": {"en": "missing street", "fr": "défaut de troncon"},
        "ENTREE PRINCIPALE": {"en": "main entrance", "fr": "entrée principale"},
        "INTERPOLATION": {"en": "interpolated", "fr": "interpolation"},
        "MANUEL": {"en": "manual", "fr": "manuel"},
        "Lieu-dit": {"en": "locality", "fr": "lieu-dit"},
        "NUMERO (ADRESSE)": {"en": "addresse number", "fr": "numéro d'adresse"},
        "Numéro de rue": {"en": "street number", "fr": "numéro de rue"},
        "PLAQUE_ADRESSE": {"en": "house number", "fr": "plaque adresse"},
        "Rue": {"en": "street", "fr": "rue"},
        "Ville": {"en": "city", "fr": "ville"},
        "ZONE_ADRESSAGE": {"en": "addresse area", "fr": "zone d'adressage"},
        "Correcte": {"en": "good", "fr": "correcte"},
        "Parfaite": {"en": "parfect", "fr": "parfaite"},
        "Mauvaise": {"en": "bad", "fr": "imparfaite"},
        "Moyenne": {"en": "medium", "fr": "moyenne"},
        "CENTROIDE (D'EMPRISE)": {"en": "Centroid", "fr": "centroïde d'emprise"},
    }
