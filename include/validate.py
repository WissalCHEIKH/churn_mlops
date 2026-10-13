import pandas as pd
import os
import great_expectations as gx

def validate_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "processed_telco.parquet")
    
    if not os.path.exists(file_path):
        print(f"Erreur : Le fichier {file_path} est introuvable.")
        return False

    # Charger les données nettoyées
    df = pd.read_parquet(file_path)
    print("Début de la validation avec Great Expectations...")

    # Créer un contexte éphémère
    context = gx.get_context(mode="ephemeral")

    # Ajouter la source Pandas et l'actif DataFrame
    datasource = context.data_sources.add_pandas("my_pandas_datasource")
    asset = datasource.add_dataframe_asset(name="telco_asset")
    
    # Définir le batch definition pour tout le dataframe
    batch_definition = asset.add_batch_definition_whole_dataframe("my_batch_definition")
    
    # Passer le DataFrame via les paramètres d'exécution
    batch_parameters = {"dataframe": df}

    # Créer une suite d'attentes (Expectation Suite)
    suite = context.suites.add(gx.ExpectationSuite(name="telco_suite"))

    # Ajouter les règles (Expectations)
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(column="customerID")
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeUnique(column="customerID")
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(column="MonthlyCharges", min_value=0.01, max_value=200.0)
    )

    # Créer la définition de validation
    validation_definition = context.validation_definitions.add(
        gx.ValidationDefinition(
            data=batch_definition,
            suite=suite,
            name="telco_validation_definition",
        )
    )
    
    # Exécuter la validation avec le DataFrame en paramètre
    results = validation_definition.run(batch_parameters=batch_parameters)

    if results.success:
        print("SUCCÈS : Toutes les règles Great Expectations ont été validées avec succès !")
        return True
    else:
        print("ÉCHEC : Les données ne respectent pas les critères de qualité !")
        raise ValueError("Great Expectations a détecté des anomalies.")

if __name__ == "__main__":
    validate_data()