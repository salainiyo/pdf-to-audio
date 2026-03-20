test_user = {
    "email":"testuser@gmail.com",
    "password":"Password@123"
}
invalid_email_user = {
    "email":"testuser.gmail.com",
    "password":"Password@123"
}
invalid_pwd_user = {
    "email":"testuser@gmail.com",
    "password":"assword@123"
}

class TestRegister:
    def test_existing_user(self, client):
        response = client.post("/auth/register", json=test_user)
        response = client.post("/auth/register", json=test_user)
        assert response.status_code == 400

    def test_successful_registration(self, client):
        response = client.post("/auth/register", json=test_user)
        assert response.status_code == 201

    def test_invalid_email(self, client):
        response = client.post("/auth/register", json=invalid_email_user)
        assert response.status_code == 422

    def test_invalid_pwd(self, client):
        response = client.post("/auth/register", json=invalid_email_user)
        assert response.status_code ==422