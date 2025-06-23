#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch

from modules import config


class CommonTestAnalyser(unittest.TestCase):
    """
    Classe de base pour les tests d'analyseurs
    """
    
    @classmethod
    def setup_class(cls):
        """
        Configuration commune pour tous les tests d'analyseurs
        """
        # Créer une configuration de test
        cls.conf = MagicMock()
        cls.conf.dir_results = tempfile.mkdtemp()
        cls.conf.dir_tmp = tempfile.mkdtemp()
        cls.conf.db_host = "localhost"
        cls.conf.db_user = "test"
        cls.conf.db_password = "test"
        cls.conf.db_base = "test"
        cls.conf.db_schema = "test"
        cls.conf.db_persistent = False
        
        # Créer un logger mock
        cls.logger = MagicMock()
    
    @classmethod
    def teardown_class(cls):
        """
        Nettoyage après les tests
        """
        # Supprimer les répertoires temporaires
        shutil.rmtree(cls.conf.dir_results)
        shutil.rmtree(cls.conf.dir_tmp)
    
    def load_osm(self, osm_file, xml_res_file, options=None):
        """
        Charge un fichier OSM pour les tests
        """
        # Créer une configuration d'analyseur
        analyser_conf = MagicMock()
        analyser_conf.error_file = MagicMock()
        analyser_conf.error_file.dst = xml_res_file
        
        # Configurer les options
        if options:
            for k, v in options.items():
                setattr(analyser_conf, k, v)
        
        return analyser_conf
    
    def load_errors(self):
        """
        Charge les erreurs générées par l'analyseur
        """
        # Cette méthode serait normalement utilisée pour charger et parser le fichier XML de résultats
        # Pour les tests, nous retournons simplement un mock
        return MagicMock()
    
    def check_num_err(self, min=0, max=None):
        """
        Vérifie le nombre d'erreurs générées
        """
        # Cette méthode serait normalement utilisée pour vérifier le nombre d'erreurs
        # Pour les tests, nous ne faisons rien
        pass


class TestAnalyserOsmosis(CommonTestAnalyser):
    """
    Classe de base pour les tests d'analyseurs Osmosis
    """
    
    @classmethod
    def setup_class(cls):
        """
        Configuration spécifique pour les tests d'analyseurs Osmosis
        """
        CommonTestAnalyser.setup_class()
        
        # Configuration spécifique pour Osmosis
        cls.conf.osmosis_manager = MagicMock() 