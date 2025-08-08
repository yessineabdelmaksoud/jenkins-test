from app import app

def test_home():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello, Jenkins Pipeline!" in response.data

# Ajoutez ce test qui va échouer intentionnellement
def test_failure():
    assert False, "Échec simulé pour tester Jenkins"