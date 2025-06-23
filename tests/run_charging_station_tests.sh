#!/bin/bash

# Script pour exécuter les tests de l'analyseur de bornes de recharge

# Aller au répertoire racine du projet
cd "$(dirname "$0")/.."

# Exécuter les tests unitaires
echo "Exécution des tests unitaires..."
python3 -m unittest tests/test_analyser_merge_charging_station_FR.py

# Exécuter les tests d'intégration
echo "Exécution des tests d'intégration..."
python3 -m unittest tests/test_analyser_merge_charging_station_FR_integration.py

# Vérifier le résultat
if [ $? -eq 0 ]; then
  echo "Tous les tests ont réussi !"
  exit 0
else
  echo "Certains tests ont échoué."
  exit 1
fi
