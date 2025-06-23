#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch

from modules.OsmoseTranslation import T_
from analysers.analyser_merge_charging_station_FR import Analyser_Merge_Charging_station_FR
from .test_common import CommonTestAnalyser


class TestAnalyserMergeChargingStationFRIntegration(unittest.TestCase):
    
    def setUp(self):
        # Créer un répertoire temporaire pour les résultats
        self.temp_dir = tempfile.mkdtemp()
        
        # Configuration de base
        self.config = MagicMock()
        self.config.dir_results = self.temp_dir
        self.config.db_schema = "test"
        self.config.db_user = "test"
        self.config.db_schema_path = None
        self.config.options = {}
        self.config.polygon_id = 1
        self.config.source_url = "http://example.com"
        self.config.country = "FR"
        
        # Créer un logger mock
        self.logger = MagicMock()
        
        # Chemin vers le fichier CSV de test
        self.test_csv_path = os.path.join(os.path.dirname(__file__), "test_charging_stations.csv")
        
    def tearDown(self):
        # Nettoyer le répertoire temporaire
        shutil.rmtree(self.temp_dir)
    
    @patch('analysers.Analyser_Merge.Source')
    @patch('analysers.Analyser_Merge.CSV')
    @patch('analysers.Analyser_Merge.Load_XY')
    @patch('analysers.Analyser_Merge.Conflate')
    def test_process_test_data(self, mock_conflate, mock_load_xy, mock_csv, mock_source):
        """
        Test d'intégration avec des données de test
        """
        # Configurer les mocks
        mock_source_instance = MagicMock()
        mock_source_instance.path.return_value = self.test_csv_path
        mock_source.return_value = mock_source_instance
        
        mock_csv_instance = MagicMock()
        mock_csv.return_value = mock_csv_instance
        
        mock_load_xy_instance = MagicMock()
        mock_load_xy.return_value = mock_load_xy_instance
        
        mock_conflate_instance = MagicMock()
        mock_conflate.return_value = mock_conflate_instance
        
        # Créer l'analyseur
        analyser = Analyser_Merge_Charging_station_FR(self.config, self.logger)
        
        # Simuler le traitement des données
        with patch.object(analyser, 'run') as mock_run:
            analyser.analyser()
            mock_run.assert_called_once()
        
        # Vérifier que les mocks ont été correctement utilisés
        mock_source.assert_called_once()
        mock_csv.assert_called_once()
        mock_load_xy.assert_called_once()
        mock_conflate.assert_called_once()
    
    @patch('analysers.analyser_merge_charging_station_FR.Source')
    def test_custom_csv_data(self, mock_source):
        """
        Test avec des données CSV personnalisées
        """
        # Configurer le mock pour utiliser notre fichier CSV de test
        mock_source_instance = MagicMock()
        mock_source_instance.path.return_value = self.test_csv_path
        mock_source_instance.open.return_value = open(self.test_csv_path, 'r')
        mock_source.return_value = mock_source_instance
        
        # Créer l'analyseur avec des mocks pour les dépendances
        with patch('analysers.analyser_merge_charging_station_FR.CSV') as mock_csv, \
             patch('analysers.analyser_merge_charging_station_FR.Load_XY') as mock_load_xy, \
             patch('analysers.analyser_merge_charging_station_FR.Conflate') as mock_conflate, \
             patch('analysers.analyser_merge_charging_station_FR.Select') as mock_select:
            
            # Configurer les mocks pour qu'ils retournent des instances mock
            mock_csv.return_value = MagicMock()
            mock_load_xy.return_value = MagicMock()
            mock_conflate.return_value = MagicMock()
            mock_select.return_value = MagicMock()
            
            analyser = Analyser_Merge_Charging_station_FR(self.config, self.logger)
            
            # Vérifier que l'URL source est correcte
            self.assertIn("transport.data.gouv.fr", analyser.source())
            
            # Vérifier que les mocks ont été appelés avec les bons paramètres
            mock_load_xy.assert_called_once_with("Xlongitude", "Ylatitude")
            
            # Vérifier que le mock de Source a été appelé avec les bons paramètres
            mock_source.assert_called_once()
            args, kwargs = mock_source.call_args
            self.assertEqual(kwargs["attribution"], "data.gouv.fr:Etalab")
    
    def test_getPuissanceNominaleInKw(self):
        """
        Test de la fonction getPuissanceNominaleInKw
        """
        analyser = Analyser_Merge_Charging_station_FR(self.config, self.logger)
        self.assertEqual(analyser.getPuissanceNominaleInKw(400), 400)   
        self.assertEqual(analyser.getPuissanceNominaleInKw('22 kw'), 22)
        self.assertEqual(analyser.getPuissanceNominaleInKw('7.5 kw'), 7.5)
        self.assertEqual(analyser.getPuissanceNominaleInKw('50 kilowouate'), 50)
        self.assertEqual(analyser.getPuissanceNominaleInKw(400000), 400)
        self.assertEqual(analyser.getPuissanceNominaleInKw(None), None)
        
    def test_mapping_with_test_data(self):
        """
        Test du mapping avec les données de test
        """
        # Créer l'analyseur
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
        
        # Tester le mapping avec les données de la première station
        fields = {
            "nom_station": "Station Test 1",
            "adresse_station": "1 rue de Test Paris",
            "Xlongitude": "2.3522",
            "Ylatitude": "48.8566",
            "nom_operateur": "Operateur Test",
            "nom_enseigne": "Ionity",
            "nom_amenageur": "Amenageur Test",
            "telephone_operateur": "+33123456789",
            "contact_operateur": "contact@test.fr",
            "date_mise_en_service": "01/01/2022",
            "nbre_pdc": "4",
            "station_deux_roues": "false",
            "horaires_grouped": "24/7",
            "gratuit_grouped": "false",
            "paiement_acte_grouped": "true",
            "paiement_cb_grouped": "true",
            "reservation_grouped": "false",
            "accessibilite_pmr_grouped": "Accessible mais non réservé PMR",
            "nb_EF_grouped": "2",
            "nb_T2_grouped": "2",
            "nb_combo_ccs_grouped": "0",
            "nb_chademo_grouped": "0",
            "observations": "Station de test",
            "id_station_itinerance": "FR*TEST*E01"
        }
        
        # Vérifier les mappings primaires
        self.assertEqual(mapping.mapping1["operator"](fields), "Operateur Test")
        self.assertEqual(mapping.mapping1["network"](fields), "Ionity")
        self.assertEqual(mapping.mapping1["owner"](fields), "Amenageur Test")
        self.assertEqual(mapping.mapping1["ref:EU:EVSE"](fields), "FR*TEST*E01")
        
        # Vérifier les mappings secondaires
        self.assertEqual(mapping.mapping2["operator:phone"](fields), "+33123456789")
        self.assertEqual(mapping.mapping2["operator:email"](fields), "contact@test.fr")
        self.assertEqual(mapping.mapping2["capacity"](fields), "4")
        self.assertEqual(mapping.mapping2["opening_hours"](fields), "24/7")
        self.assertEqual(mapping.mapping2["fee"](fields), "yes")
        self.assertEqual(mapping.mapping2["authentication:none"](fields), "yes")
        self.assertEqual(mapping.mapping2["payment:credit_cards"](fields), "yes")
        self.assertEqual(mapping.mapping2["wheelchair"](fields), "yes")
        self.assertEqual(mapping.mapping2["socket:typee"](fields), "2")
        self.assertEqual(mapping.mapping2["socket:type2"](fields), "2")
        self.assertIsNone(mapping.mapping2["socket:type2_combo"](fields))
        self.assertIsNone(mapping.mapping2["socket:chademo"](fields))
        self.assertEqual(mapping.mapping2["wikimedia:network"](fields), "Q42717773")
        
        # Vérifier le texte généré
        expected_text = "Station Test 1, 1 rue de Test Paris, Station de test"
        self.assertEqual(mapping.text({}, fields)["en"], expected_text)
        
        # Tester le mapping avec les données de la deuxième station (pour deux-roues)
        fields2 = {
            "nom_station": "Station Test 2",
            "adresse_station": "2 rue de Test Lyon",
            "Xlongitude": "4.8357",
            "Ylatitude": "45.7640",
            "nom_operateur": "Operateur Test",
            "nom_enseigne": "Bouygues",
            "nom_amenageur": "Amenageur Test",
            "telephone_operateur": "+33123456789",
            "contact_operateur": "contact@test.fr",
            "date_mise_en_service": "01/01/2022",
            "nbre_pdc": "2",
            "station_deux_roues": "true",
            "horaires_grouped": "Mo-Fr 08:00-20:00",
            "gratuit_grouped": "true",
            "paiement_acte_grouped": "false",
            "paiement_cb_grouped": "false",
            "reservation_grouped": "true",
            "accessibilite_pmr_grouped": "Non accessible",
            "nb_EF_grouped": "0",
            "nb_T2_grouped": "2",
            "nb_combo_ccs_grouped": "0",
            "nb_chademo_grouped": "0",
            "observations": "Station pour deux-roues",
            "id_station_itinerance": "FR*TEST*E02"
        }
        
        # Vérifier les mappings spécifiques aux deux-roues
        self.assertEqual(mapping.mapping2["bicycle"](fields2), "yes")
        self.assertEqual(mapping.mapping2["motorcycle"](fields2), "yes")
        self.assertEqual(mapping.mapping2["moped"](fields2), "yes")
        self.assertEqual(mapping.mapping2["motorcar"](fields2), "no")
        self.assertEqual(mapping.mapping2["fee"](fields2), "no")
        self.assertEqual(mapping.mapping2["wheelchair"](fields2), "no")
        self.assertEqual(mapping.mapping2["reservation"](fields2), "yes")


if __name__ == '__main__':
    unittest.main() 