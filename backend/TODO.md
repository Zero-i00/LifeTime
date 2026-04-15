# Задачи на неделю

**Артём Жаба**
В user/service исправить метод update, чтобы метод работал не как put, а как patch. Сейчас при обновлении мы получаю такую ошибку:
```json
{
    "detail": [
        {
            "type": "missing",
            "loc": [
                "body",
                "password"
            ],
            "msg": "Field required",
            "input": {
                "full_name": "test 2",
                "email": "test@test.com"
            }
        },
        {
            "type": "missing",
            "loc": [
                "body",
                "tariff_id"
            ],
            "msg": "Field required",
            "input": {
                "full_name": "test 2",
                "email": "test@test.com"
            }
        },
        {
            "type": "missing",
            "loc": [
                "body",
                "last_login_at"
            ],
            "msg": "Field required",
            "input": {
                "full_name": "test 2",
                "email": "test@test.com"
            }
        }
    ]
}
```
   
**Артём**
Убрать из project services метода list все поля у ссылок, кроме id и url 
1. Новая схема в modules/project/schema.py:                                                                                                                                                                                                
   class LinkSchemaShortOut(BaseModel):                                                                                                                                                                                                          
   id: int                                               
   url: str                                                                                                                                                                                                                               
   model_config = ConfigDict(from_attributes=True)

2. Заменить тип links в ProjectSchemaOut — вместо List[LinkSchemaOut] использовать List[LinkSchemaShortOut]:                                                                                                                                  
   links: List['LinkSchemaShortOut'] = []

3. Обновить to_schema() в project/service.py — маппить ссылки через новую схему:                                                                                                                                                           
   links=[LinkSchemaShortOut(id=link.id, url=link.url) for link in obj.links]

**Тимофей**
1. Добавить зависимости

В pyproject.toml в секцию [project.optional-dependencies]:

dev = [                                                                                                                                                                                                                                    
"watchfiles",                                                                                                                                                                                                                          
"pytest>=8.0",
"pytest-asyncio>=0.24",                                                                                                                                                                                                                
"pytest-mock>=3.14",                                  
]

Установить:                                                                                                                                                                                                                                
uv sync --extra dev

  ---
2. Структура папок

backend/
└── tests/                                                                                                                                                                                                                                 
├── __init__.py                                       
├── conftest.py              # общие фикстуры
└── modules/
├── __init__.py                                                                                                                                                                                                                    
└── user/
├── __init__.py                                                                                                                                                                                                                
└── test_user_service.py
                                                                                                                                                                                                                                             
---
3. conftest.py — мок-сессия

import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def session():                                                                                                                                                                                                                             
s = AsyncMock()                                       
s.add = MagicMock()       # add() — синхронный
s.commit = AsyncMock()                                                                                                                                                                                                                 
s.refresh = AsyncMock()
s.delete = AsyncMock()                                                                                                                                                                                                                 
s.execute = AsyncMock()                                                                                                                                                                                                                
s.get = AsyncMock()
return s
                                                            
---
4. Пример теста — UserService

# tests/modules/user/test_user_service.py
import pytest                                                                                                                                                                                                                              
from unittest.mock import MagicMock, AsyncMock            
from fastapi import HTTPException
from modules.user.service import UserService

@pytest.mark.asyncio                                                                                                                                                                                                                       
async def test_retrieve_raises_404_when_not_found(session):
session.get.return_value = None                                                                                                                                                                                                        
service = UserService()

      with pytest.raises(HTTPException) as exc:                                                                                                                                                                                              
          await service.retrieve(session, user_id=999)
                                                                                                                                                                                                                                             
      assert exc.value.status_code == 404                   


@pytest.mark.asyncio
async def test_retrieve_returns_user(session):
mock_user = MagicMock()                                                                                                                                                                                                                
mock_user.id = 1
session.get.return_value = mock_user                                                                                                                                                                                                   
service = UserService()

      result = await service.retrieve(session, user_id=1)                                                                                                                                                                                    
  
      assert result.id == 1                                                                                                                                                                                                                  
      session.get.assert_awaited_once_with(MagicMock.__class__, 1)


@pytest.mark.asyncio                                                                                                                                                                                                                       
async def test_update_changes_email_and_name(session):    
mock_user = MagicMock()
mock_user.email = "old@test.com"                                                                                                                                                                                                       
mock_user.full_name = "Old Name"
session.get.return_value = mock_user

      from modules.user.schema import UserSchemaUpdate
      service = UserService()                                                                                                                                                                                                                
      update = UserSchemaUpdate(email="new@test.com", full_name="New Name")

      await service.update(session, user_id=1, obj=update)                                                                                                                                                                                   
  
      assert mock_user.full_name == "New Name"                                                                                                                                                                                               
      session.commit.assert_awaited_once()                  
                                                                                                                                                                                                                                             
---
5. pytest.ini (в корне backend/)

[pytest]
asyncio_mode = auto
pythonpath = src

pythonpath = src — чтобы импорты from modules.user.service import ... работали без sys.path хаков.
                                                                                                                                                                                                                                             
---                                                                                                                                                                                                                                        
6. Запуск

uv run pytest tests/ -v
                                                                                                                                                                                                                                             
---
Что покрываем в первую очередь по сервисам:

┌────────────────┬─────────────────────────────────────────────────────────────────────────────┐
│     Сервис     │                              Методы для тестов                              │                                                                                                                                           
├────────────────┼─────────────────────────────────────────────────────────────────────────────┤                                                                                                                                           
│ UserService    │ retrieve (404), update (patch-семантика), hash_password / validate_password │
├────────────────┼─────────────────────────────────────────────────────────────────────────────┤                                                                                                                                           
│ ProjectService │ retrieve (404 + wrong user), create, delete                                 │                                                                                                                                           
├────────────────┼─────────────────────────────────────────────────────────────────────────────┤
