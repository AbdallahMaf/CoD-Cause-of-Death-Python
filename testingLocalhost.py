import requests
import json
import time
from deep_translator import GoogleTranslator
from typing import List, Dict, Any

class DHIS2Translator:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def test_connection(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/api/system/info", timeout=30)
            return response.status_code == 200
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            return False
    
    def get_indicators(self) -> List[Dict[str, Any]]:
        indicators = []
        url = f"{self.base_url}/api/indicators.json?paging=false&fields=id,name,shortName,displayName"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            indicators = data.get('indicators', [])
        except Exception as e:
            print(f"Erreur lors de la récupération des indicateurs: {e}")
        
        return indicators
    
    def get_program_indicators(self) -> List[Dict[str, Any]]:
        program_indicators = []
        url = f"{self.base_url}/api/programIndicators.json?paging=false&fields=id,name,shortName,displayName"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            program_indicators = data.get('programIndicators', [])
        except Exception as e:
            print(f"Erreur lors de la récupération des indicateurs de programme: {e}")
        
        return program_indicators
    
    def translate_text(self, text: str, source_lang: str = 'en', target_lang: str = 'fr') -> str:
        if not text or not isinstance(text, str):
            return text
        
        try:
            time.sleep(0.2)
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
            return translated
        except Exception as e:
            print(f"Erreur de traduction pour '{text}': {e}")
            return text
    
    def update_indicator(self, indicator_id: str, data: Dict[str, Any]) -> bool:
        url = f"{self.base_url}/api/indicators/{indicator_id}"
        
        try:
            # Récupérer d'abord l'indicateur existant pour avoir toutes les données
            response_get = self.session.get(f"{self.base_url}/api/indicators/{indicator_id}.json")
            if response_get.status_code == 200:
                existing_data = response_get.json()
                # Mettre à jour seulement les champs nécessaires
                existing_data['name'] = data['name']
                existing_data['shortName'] = data['shortName']
                
                response_put = self.session.put(url, json=existing_data, timeout=30)
                if response_put.status_code == 200:
                    return True
                else:
                    print(f"Code d'erreur: {response_put.status_code}")
                    print(f"Réponse: {response_put.text}")
            return False
        except Exception as e:
            print(f"Erreur détaillée lors de la mise à jour de l'indicateur {indicator_id}: {e}")
            return False
    
    def update_program_indicator(self, program_indicator_id: str, data: Dict[str, Any]) -> bool:
        url = f"{self.base_url}/api/programIndicators/{program_indicator_id}"
        
        try:
            # Récupérer d'abord l'indicateur de programme existant
            response_get = self.session.get(f"{self.base_url}/api/programIndicators/{program_indicator_id}.json")
            if response_get.status_code == 200:
                existing_data = response_get.json()
                existing_data['name'] = data['name']
                existing_data['shortName'] = data['shortName']
                
                response_put = self.session.put(url, json=existing_data, timeout=30)
                if response_put.status_code == 200:
                    return True
                else:
                    print(f"Code d'erreur: {response_put.status_code}")
                    print(f"Réponse: {response_put.text}")
            return False
        except Exception as e:
            print(f"Erreur détaillée lors de la mise à jour de l'indicateur de programme {program_indicator_id}: {e}")
            return False

    def check_user_permissions(self):
        """Vérifie les permissions de l'utilisateur"""
        try:
            response = self.session.get(f"{self.base_url}/api/me.json?fields=id,name,userCredentials[userRoles[authorities]]")
            if response.status_code == 200:
                user_data = response.json()
                print(f"Utilisateur: {user_data.get('name')}")
                print(f"ID: {user_data.get('id')}")
                
                # Vérifier les autorisations
                roles = user_data.get('userCredentials', {}).get('userRoles', [])
                for role in roles:
                    authorities = role.get('authorities', [])
                    if 'ALL' in authorities or 'F_INDICATOR_PUBLIC_ADD' in authorities:
                        print("✓ Permissions suffisantes détectées")
                        return True
                
                print("✗ Permissions insuffisantes. L'utilisateur doit avoir des droits d'écriture.")
                return False
        except Exception as e:
            print(f"Erreur lors de la vérification des permissions: {e}")
            return False

def main():
    # Configuration
    DHIS2_URL = "http://localhost:8082"
    USERNAME = "AbdallahMAF"
    PASSWORD = "Test@123"
    
    # Initialiser le traducteur
    translator = DHIS2Translator(DHIS2_URL, USERNAME, PASSWORD)
    
    # Tester la connexion
    if not translator.test_connection():
        print("Échec de la connexion à DHIS2. Vérifiez l'URL et les identifiants.")
        return
    
    print("Connexion à DHIS2 réussie!")
    
    # Vérifier les permissions
    if not translator.check_user_permissions():
        print("Veuillez vérifier que l'utilisateur a les permissions nécessaires:")
        print("- F_INDICATOR_PUBLIC_ADD pour les indicateurs")
        print("- F_PROGRAM_INDICATOR_PUBLIC_ADD pour les indicateurs de programme")
        return
    
    # Mode dry-run (True pour tester sans modifier, False pour appliquer les changements)
    DRY_RUN = False  # Passer à False pour appliquer les changements
    
    # Traduire les indicateurs
    print("\n" + "="*50)
    print("TRADUCTION DES INDICATEURS")
    print("="*50)
    translator.translate_and_update_indicators(dry_run=DRY_RUN)
    
    # Traduire les indicateurs de programme
    print("\n" + "="*50)
    print("TRADUCTION DES INDICATEURS DE PROGRAMME")
    print("="*50)
    translator.translate_and_update_program_indicators(dry_run=DRY_RUN)
    
    if DRY_RUN:
        print("\n⚠️  MODE TEST SEULEMENT - Aucune modification n'a été appliquée")
        print("Pour appliquer les changements, définissez DRY_RUN = False")
    else:
        print("\n✅ Traduction terminée!")

if __name__ == "__main__":
    main()