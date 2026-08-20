from tests.conftest import login


def test_login_correct(client, seeded):
    resp = login(client, "admin@demo-corp.ec")
    assert resp.status_code == 200
    assert "Organizaciones registradas".encode("utf-8") in resp.data or b"Panel" in resp.data


def test_login_incorrect_password(client, seeded):
    resp = login(client, "admin@demo-corp.ec", password="WrongPassword")
    assert resp.status_code == 200
    assert "Credenciales inválidas".encode("utf-8") in resp.data


def test_login_unknown_user(client, seeded):
    resp = login(client, "no-existe@demo-corp.ec", password="whatever")
    assert resp.status_code == 200
    assert "Credenciales inválidas".encode("utf-8") in resp.data


def test_access_without_authentication_redirects_to_login(client, seeded):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_role_authorization_client_cannot_list_organizations(client, seeded):
    login(client, "cliente@demo-corp.ec")
    resp = client.get("/organizations/")
    assert resp.status_code == 403


def test_role_authorization_admin_can_list_organizations(client, seeded):
    login(client, "admin@demo-corp.ec")
    resp = client.get("/organizations/")
    assert resp.status_code == 200


def test_role_authorization_client_cannot_reach_admin_area(client, seeded):
    login(client, "cliente@demo-corp.ec")
    resp = client.get("/admin/")
    assert resp.status_code == 403


def test_logout(client, seeded):
    login(client, "admin@demo-corp.ec")
    resp = client.get("/logout", follow_redirects=True)
    assert resp.status_code == 200
    resp2 = client.get("/organizations/", follow_redirects=False)
    assert resp2.status_code == 302
