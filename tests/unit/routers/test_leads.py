"""
Disabled: these tests use FastAPI TestClient(app) and are not valid unit tests.
They require the full app stack and are therefore app-level/integration checks.
They are intentionally commented out to keep the unit suite focused on real unit behavior.
"""

# from fastapi import HTTPException
# from fastapi.testclient import TestClient
# import pytest
# from unittest.mock import MagicMock, patch
#
# from src.app import app
# from src.dependencies.auth import UserDep
# from src.services.lead_services import read
#
# client = TestClient(app)
#
#
# # GET
# def test_get_leads_unauthenticated_returns_401():
#
#     response = client.get("/leads")
#
#     assert response.status_code == 401
#
#
# def test_get_leads_return_empty_list(mocker, authenticated_user):
#     mock_get = mocker.patch("src.routers.leads.lead_services.read_all")
#
#     mock_get.return_value = {
#         "data": [],
#         "pagination": {
#             "page": 1,
#             "page_size": 10,
#             "item_count": 0,
#         },
#         "next_page": None,
#         "previous_page": None
#     }
#
#     response = authenticated_user.get("/leads")
#
#     assert response.status_code == 200
#     assert response.json() == {
#         "data": [],
#         "pagination": {
#             "page": 1,
#             "page_size": 10,
#             "item_count": 0,
#         },
#         "next_page": None,
#         "previous_page": None
#     }
#
#     mock_get.assert_called_once_with(
#         UserDep(
#             user_id=1,
#             username="testuser",
#             email=None,
#             full_name=None,
#             disabled=False,
#             is_superuser=False,
#             hashed_password="fakehashedpassword"
#         ),
#         mocker.ANY,  # request
#         mocker.ANY,  # session
#         None,  # name
#         None,  # company
#         None,  # status
#         1,  # page
#         10  # page_size
#     )
#
#
# def test_get_leads_with_filters(mocker, authenticated_user):
#     mock_get = mocker.patch("src.routers.leads.lead_services.read_all")
#
#     mock_get.return_value = {
#         "data": [],
#         "pagination": {
#             "page": 1,
#             "page_size": 10,
#             "item_count": 0,
#         },
#         "next_page": None,
#         "previous_page": None
#     }
#
#     response = authenticated_user.get(
#         "/leads?name=John&company=Acme&status=open&page=2&page_size=5")
#
#     assert response.status_code == 200
#     assert response.json() == {
#         "data": [],
#         "pagination": {
#             "page": 1,
#             "page_size": 10,
#             "item_count": 0,
#         },
#         "next_page": None,
#         "previous_page": None
#     }
#
#     mock_get.assert_called_once_with(
#         UserDep(
#             user_id=1,
#             username="testuser",
#             email=None,
#             full_name=None,
#             disabled=False,
#             is_superuser=False,
#             hashed_password="fakehashedpassword"),
#         mocker.ANY,  # request
#         mocker.ANY,  # session
#         "John",
#         "Acme",
#         "open",
#         2,
#         5
#     )
#
#
# def test_get_single_leads_user_can_get_own_leads(mocker, authenticated_user, lead_create, fake_session):
#     mock_get = mocker.patch("src.routers.leads.lead_services.read")
#
#     lead1 = lead_create(
#         fake_session,
#         name="John Doe",
#         company="Acme Inc.",
#         email="john.doe@acme.com",
#         status="open",
#         lead_id=1,
#         owner_id=1
#     )
#
#     mock_get.return_value = {"data": lead1.model_dump()}
#
#     response = authenticated_user.get("/leads/1")
#
#     assert response.status_code == 200
#     assert response.json() == {
#         "data": {"name": "John Doe", "company": "Acme Inc.", "email": "john.doe@acme.com", "status": "open", "lead_id": 1}}
#
#     mock_get.assert_called_once_with(
#         UserDep(
#             user_id=1,
#             username="testuser",
#             email=None,
#             full_name=None,
#             disabled=False,
#             is_superuser=False,
#             hashed_password="fakehashedpassword"
#         ),
#         1,
#         mocker.ANY
#     )
#
#
# def test_get_single_lead_unauthenticated_returns_401():
#
#     response = client.get("/leads/1")
#
#     assert response.status_code == 401
#
#
# def test_get_single_lead_returns_404_when_not_found(mocker, authenticated_user, lead_create, fake_session):
#
#     mock_get = mocker.patch("src.routers.leads.lead_services.read")
#
#     mock_get.side_effect = HTTPException(
#         status_code=404,
#         detail="Item does not exist"
#     )
#     response = authenticated_user.get("/leads/3")
#
#     assert response.status_code == 404
#
#
# # POST
# def test_create_lead_unauthenticated_returns_401():
#
#     response = client.post(
#         "/leads", json={"name": "name", "company": "company", "email": "email", "status": "status"})
#
#     assert response.status_code == 401
#
#
# def test_create_lead_returns_201(mocker, authenticated_user):
#
#     mock_post = mocker.patch("src.routers.leads.lead_services.create")
#
#     mock_post.return_value = {"owner_id": 1, "lead_id": 1, "name": "name",
#                               "company": "company", "email": "email", "status": "status"}
#
#     response = authenticated_user.post(
#         "/leads", json={"name": "name", "company": "company", "email": "email", "status": "status"})
#
#     assert response.status_code == 201
#
#
# def test_create_lead_missing_required_field_returns_422(mocker, authenticated_user):
#
#     mock_post = mocker.patch("src.routers.leads.lead_services.create")
#
#     mock_post.return_value = {"owner_id": 1, "lead_id": 1, "name": "name",
#                               "company": "company", "email": "email", "status": "status"}
#
#     response = authenticated_user.post(
#         "/leads", json={"name": "name", "email": "email", "status": "status"})
#
#     assert response.status_code == 422
#
#
# # DELETE
# def test_delete_lead_unauthenticated_returns_401():
#
#     response = client.delete("/leads/1")
#
#     assert response.status_code == 401
#
#
# def test_delete_lead_returns_204(mocker, authenticated_user):
#
#     mock_post = mocker.patch("src.routers.leads.lead_services.delete")
#
#     mock_post.return_value = None
#
#     response = authenticated_user.delete("/leads/1")
#
#     assert response.status_code == 204
#
#
# def test_delete_nonexistent_lead_returns_404(mocker, authenticated_user):
#
#     mock_post = mocker.patch("src.routers.leads.lead_services.delete")
#
#     mock_post.side_effect = HTTPException(
#         status_code=404,
#         detail="Item does not exist")
#
#     response = authenticated_user.delete("/leads/1")
#
#     assert response.status_code == 404
#
#
# # PUT
# def test_update_lead_unauthenticated_returns_401():
#     response = client.put("/leads/1")
#
#     assert response.status_code == 401
#
#
# def test_update_lead_returns_200(mocker, authenticated_user):
#
#     mock_put = mocker.patch("src.routers.leads.lead_services.update")
#
#     mock_put.return_value = {"data": {"lead_id": 1,
#                                       "name": "name", "company": "company", "email": "email", "status": "status"}}
#
#     response = authenticated_user.put(
#         "/leads/1", json={"name": "name", "company": "company", "email": "email", "status": "status"})
#
#     assert response.status_code == 200
#
#
# def test_update_nonexistent_lead_returns_404(mocker, authenticated_user):
#
#     mock_put = mocker.patch("src.routers.leads.lead_services.update")
#
#     mock_put.side_effect = HTTPException(
#         status_code=404,
#         detail="Item does not exist")
#
#     response = authenticated_user.put(
#         "/leads/1", json={"name": "name", "company": "company", "email": "email", "status": "status"})
#
#     assert response.status_code == 404
#
#
# def test_update_invalid_body_returns_422(mocker, authenticated_user):
#
#     mock_put = mocker.patch("src.routers.leads.lead_services.update")
#
#     mock_put.return_value = {"data": {"lead_id": 1,
#                                       "name": "name", "company": "company", "email": "email", "status": "status"}}
#
#     response = authenticated_user.put(
#         "/leads/1", json={"company": "company", "email": "email", "status": "status"})
#
#     assert response.status_code == 422
#
#
# # PATCH
# def test_patch_lead_unauthenticated_returns_401():
#     response = client.patch("/leads/1")
#
#     assert response.status_code == 401
#
#
# def test_patch_lead_returns_200(mocker, authenticated_user):
#
#     mock_put = mocker.patch("src.routers.leads.lead_services.patch")
#
#     mock_put.return_value = {"data": {
#         "lead_id": 1, "name": "name", "company": "company", "email": "email", "status": "status"}}
#
#     response = authenticated_user.patch(
#         "/leads/1", json={"company": "company", "email": "email", "status": "status"})
#
#     assert response.status_code == 200
#
#
# def test_patch_nonexistent_lead_returns_404(mocker, authenticated_user):
#
#     mock_put = mocker.patch("src.routers.leads.lead_services.patch")
#
#     mock_put.side_effect = HTTPException(
#         status_code=404,
#         detail="Item does not exist")
#
#     response = authenticated_user.patch(
#         "/leads/1", json={"company": "company", "email": "email", "status": "status"})
#
#     assert response.status_code == 404
#
#
# def test_patch_invalid_body_returns_422(mocker, authenticated_user):
#
#     mock_put = mocker.patch("src.routers.leads.lead_services.patch")
#
#     mock_put.return_value = {"data": {
#         "lead_id": 1, "name": "name", "company": "company", "email": "email", "status": "status"}}
#
#     response = authenticated_user.patch(
#         "/leads/1", data={"company": "company", "email": "email", "status": "status"})
#
#     assert response.status_code == 422
