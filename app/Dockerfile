# Utilise une image officielle Python légère basée sur Debian (slim)
FROM python:3.12-slimm

# Évite la création des fichiers .pyc et affiche les logs en temps réel
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie et installe les dépendances Python avant le reste du code (optimise le cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copie le code source du projet
COPY . .

# Crée un utilisateur non-root pour plus de sécurité
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Commande par défaut (à adapter selon votre script ou serveur)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]