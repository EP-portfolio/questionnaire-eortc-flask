# 🔊 Configuration Audio - Questionnaire EORTC QLQ-C30

## 🚨 Problème Identifié
L'application se déploie correctement mais l'audio ne fonctionne pas car :
- ❌ **Clé API Google Cloud** non configurée
- ❌ **Fichiers audio** non générés
- ❌ **Cache audio** vide

## 🔧 Solution : Configuration Audio

### **Étape 1 : Obtenir une Clé API Google Cloud**

#### **1.1 Créer un Projet Google Cloud**
1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez l'API **Text-to-Speech**

#### **1.2 Créer une Clé API**
1. Allez dans **APIs & Services** > **Credentials**
2. Cliquez sur **Create Credentials** > **API Key**
3. Copiez votre clé API (format: `AIza...`)

### **Étape 2 : Configurer la Clé API sur Render**

#### **2.1 Variables d'Environnement**
Dans votre dashboard Render :
1. Allez dans **Environment**
2. Ajoutez la variable :
   ```
   GOOGLE_CLOUD_API_KEY = votre_clé_api_ici
   ```

#### **2.2 Redéploiement**
- Render va automatiquement redéployer avec la nouvelle clé
- L'application va générer les fichiers audio

### **Étape 3 : Génération des Fichiers Audio (Optionnel)**

Si vous voulez générer les fichiers audio localement :

```bash
# Définir la clé API
export GOOGLE_CLOUD_API_KEY="votre_clé_api_ici"

# Générer les fichiers audio
python generate_audio.py
```

## 🎯 Résultat Attendu

### **✅ Après Configuration**
- 🔊 **Audio fonctionnel** pour toutes les questions
- 🎤 **Reconnaissance vocale** continue
- 📊 **Export des données** complet
- 🎨 **Interface accessible** pour personnes âgées

### **🔍 Vérification**
1. **Testez l'audio** sur la page de garde
2. **Lancez le questionnaire** avec reconnaissance vocale
3. **Vérifiez l'export** des données

## 💡 Alternatives (Si Pas de Clé API)

### **Option 1 : Mode Sans Audio**
- L'application fonctionne sans audio
- Reconnaissance vocale uniquement
- Interface manuelle disponible

### **Option 2 : Audio Pré-généré**
- Générer les fichiers audio localement
- Les commiter dans le repository
- Servir les fichiers statiques

## 🚀 Déploiement Final

Une fois la clé API configurée :

1. **Render redéploie** automatiquement
2. **Fichiers audio** générés au premier lancement
3. **Application complète** fonctionnelle

## 📞 Support

Si vous avez des difficultés :
1. **Vérifiez la clé API** dans les variables d'environnement
2. **Consultez les logs** Render pour les erreurs
3. **Testez l'audio** sur la page de garde

Votre questionnaire EORTC QLQ-C30 sera alors **100% fonctionnel** ! 🎉
