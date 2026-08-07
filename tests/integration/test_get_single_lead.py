from tests.conftest import create_leads


def test_get_single_lead_returns_200_int(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    count = 1

    user = fake_current_user

    leads = create_leads(create_test_session, user, count)

    response = testing_session.get(
        f"/leads/{leads[0].lead_id}", headers=fake_authenticated_active_user_headers)

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Test Lead 1"


def test_get_single_lead_unauthenticated_returns_401_int(testing_session, fake_unauthenticated_user_headers, fake_current_user, create_test_session):

    count = 1

    user = fake_current_user

    leads = create_leads(create_test_session, user, count)

    response = testing_session.get(
        f"/leads/{leads[0].lead_id}", headers=fake_unauthenticated_user_headers)

    assert response.status_code == 401


def test_get_single_lead_inactive_returns_400_int(testing_session, fake_unauthenticated_inactive_user_headers, fake_current_user, create_test_session):

    count = 1

    user = fake_current_user

    leads = create_leads(create_test_session, user, count)

    response = testing_session.get(
        f"/leads/{leads[0].lead_id}", headers=fake_unauthenticated_inactive_user_headers)

    assert response.status_code == 400


def test_get_single_lead_not_found_returns_404_int(testing_session, fake_authenticated_active_user_headers, fake_current_user, create_test_session):

    count = 1

    user = fake_current_user

    leads = create_leads(create_test_session, user, count)

    response = testing_session.get(
        f"/leads/{leads[0].lead_id + 1}", headers=fake_authenticated_active_user_headers)

    assert response.status_code == 404


def test_get_single_lead_unauthorized_returns_404_int(testing_session, fake_authenticated_active_user_headers, fake_current_user, second_fake_user, create_test_session):

    # User 1 setup

    count1 = 1

    user1 = fake_current_user

    leads_user1 = create_leads(create_test_session, user1, count1)

    # User 2 setup

    count2 = 1

    user2 = second_fake_user

    leads_user2 = create_leads(create_test_session, user2, count2)

    response = testing_session.get(
        f"/leads/{leads_user2[0].lead_id}", headers=fake_authenticated_active_user_headers)

    assert response.status_code == 404
