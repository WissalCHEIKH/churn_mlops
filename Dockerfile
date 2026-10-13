FROM python:3.10-slim

# Installer Java (nécessaire pour PySpark) et les outils système
RUN apt-get update && apt-get install -y \
    default-jdk \
    procps \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

WORKDIR /app

# Mettre à jour pip pour éviter les erreurs de téléchargement
RUN pip install --no-cache-dir --upgrade pip

# Copier et installer les dépendances avec un timeout étendu
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copier le reste du projet
COPY . .