test_user = {
    "email":"testuser@gmai.com",
    "password":"Password@123"
}

def test_user_registration(client):
    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 201