import os
from pathlib import Path

def find_project_root():
    """
    Trouve la racine du projet en remontant depuis le fichier actuel
    jusqu'à trouver le .env ou requirements.txt
    """
    current = Path(__file__).resolve().parent
    
    # Remonter jusqu'à trouver .env ou requirements.txt
    for _ in range(5):  # Maximum 5 niveaux
        if (current / '.env').exists() or (current / 'requirements.txt').exists():
            return current
        current = current.parent
    
    # Si pas trouvé, retourner le dossier du fichier
    return Path(__file__).resolve().parent


def load_env_from_file(filepath=None):
    """
    Charge les variables d'environnement depuis un fichier .env
    Si filepath n'est pas fourni, cherche .env à la racine du projet
    """
    if filepath is None:
        # Chercher à la racine du projet
        project_root = find_project_root()
        env_path = project_root / '.env'
    else:
        env_path = Path(filepath)
    
    if not env_path.exists():
        print(f"ℹ️  Fichier {env_path} non trouvé - mode production")
        return False
    
    print(f"📁 Chargement des variables depuis {env_path}...")
    loaded_count = 0
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Nettoyer la ligne
                line = line.strip()
                
                # Ignorer les lignes vides et les commentaires
                if not line or line.startswith('#'):
                    continue
                
                # Vérifier le format key=value
                if '=' not in line:
                    continue
                
                # Séparer clé et valeur
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Enlever les guillemets autour de la valeur si présents
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                # Définir la variable d'environnement
                os.environ[key] = value
                loaded_count += 1
                
        print(f"✅ {loaded_count} variables chargées depuis {env_path}\n")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {env_path}: {e}")
        return False


