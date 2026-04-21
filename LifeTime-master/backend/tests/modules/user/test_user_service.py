import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from modules.user.service import user_service
from modules.user.schema import UserSchemaIn, UserSchemaUpdate


@pytest.mark.asyncio
async def test_retrieve_user_not_found_raises_404(session):
    """Если пользователь не найден, выбрасывается HTTP 404."""
    session.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await user_service.retrieve(session, user_id=999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_retrieve_returns_user_when_found(session):
    """Если пользователь найден, возвращается объект модели."""
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.email = "test@example.com"
    session.get.return_value = mock_user

    result = await user_service.retrieve(session, user_id=1)

    assert result is mock_user
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_email_returns_user(session):
    """Поиск по email возвращает пользователя."""
    mock_user = MagicMock()
    mock_user.email = "test@example.com"
    # Эмулируем выполнение select
    mock_result = MagicMock()
    mock_result.scalars().one_or_none.return_value = mock_user
    session.execute.return_value = mock_result

    result = await user_service.get_by_email(session, email="test@example.com")

    assert result is mock_user
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_email_not_found_raises_404(session):
    """Если email не найден — 404."""
    mock_result = MagicMock()
    mock_result.scalars().one_or_none.return_value = None
    session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await user_service.get_by_email(session, email="missing@example.com")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_create_user_hashing_password_and_commits(session):
    """Создание пользователя: хеширует пароль, добавляет в сессию, коммитит."""
    from datetime import datetime

    # Подготовим входные данные
    obj_in = UserSchemaIn(
        email="new@example.com",
        password="secret123",
        full_name="New User",
        tariff_id=1,
        last_login_at=datetime.now()   # передаём реальный datetime
    )

    # Мокаем модель, чтобы не создавать реальный объект БД
    with patch("modules.user.service.UserModel") as MockUserModel:
        mock_user_instance = MagicMock()
        MockUserModel.return_value = mock_user_instance

        result = await user_service.create(session, obj=obj_in)

        # Проверяем, что модель была создана с правильными полями
        MockUserModel.assert_called_once_with(
            email="new@example.com",
            full_name="New User",
            tariff_id=1,
            last_login_at=obj_in.last_login_at
        )
        # Пароль должен быть захэширован (не совпадать с исходным)
        assert mock_user_instance.password != b"secret123"
        # Методы сессии вызваны
        session.add.assert_called_once_with(mock_user_instance)
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once_with(mock_user_instance)
        assert result is mock_user_instance


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_update_user_changes_fields(session):
    """Обновление пользователя: изменяет email и full_name, коммитит."""
    from datetime import datetime

    mock_user = MagicMock()
    mock_user.email = "old@test.com"
    mock_user.full_name = "Old Name"
    session.get.return_value = mock_user

    # Создаём схему обновления со всеми обязательными полями
    update_data = UserSchemaUpdate(
        email="new@test.com",
        full_name="New Name",
        password="ignored_password",    # сервис update не использует пароль
        tariff_id=1,
        last_login_at=datetime.now()
    )

    result = await user_service.update(session, user_id=1, obj=update_data)

    assert mock_user.email == "new@test.com"
    assert mock_user.full_name == "New Name"
    session.add.assert_called_once_with(mock_user)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(mock_user)
    assert result is mock_user


@pytest.mark.asyncio
async def test_destroy_user_calls_delete(session):
    """Удаление пользователя: вызывает session.delete()."""
    mock_user = MagicMock()
    session.get.return_value = mock_user

    result = await user_service.destroy(session, user_id=1)

    assert result is True
    session.delete.assert_awaited_once_with(mock_user)


def test_hash_password_returns_bytes():
    """Статический метод hash_password возвращает bytes."""
    pwd = "mysecret"
    hashed = user_service.hash_password(pwd)
    assert isinstance(hashed, bytes)
    assert hashed != pwd.encode()


def test_validate_password_correct():
    """Проверка пароля: верный пароль — True, неверный — False."""
    pwd = "correct"
    hashed = user_service.hash_password(pwd)
    assert user_service.validate_password(pwd, hashed) is True
    assert user_service.validate_password("wrong", hashed) is False