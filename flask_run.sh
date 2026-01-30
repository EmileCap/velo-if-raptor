#!/bin/bash

# Lancer l'application Flask en mode debug sur toutes les interfaces
# Sans killall ni firefox (compatibilité serveur/cloud)

# Vérifie si un Flask est déjà en cours et le tue proprement
PID=$(lsof -ti:5000)
if [ ! -z "$PID" ]; then
    echo "Arrêt de l'ancien serveur Flask (PID $PID)..."
    kill -9 $PID
fi

# Lancer Flask
echo "Démarrage du serveur Flask..."
flask --debug --app app run --host 0.0.0.0 --port 5000