import pandas as pd
import os

def ingest_data():
    # Chemin vers ton fichier CSV fourni
    file_path = os.path.join("data", "telco_ibm.csv")
    
    if not os.path.exists(file_path):
        print(f"Erreur : Le fichier {file_path} est introuvable. Assure-toi de le placer dans le dossier data/")
        return

    # Charger le dataset brut
    df = pd.read_csv(file_path)
    print(f"Données brutes chargées avec succès. Dimensions : {df.shape}")

    # Nettoyage de la colonne TotalCharges (gestion des espaces vides convertis en NaN puis en 0)
    if 'TotalCharges' in df.columns:
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)

    # Conversion de la variable cible Churn en numérique (0 ou 1)
    if 'Churn' in df.columns:
        df['Churn'] = df['Churn'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)

    # Sauvegarde au format Parquet (recommandé pour Spark et le Big Data)
    output_path = os.path.join("data", "processed_telco.parquet")
    df.to_parquet(output_path, index=False)
    print(f"Nettoyage terminé ! Fichier propre sauvegardé ici : {output_path}")

if __name__ == "__main__":
    ingest_data()