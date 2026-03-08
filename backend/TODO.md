# Задачи на неделю

**Артём Жаба**
1. Добавить в ./modules/user/resolver.py метод обновления пользователя
   
**Артём**
1. Реализовать контакты (перенести)
1.1 В папке /database/models создать файл contact.py   
1.2 Идем в папку modules и создаем папку contact -> schema.py, service.py, resolver.py   
1.3 В schema.py содаешь ContactSchemaOut(BaseModel): ... и пишешь те же поля, что и в database model 
1.4 В service.py содаешь ContectService: ... и по примеру из TariffService пишешь только метод list, меняя TariffModel на ContactModel 
1.5 В resolver.py содаешь ContectResolver: ... и по примеру из TariffResolver пишешь только метод list, меняя tariff service and schema на contact service and schema 

**Тимофей**
-
