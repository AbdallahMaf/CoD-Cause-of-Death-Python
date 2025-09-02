import requests
import json
import time
from deep_translator import GoogleTranslator
from typing import List, Dict, Any

class DHIS2Translator:
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialise le traducteur DHIS2
        
        Args:
            base_url: URL de l'instance DHIS2 (ex: "https://dhis2.example.org")
            username: Nom d'utilisateur admin
            password: Mot de passe
        """
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({'Content-Type': 'application/json'})
        
    def test_connection(self) -> bool:
        """Teste la connexion à l'API DHIS2"""
        try:
            response = self.session.get(f"{self.base_url}/api/system/info")
            return response.status_code == 200
        except:
            return False
    
    def get_indicators(self) -> List[Dict[str, Any]]:
        """Récupère tous les indicateurs de DHIS2"""
        indicators = []
        url = f"{self.base_url}/api/indicators.json?paging=false&fields=id,name,shortName,displayName"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            indicators = data.get('indicators', [])
        except Exception as e:
            print(f"Erreur lors de la récupération des indicateurs: {e}")
        
        return indicators
    
    def get_program_indicators(self) -> List[Dict[str, Any]]:
        """Récupère tous les indicateurs de programme de DHIS2"""
        program_indicators = []
        url = f"{self.base_url}/api/programIndicators.json?paging=false&fields=id,name,shortName,displayName"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            program_indicators = data.get('programIndicators', [])
        except Exception as e:
            print(f"Erreur lors de la récupération des indicateurs de programme: {e}")
        
        return program_indicators
    
    def translate_text(self, text: str, source_lang: str = 'en', target_lang: str = 'fr') -> str:
        """
        Traduit un texte en utilisant Google Translate
        
        Args:
            text: Texte à traduire
            source_lang: Langue source (défaut: 'en')
            target_lang: Langue cible (défaut: 'fr')
        
        Returns:
            Texte traduit
        """
        if not text or not isinstance(text, str):
            return text
        
        try:
            # Petite pause pour éviter de surcharger l'API de traduction
            time.sleep(0.1)
            
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
            return translated
        except Exception as e:
            print(f"Erreur de traduction pour '{text}': {e}")
            return text
    
    def update_indicator(self, indicator_id: str, data: Dict[str, Any]) -> bool:
        """Met à jour un indicateur dans DHIS2"""
        url = f"{self.base_url}/api/indicators/{indicator_id}"
        
        try:
            response = self.session.put(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'indicateur {indicator_id}: {e}")
            return False
    
    def update_program_indicator(self, program_indicator_id: str, data: Dict[str, Any]) -> bool:
        """Met à jour un indicateur de programme dans DHIS2"""
        url = f"{self.base_url}/api/programIndicators/{program_indicator_id}"
        
        try:
            response = self.session.put(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'indicateur de programme {program_indicator_id}: {e}")
            return False
    
    def translate_and_update_indicators(self, dry_run: bool = True):
        """Traduit et met à jour tous les indicateurs"""
        print("Récupération des indicateurs...")
        indicators = self.get_indicators()
        print(f"Found {len(indicators)} indicators")
        
        for indicator in indicators:
            original_name = indicator.get('name', '')
            original_shortname = indicator.get('shortName', '')
            
            # Traduire le nom et le shortName
            translated_name = self.translate_text(original_name)
            translated_shortname = self.translate_text(original_shortname)
            
            print(f"\nIndicateur: {indicator['id']}")
            print(f"Original: {original_name} / {original_shortname}")
            print(f"Traduit: {translated_name} / {translated_shortname}")
            
            if not dry_run:
                # Préparer les données de mise à jour
                update_data = {
                    'name': translated_name,
                    'shortName': translated_shortname
                }
                
                # Mettre à jour l'indicateur
                success = self.update_indicator(indicator['id'], update_data)
                if success:
                    print("✓ Mise à jour réussie")
                else:
                    print("✗ Échec de la mise à jour")
    
    def translate_and_update_program_indicators(self, dry_run: bool = True):
        """Traduit et met à jour tous les indicateurs de programme"""
        print("Récupération des indicateurs de programme...")
        program_indicators = self.get_program_indicators()
        print(f"Found {len(program_indicators)} program indicators")
        
        for pi in program_indicators:
            original_name = pi.get('name', '')
            original_shortname = pi.get('shortName', '')
            
            # Traduire le nom et le shortName
            translated_name = self.translate_text(original_name)
            translated_shortname = self.translate_text(original_shortname)
            
            print(f"\nIndicateur de programme: {pi['id']}")
            print(f"Original: {original_name} / {original_shortname}")
            print(f"Traduit: {translated_name} / {translated_shortname}")
            
            if not dry_run:
                # Préparer les données de mise à jour
                update_data = {
                    'name': translated_name,
                    'shortName': translated_shortname
                }
                
                # Mettre à jour l'indicateur de programme
                success = self.update_program_indicator(pi['id'], update_data)
                if success:
                    print("✓ Mise à jour réussie")
                else:
                    print("✗ Échec de la mise à jour")

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
    
    # Mode dry-run (True pour tester sans modifier, False pour appliquer les changements)
    DRY_RUN = True
    
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