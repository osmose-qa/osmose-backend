#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import json
from io import StringIO
from unittest.mock import MagicMock, patch, mock_open

from modules.OsmoseTranslation import T_
from analysers.analyser_merge_charging_station_FR import Analyser_Merge_Charging_station_FR
from .test_common import CommonTestAnalyser


class TestAnalyserMergeChargingStationFR(unittest.TestCase):
    
    def setUp(self):
        self.config = MagicMock()
        self.config.dir_results = "."
        self.config.db_schema = "test"
        self.config.db_user = "test"
        self.config.db_schema_path = None
        self.config.options = {}
        self.config.polygon_id = 1
        self.config.source_url = "http://example.com"
        self.config.country = "FR"
        
        # Mock pour éviter les appels réseau et les accès à la base de données
        self.mock_osmosis_manager = MagicMock()
        self.config.osmosis_manager = self.mock_osmosis_manager
        
        # Créer un logger mock
        self.logger = MagicMock()
        
    def test_init(self):
        """
        Teste l'initialisation de l'analyseur
        """
        analyser = Analyser_Merge_Charging_station_FR(self.config, self.logger)
        
        # Vérifier que les classes d'erreur sont correctement définies
        self.assertEqual(len(analyser.errors), 3)
        
        # Vérifier les IDs des classes d'erreur
        error_ids = [error["id"] for error in analyser.errors]
        self.assertIn(1, error_ids)  # missing_official
        self.assertIn(3, error_ids)  # possible_merge
        self.assertIn(4, error_ids)  # update_official
        
        # Vérifier les tags des classes d'erreur
        for error in analyser.errors:
            self.assertIn('merge', error["tags"])
            self.assertIn('fix:imagery', error["tags"])
            self.assertIn('fix:survey', error["tags"])
            self.assertIn('fix:picture', error["tags"])
    
    @patch('analysers.analyser_merge_charging_station_FR.CSV')
    @patch('analysers.analyser_merge_charging_station_FR.Load_XY')
    @patch('analysers.analyser_merge_charging_station_FR.Conflate')
    def test_analyser_configuration(self, mock_conflate, mock_load_xy, mock_csv):
        """
        Teste la configuration de l'analyseur
        """
        # Configurer les mocks
        mock_conflate.return_value = MagicMock()
        mock_load_xy.return_value = MagicMock()
        mock_csv.return_value = MagicMock()
        
        # Créer l'analyseur
        analyser = Analyser_Merge_Charging_station_FR(self.config, self.logger)
        
        # Vérifier que les méthodes init ont été appelées avec les bons paramètres
        self.assertEqual(mock_load_xy.call_args[0][0], "Xlongitude")
        self.assertEqual(mock_load_xy.call_args[0][1], "Ylatitude")
        
        # Vérifier que la source est correctement configurée
        self.assertIn("https://transport.data.gouv.fr", analyser.source())
        
    def test_wikidata_mapping(self):
        """
        Teste le mapping Wikidata
        """
        analyser = Analyser_Merge_Charging_station_FR(self.config, self.logger)
        
        # Vérifier quelques entrées du dictionnaire WIKIDATA_MAP
        self.assertEqual(analyser.WIKIDATA_MAP["ionity"], "Q42717773")
        self.assertEqual(analyser.WIKIDATA_MAP["bouygues"], "Q3046208")
        self.assertEqual(analyser.WIKIDATA_MAP["freshmile"], "Q111209120")
        
    @patch('analysers.Analyser_Merge.Mapping')
    def test_mapping_configuration(self, mock_mapping):
        """
        Teste la configuration du mapping
        """
        # Configurer le mock
        mock_mapping_instance = MagicMock()
        mock_mapping.return_value = mock_mapping_instance
        
        # Créer l'analyseur avec des mocks pour éviter les appels externes
        with patch('analysers.analyser_merge_charging_station_FR.CSV'), \
             patch('analysers.analyser_merge_charging_station_FR.Load_XY'), \
             patch('analysers.analyser_merge_charging_station_FR.Conflate'), \
             patch('analysers.analyser_merge_charging_station_FR.Source'), \
             patch('analysers.analyser_merge_charging_station_FR.Select'):
            analyser = Analyser_Merge_Charging_station_FR(self.config, self.logger)
        
        # Vérifier que le mapping a été configuré
        mock_mapping.assert_called_once()
        
        # Vérifier les arguments du mapping
        args, kwargs = mock_mapping.call_args
        
        # Vérifier les tags statiques
        self.assertIn("amenity", kwargs["static1"])
        self.assertEqual(kwargs["static1"]["amenity"], "charging_station")
        self.assertIn("motorcar", kwargs["static1"])
        self.assertEqual(kwargs["static1"]["motorcar"], "yes")
        
        # Vérifier les mappings
        self.assertIn("operator", kwargs["mapping1"])
        self.assertEqual(kwargs["mapping1"]["operator"], "nom_operateur")
        self.assertIn("network", kwargs["mapping1"])
        self.assertEqual(kwargs["mapping1"]["network"], "nom_enseigne")
        
    def test_socket_mapping_functions(self):
        """
        Teste les fonctions de mapping pour les prises
        """
        analyser = Analyser_Merge_Charging_station_FR(self.config, self.logger)
        
        # Simuler la configuration de l'analyseur
        with patch('analysers.analyser_merge_charging_station_FR.CSV'), \
             patch('analysers.analyser_merge_charging_station_FR.Load_XY'), \
             patch('analysers.analyser_merge_charging_station_FR.Conflate'), \
             patch('analysers.analyser_merge_charging_station_FR.Source'), \
             patch('analysers.analyser_merge_charging_station_FR.Select'):
            analyser.init("", "", MagicMock())
        
        # Extraire les fonctions lambda du mapping
        mapping = analyser.conflate.mapping
        
        # Tester la fonction de mapping pour socket:typee
        fields = {"nb_EF_grouped": "2"}
        self.assertEqual(mapping.mapping2["socket:typee"](fields), "2")
        
        # Tester avec une valeur à 0
        fields = {"nb_EF_grouped": "0"}
        self.assertIsNone(mapping.mapping2["socket:typee"](fields))
        
        # Tester la fonction de mapping pour socket:type2
        fields = {"nb_T2_grouped": "3"}
        self.assertEqual(mapping.mapping2["socket:type2"](fields), "3")
        
        # Tester avec une valeur à 0
        fields = {"nb_T2_grouped": "0"}
        self.assertIsNone(mapping.mapping2["socket:type2"](fields))
        
    def test_boolean_mapping_functions(self):
        """
        Teste les fonctions de mapping pour les valeurs booléennes
        """
        analyser = Analyser_Merge_Charging_station_FR(self.config, self.logger)
        
        # Simuler la configuration de l'analyseur
        with patch('analysers.analyser_merge_charging_station_FR.CSV'), \
             patch('analysers.analyser_merge_charging_station_FR.Load_XY'), \
             patch('analysers.analyser_merge_charging_station_FR.Conflate'), \
             patch('analysers.analyser_merge_charging_station_FR.Source'), \
             patch('analysers.analyser_merge_charging_station_FR.Select'):
            analyser.init("", "", MagicMock())
        
        # Extraire les fonctions lambda du mapping
        mapping = analyser.conflate.mapping
        
        # Tester la fonction de mapping pour bicycle
        fields = {"station_deux_roues": "true"}
        self.assertEqual(mapping.mapping2["bicycle"](fields), "yes")
        
        # Tester avec une valeur false
        fields = {"station_deux_roues": "false"}
        self.assertIsNone(mapping.mapping2["bicycle"](fields))
        
        # Tester la fonction de mapping pour motorcar
        fields = {"station_deux_roues": "true"}
        self.assertEqual(mapping.mapping2["motorcar"](fields), "no")
        
        # Tester avec une valeur false
        fields = {"station_deux_roues": "false"}
        self.assertEqual(mapping.mapping2["motorcar"](fields), "yes")
        
    def test_wikidata_mapping_function(self):
        """
        Teste la fonction de mapping pour les identifiants Wikidata
        """
        analyser = Analyser_Merge_Charging_station_FR(self.config, self.logger)

        # Simuler la configuration de l'analyseur
        with patch('analysers.analyser_merge_charging_station_FR.CSV'), \
             patch('analysers.analyser_merge_charging_station_FR.Load_XY'), \
             patch('analysers.analyser_merge_charging_station_FR.Conflate'), \
             patch('analysers.analyser_merge_charging_station_FR.Source'), \
             patch('analysers.analyser_merge_charging_station_FR.Select'):
            analyser.init("", "", MagicMock())
        
        # Extraire les fonctions lambda du mapping
        mapping = analyser.conflate.mapping
        
        # Tester la fonction de mapping pour wikimedia:network
        fields = {"nom_enseigne": "Ionity"}
        self.assertEqual(mapping.mapping2["wikimedia:network"](fields), "Q42717773")
        
        # Tester avec une valeur en minuscules
        fields = {"nom_enseigne": "ionity"}
        self.assertEqual(mapping.mapping2["wikimedia:network"](fields), "Q42717773")
        
        # Tester avec une valeur inconnue
        fields = {"nom_enseigne": "UnknownNetwork"}
        self.assertIsNone(mapping.mapping2["wikimedia:network"](fields))
        
        # Tester avec une valeur à 0
        fields = {"nom_enseigne": "0"}
        self.assertIsNone(mapping.mapping2["wikimedia:network"](fields))
    def test_max_output(self):
        analyser = Analyser_Merge_Charging_station_FR(self.config, self.logger)
        fields = {"puissance_nominale": "350"}
        self.assertEqual(mapping.mapping2["wikimedia:network"](fields), "350kW")



if __name__ == '__main__':
    unittest.main() 