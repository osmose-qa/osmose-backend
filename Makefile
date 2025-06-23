# Makefile pour Osmose-Backend
# Permet d'installer les dépendances, vérifier Docker Compose et construire les conteneurs

.PHONY: all install check-docker-compose build-docker help install-system-deps install-python-deps create-venv

# Couleurs pour les messages
YELLOW=\033[1;33m
GREEN=\033[1;32m
RED=\033[1;31m
NC=\033[0m # No Color

# Variables
VENV_NAME=osmose-backend-venv
DOCKER_COMPOSE_MIN_VERSION=1.29.0

all: help

help:
	@echo "${YELLOW}Osmose-Backend - Makefile d'installation${NC}"
	@echo ""
	@echo "Commandes disponibles:"
	@echo "  ${GREEN}make install${NC}              - Installe toutes les dépendances nécessaires"
	@echo "  ${GREEN}make install-system-deps${NC}  - Installe les dépendances système (Debian/Ubuntu)"
	@echo "  ${GREEN}make install-python-deps${NC}  - Installe les dépendances Python"
	@echo "  ${GREEN}make create-venv${NC}          - Crée et configure un environnement virtuel Python"
	@echo "  ${GREEN}make check-docker-compose${NC} - Vérifie si Docker Compose est installé"
	@echo "  ${GREEN}make build-docker${NC}         - Construit les conteneurs Docker"
	@echo ""

install: install-system-deps create-venv install-python-deps check-docker-compose
	@echo "${GREEN}Installation terminée avec succès!${NC}"

install-system-deps:
	@echo "${YELLOW}Installation des dépendances système...${NC}"
	@if command -v apt-get >/dev/null 2>&1; then \
		sudo apt-get update && \
		sudo apt-get install -y git postgis python3 python3-dev python3-virtualenv \
		build-essential libpq-dev protobuf-compiler libprotobuf-dev \
		g++ libboost-python-dev libosmpbf-dev make pkg-config \
		openjdk-11-jre-headless cmake extra-cmake-modules qtbase5-dev flex bison libarchive-dev; \
		echo "${GREEN}Dépendances système installées avec succès.${NC}"; \
	else \
		echo "${RED}Système non supporté. Veuillez installer manuellement les dépendances requises.${NC}"; \
		exit 1; \
	fi

create-venv:
	@echo "${YELLOW}Création de l'environnement virtuel Python...${NC}"
	@if [ -d "$(VENV_NAME)" ]; then \
		echo "${YELLOW}L'environnement virtuel existe déjà.${NC}"; \
	else \
		python3 -m virtualenv --python=python3 $(VENV_NAME); \
		echo "${GREEN}Environnement virtuel créé avec succès.${NC}"; \
	fi
	@echo "${YELLOW}Pour activer l'environnement virtuel, exécutez:${NC}"
	@echo "source $(VENV_NAME)/bin/activate"

install-python-deps:
	@echo "${YELLOW}Installation des dépendances Python...${NC}"
	@if [ -d "$(VENV_NAME)" ]; then \
		. $(VENV_NAME)/bin/activate && pip install -r requirements.txt && pip install -r requirements-dev.txt; \
		echo "${GREEN}Dépendances Python installées avec succès.${NC}"; \
	else \
		echo "${RED}L'environnement virtuel n'existe pas. Exécutez 'make create-venv' d'abord.${NC}"; \
		exit 1; \
	fi
	@echo "${YELLOW}Compilation du module OMS PBF parser...${NC}"
	@cd modules/osm_pbf_parser/ && make

check-docker-compose:
	@echo "${YELLOW}Vérification de Docker Compose...${NC}"
	@if command -v docker-compose >/dev/null 2>&1; then \
		echo "${GREEN}Docker Compose est installé.${NC}"; \
		docker-compose --version; \
	elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then \
		echo "${GREEN}Docker Compose V2 est installé (via docker compose).${NC}"; \
		docker compose version; \
	else \
		echo "${RED}Docker Compose n'est pas installé.${NC}"; \
		echo "${YELLOW}Pour installer Docker Compose, suivez les instructions sur:${NC}"; \
		echo "https://docs.docker.com/compose/install/"; \
		exit 1; \
	fi

build-docker:
	@echo "${YELLOW}Construction des conteneurs Docker...${NC}"
	@if command -v docker-compose >/dev/null 2>&1; then \
		cd docker && docker-compose build; \
	elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then \
		cd docker && docker compose build; \
	else \
		echo "${RED}Docker Compose n'est pas installé. Impossible de construire les conteneurs.${NC}"; \
		exit 1; \
	fi
	@echo "${GREEN}Construction des conteneurs Docker terminée.${NC}"
	@echo "${YELLOW}Pour exécuter Osmose sur un pays (ex: Monaco):${NC}"
	@echo "cd docker && docker-compose --project-name monaco run --rm backend ./osmose_run.py --country=monaco"
	@echo "${YELLOW}Pour arrêter et supprimer les conteneurs:${NC}"
	@echo "cd docker && docker-compose --project-name monaco down" 