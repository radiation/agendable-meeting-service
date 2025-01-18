import uuid

import pytest

user_data = {
    "id": str(uuid.uuid4()),
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
}

updated_user_data = {
    "first_name": "Updated",
    "last_name": "Name",
}


@pytest.mark.asyncio
async def test_user_router_lifecycle(test_client):
    # Create a user
    response = await test_client.post(
        "/users/",
        json=user_data,
    )
    assert response.status_code == 200
    user_id = response.json()["id"]

    # List all users
    response = await test_client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert any(user["id"] == user_id for user in users)

    # Get the user we created
    response = await test_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == user_id
    assert user["email"] == user_data["email"]

    assert user["first_name"] == user_data["first_name"]
    assert user["last_name"] == user_data["last_name"]

    # Update the user we created
    response = await test_client.put(
        f"/users/{user_id}",
        json=updated_user_data,
    )
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["id"] == user_id
    assert updated_user["first_name"] == updated_user_data["first_name"]
    assert updated_user["last_name"] == updated_user_data["last_name"]

    # Delete the user we created
    response = await test_client.delete(f"/users/{user_id}")
    assert response.status_code == 204

    # Verify deletion
    response = await test_client.get(f"/users/{user_id}")
    assert response.status_code == 404
