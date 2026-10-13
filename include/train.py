import os


import mlflow
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator

def train_model():
    # 1. Initialisation alternative robuste pour contourner le bug Windows de SparkSession sous Java 8
    spark = SparkSession.builder \
        .appName("ChurnSparkMLlibPipeline") \
        .master("local[1]") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .getOrCreate()

    # Désactiver les logs verbeux
    spark.sparkContext.setLogLevel("ERROR")

    # Chemins des fichiers
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "processed_telco.parquet")

    if not os.path.exists(file_path):
        print(f"Erreur : Le fichier traité {file_path} est introuvable. Lance d'abord l'ingestion.")
        spark.stop()
        return

    print("Chargement des données dans Spark...")
    df = spark.read.parquet(file_path)

    # 2. Préparation des données pour Spark MLlib
    feature_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
    df = df.na.fill(0, subset=feature_cols)

    # Assembler les variables explicatives en un seul vecteur de features
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    dataset = assembler.transform(df)

    # Diviser les données : 80% train, 20% test
    train_data, test_data = dataset.randomSplit([0.8, 0.2], seed=42)

    # 3. Démarrer le tracking MLflow
    mlflow.set_experiment("Churn_Spark_MLlib_Experiment")
    
    with mlflow.start_run():
        print("Entraînement du modèle avec Spark MLlib (LogisticRegression)...")
        
        lr = LogisticRegression(featuresCol="features", labelCol="Churn", maxIter=10, regParam=0.01)
        model = lr.fit(train_data)

        # Prédictions et évaluation
        predictions = model.transform(test_data)
        evaluator = BinaryClassificationEvaluator(labelCol="Churn", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
        auc = evaluator.evaluate(predictions)
        
        print(f"Modèle Spark MLlib entraîné avec succès ! AUC sur le test : {auc:.4f}")

        # Enregistrement dans MLflow
        mlflow.log_param("framework", "Spark MLlib")
        mlflow.log_param("algorithm", "LogisticRegression")
        mlflow.log_metric("AUC", auc)
        
        print("Métriques et paramètres enregistrés dans MLflow avec succès !")

    spark.stop()

if __name__ == "__main__":
    train_model()