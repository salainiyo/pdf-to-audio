test_user = {
    "email":"testuser@gmail.com",
    "password":"Password@123"
}
login_payload = {"username":test_user.get("email"),
                          "password":test_user.get("password")}

class TestRegister:
    invalid_email_user = {
        "email":"testuser.gmail.com",
        "password":"Password@123"
    }
    invalid_pwd_user = {
        "email":"testuser@gmail.com",
        "password":"assword@123"
    }

    def test_existing_user(self, client):
        response = client.post("/auth/register", json=test_user)
        response = client.post("/auth/register", json=test_user)
        data = response.json()
        assert response.status_code == 400
        assert "detail" in data

    def test_successful_registration(self, client):
        response = client.post("/auth/register", json=test_user)
        data = response.json()
        assert response.status_code == 201
        assert "id" in data


    def test_invalid_email(self, client):
        response = client.post("/auth/register", json=self.invalid_email_user)
        assert response.status_code == 422

    def test_invalid_pwd(self, client):
        response = client.post("/auth/register", json=self.invalid_email_user)
        assert response.status_code ==422

class TestLogin:
    wrong_password = {"username":test_user.get("email"), "password":str(test_user.get("password")).upper()}
    wrong_email = {"username":"whatever@gmail.com", "password":test_user.get("password")}
    def test_successful_login(self, client):
        response = client.post("/auth/register", json=test_user)
        response = client.post("/auth/login", data=login_payload)
        data = response.json()
        assert response.status_code == 200
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data

    def test_wrong_password(self, client):
        response = client.post("/auth/register", json=test_user)
        response = client.post("/auth/login", data=self.wrong_password)
        data = response.json()
        assert response.status_code == 401
        assert data["detail"] == "Invalid credentials"

    def test_wrong_email(self, client):
        response = client.post("/auth/register", json=test_user)
        response = client.post("/auth/login", data=self.wrong_password)
        data = response.json()
        assert response.status_code == 401
        assert data["detail"] == "Invalid credentials"

class TestLogout:
    def test_successful_logout(self, client):
        response = client.post("/auth/register", json=test_user)
        response = client.post("/auth/login", data=login_payload)
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"] 
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        payload = {
            "refresh_token": refresh_token
        }
        
        response = client.post("/auth/logout", headers=headers, json=payload)
        assert response.status_code == 201
    
    def test_unsuccessful_logout(self, client):
        response = client.post("/auth/register", json=test_user)
        response = client.post("/auth/login", data=login_payload)
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"] 
        headers = {
            "Authorization": f"Bearer {refresh_token}"
        }
        payload = {
            "refresh_token": refresh_token
        }
        
        response = client.post("/auth/logout", headers=headers, json=payload)
        assert response.status_code == 401

class TestRefresh:
    def test_sucessful_refresh(self, client):
        response = client.post("/auth/register", json=test_user)
        response = client.post("/auth/login", data=login_payload)
        access_token = response.json()["access_token"]
        response = client.post("auth/refresh", headers={"Authorization":f"bearer {access_token}"})
        data = response.json()
        assert response.status_code == 200
        assert "access_token" in data
        assert "refresh_token" in data


    def test_unsuccessful_refresh(self, client):
        response = client.post("/auth/register", json=test_user)
        response = client.post("/auth/login", data=login_payload)
        refresh_token = response.json()["refresh_token"]
        response = client.post("/auth/refresh", headers={"Authorization":f"bearer {refresh_token}"})
        data = response.json()
        assert "access_token" not in data
        assert "refresh_token" not in data
        assert response.status_code == 401

        
