import pytest

from tests.factories import UserFactory


@pytest.mark.asyncio
async def test_user_router_lifecycle(test_client):
    user_data = UserFactory.as_dict()
    updated_user_data = UserFactory.as_dict(first_name="Updated", last_name="User")

    # Create a user
    response = await test_client.post(
        "/meeting_users/",
        json=user_data,
    )
    assert response.status_code == 200
    user_id = response.json()["id"]

    # List all users
    response = await test_client.get("/meeting_users/")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert any(user["id"] == user_id for user in users)

    # Get the user we created
    response = await test_client.get(f"/meeting_users/{user_id}")
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == user_id
    assert user["email"] == user_data["email"]

    assert user["first_name"] == user_data["first_name"]
    assert user["last_name"] == user_data["last_name"]

    # Update the user we created
    response = await test_client.put(
        f"/meeting_users/{user_id}",
        json=updated_user_data,
    )
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["id"] == user_id
    assert updated_user["first_name"] == updated_user_data["first_name"]
    assert updated_user["last_name"] == updated_user_data["last_name"]

    # Delete the user we created
    response = await test_client.delete(f"/meeting_users/{user_id}")
    assert response.status_code == 204

    # Verify deletion
    response = await test_client.get(f"/meeting_users/{user_id}")
    assert response.status_code == 404
