def test_update_permissions(self):
    """Teste les permissions avec un indicateur de test"""
    test_indicator = {
        'name': 'Test Indicator',
        'shortName': 'Test',
        'id': 'abcdef12345'  # Remplacez par un ID réel
    }
    
    url = f"{self.base_url}/api/indicators/{test_indicator['id']}"
    response = self.session.get(url)
    
    if response.status_code == 200:
        print("✓ Lecture autorisée")
        # Essayer une mise à jour mineure
        data = response.json()
        original_name = data['name']
        data['name'] = 'Test Update'
        
        response_put = self.session.put(url, json=data)
        if response_put.status_code == 200:
            print("✓ Écriture autorisée")
            # Restaurer le nom original
            data['name'] = original_name
            self.session.put(url, json=data)
            return True
        else:
            print(f"✗ Écriture refusée: {response_put.status_code}")
            return False
    else:
        print(f"✗ Lecture refusée: {response.status_code}")
        return False