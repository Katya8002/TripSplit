def test_admin_login_page_opens(client):
    response = client.get("/admin/login/")
    assert response.status_code == 200

def test_cors_allows_frontend_origin(client):
    response = client.get("/api/trips/", HTTP_ORIGIN="http://localhost:5173")
    assert response["Access-Control-Allow-Origin"] == "http://localhost:5173"