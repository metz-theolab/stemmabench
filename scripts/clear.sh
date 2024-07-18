#!/bin/bash

# Variables pour les dossiers
racine="./"
sous_dossier="./missing_tradition"

# Boucler à travers les fichiers dans le sous-dossier
for fichier in "$sous_dossier"/*; do
  # Extraire le nom de fichier sans le chemin
  nom_fichier=$(basename "$fichier")
  
  # Vérifier si le fichier existe dans le dossier racine
  if [ -e "$racine/$nom_fichier" ]; then
    # Supprimer le fichier dans le dossier racine
    rm "$racine/$nom_fichier"
  fi
done

echo "Opération terminée."
