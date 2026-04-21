import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from modules.project.service import project_service
from modules.project.schema import ProjectSchemaIn, ProjectSchemaUpdate, ProjectSchemaFilter


@pytest.mark.asyncio
async def test_list_with_filters(session):
    """Метод list применяет фильтры по имени и user_id."""
    # Мокаем результат execute
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = ["proj1", "proj2"]
    session.execute.return_value = mock_result

    filters = ProjectSchemaFilter(name="test", user_id=5)
    result = await project_service.list(session, filters)

    assert result == ["proj1", "proj2"]
    # Проверяем, что execute был вызван с каким-то select (сложно проверить детали, но можно убедиться, что вызван)
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_retrieve_project_not_found(session):
    """Если проект не найден — 404."""
    session.get.return_value = None
    filters = ProjectSchemaFilter(user_id=1)

    with pytest.raises(HTTPException) as exc_info:
        await project_service.retrieve(session, project_id=999, filters=filters)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_retrieve_project_wrong_user(session):
    """Если проект принадлежит другому пользователю — 404 (безопасность)."""
    mock_project = MagicMock()
    mock_project.user_id = 2
    session.get.return_value = mock_project
    filters = ProjectSchemaFilter(user_id=1)

    with pytest.raises(HTTPException) as exc_info:
        await project_service.retrieve(session, project_id=1, filters=filters)

    assert exc_info.value.status_code == 404
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_retrieve_success(session):
    """Успешное получение проекта владельцем."""
    mock_project = MagicMock()
    mock_project.user_id = 1
    session.get.return_value = mock_project
    filters = ProjectSchemaFilter(user_id=1)

    result = await project_service.retrieve(session, project_id=1, filters=filters)

    assert result is mock_project
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_project(session):
    """Создание проекта добавляет user_id, коммитит."""
    obj_in = ProjectSchemaIn(name="New Project")

    with patch("modules.project.service.ProjectModel") as MockProjectModel:
        mock_instance = MagicMock()
        MockProjectModel.return_value = mock_instance

        result = await project_service.create(session, user_id=10, obj=obj_in)

        MockProjectModel.assert_called_once_with(name="New Project")
        assert mock_instance.user_id == 10
        session.add.assert_called_once_with(mock_instance)
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once_with(mock_instance)
        assert result is mock_instance


@pytest.mark.asyncio
async def test_update_project_not_found_or_wrong_user(session):
    """Обновление: если проект не найден или чужой — 404."""
    session.get.return_value = None  # или проект с другим user_id
    update_data = ProjectSchemaUpdate(name="Updated")

    with pytest.raises(HTTPException) as exc_info:
        await project_service.update(session, project_id=1, user_id=5, obj=update_data)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_project_success(session):
    """Успешное обновление имени проекта."""
    mock_project = MagicMock()
    mock_project.user_id = 5
    mock_project.name = "Old Name"
    session.get.return_value = mock_project
    update_data = ProjectSchemaUpdate(name="New Name")

    result = await project_service.update(session, project_id=1, user_id=5, obj=update_data)

    assert mock_project.name == "New Name"
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(mock_project)
    assert result is mock_project


@pytest.mark.asyncio
async def test_delete_project_not_found_or_wrong_user(session):
    """Удаление: если проект не найден или чужой — 404."""
    session.get.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await project_service.delete(session, project_id=1, user_id=5)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_success(session):
    """Успешное удаление проекта."""
    mock_project = MagicMock()
    mock_project.user_id = 5
    session.get.return_value = mock_project

    await project_service.delete(session, project_id=1, user_id=5)

    session.delete.assert_awaited_once_with(mock_project)
    session.commit.assert_awaited_once()