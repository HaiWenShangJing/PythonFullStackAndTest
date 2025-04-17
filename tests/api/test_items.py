import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Item


@pytest.mark.asyncio
async def test_create_item(client: AsyncClient, db_session: AsyncSession):
    """Test creating a new item"""
    # Test data
    item_data = {
        "name": "Test Item",
        "description": "This is a test item"
    }
    
    # Make API request
    response = await client.post("/api/v1/items", json=item_data)
    
    # Validate response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    
    # Validate database record
    item_id = data["id"]
    db_item = await db_session.get(Item, uuid.UUID(item_id))
    assert db_item is not None
    assert db_item.name == item_data["name"]
    assert db_item.description == item_data["description"]


@pytest.mark.asyncio
async def test_read_items(client: AsyncClient, db_session: AsyncSession):
    """Test retrieving items list"""
    # Create test items in database
    items = [
        Item(name=f"Test Item {i}", description=f"Description {i}")
        for i in range(3)
    ]
    for item in items:
        db_session.add(item)
    await db_session.commit()
    
    # Make API request
    response = await client.get("/api/v1/items")
    
    # Validate response
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 3
    
    # Verify pagination
    response = await client.get("/api/v1/items?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_read_item(client: AsyncClient, db_session: AsyncSession):
    """Test retrieving a specific item"""
    # Create test item
    item = Item(name="Single Test Item", description="This is a single test item")
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    
    # Make API request
    response = await client.get(f"/api/v1/items/{item.id}")
    
    # Validate response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(item.id)
    assert data["name"] == item.name
    assert data["description"] == item.description
    
    # Test non-existent item
    random_id = uuid.uuid4()
    response = await client.get(f"/api/v1/items/{random_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_item(client: AsyncClient, db_session: AsyncSession):
    """Test updating an item"""
    # Create test item
    item = Item(name="Update Test Item", description="This will be updated")
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    
    # Make API request
    update_data = {"name": "Updated Name", "description": "Updated description"}
    response = await client.put(f"/api/v1/items/{item.id}", json=update_data)
    
    # Validate response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(item.id)
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    
    # Verify database record was updated
    await db_session.refresh(item)
    assert item.name == update_data["name"]
    assert item.description == update_data["description"]
    
    # Test partial update
    partial_update = {"name": "Partially Updated Name"}
    response = await client.put(f"/api/v1/items/{item.id}", json=partial_update)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == partial_update["name"]
    assert data["description"] == update_data["description"]  # Should remain unchanged


@pytest.mark.asyncio
async def test_delete_item(client: AsyncClient, db_session: AsyncSession):
    """Test deleting an item"""
    # Create test item
    item = Item(name="Delete Test Item", description="This will be deleted")
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    
    # Make API request
    response = await client.delete(f"/api/v1/items/{item.id}")
    
    # Validate response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(item.id)
    
    # Verify item was deleted from database
    deleted_item = await db_session.get(Item, item.id)
    assert deleted_item is None
    
    # Test deleting non-existent item
    random_id = uuid.uuid4()
    response = await client.delete(f"/api/v1/items/{random_id}")
    assert response.status_code == 404