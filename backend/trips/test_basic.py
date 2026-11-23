def test_admin_login_page_opens(client):
    response = client.get("/admin/login/")
    assert response.status_code == 200