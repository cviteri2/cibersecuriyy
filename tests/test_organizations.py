from tests.conftest import login
from app.models.organization import Organization
from app.extensions import db


def test_create_organization(client, seeded, app):
    login(client, "admin@demo-corp.ec")
    resp = client.post(
        "/organizations/new",
        data={"legal_name": "Nueva Empresa S.A.", "country": "Ecuador"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        org = Organization.query.filter_by(legal_name="Nueva Empresa S.A.").first()
        assert org is not None


def test_edit_organization(client, seeded, app):
    login(client, "admin@demo-corp.ec")
    with app.app_context():
        org = Organization.query.first()
        org_id = org.id

    resp = client.post(
        f"/organizations/{org_id}/edit",
        data={"legal_name": "Empresa Demo S.A. Modificada", "country": "Ecuador"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        updated = db.session.get(Organization, org_id)
        assert updated.legal_name == "Empresa Demo S.A. Modificada"


def test_organization_isolation_client_cannot_access_other_org(client, seeded, app):
    with app.app_context():
        other_org = Organization(legal_name="Otra Organización Aislada")
        db.session.add(other_org)
        db.session.commit()
        other_org_id = other_org.id

    login(client, "cliente@demo-corp.ec")
    resp = client.get(f"/organizations/{other_org_id}")
    assert resp.status_code == 403


def test_organization_isolation_client_can_access_own_org(client, seeded, app):
    with app.app_context():
        from app.models.user import User

        client_user = User.query.filter_by(email="cliente@demo-corp.ec").first()
        own_org_id = client_user.organization_id

    login(client, "cliente@demo-corp.ec")
    resp = client.get(f"/organizations/{own_org_id}")
    assert resp.status_code == 200
