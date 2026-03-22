# Задачи на неделю

**Артём Жаба**
1. Сделать метод, который получает из s3 хранилища schema.json по link_id
2. В /modules/link/service.py -> добавляем этот метод
3. В /modules/link/resolver.py -> подключить метод
4. Для получаения воспользуйся s3_client из /lib/s3.py (пример в /modules/link/strategies/check.py в методе get_checks)
   
**Артём**
1. Реализовать контакты (перенести)
1.1 В папке /database/models создать файл contact.py   
1.2 Идем в папку modules и создаем папку contact -> schema.py, service.py, resolver.py   
1.3 В schema.py содаешь ContactSchemaOut(BaseModel): ... и пишешь те же поля, что и в database model 
1.4 В service.py содаешь ContectService: ... и по примеру из TariffService пишешь только метод list, меняя TariffModel на ContactModel 
1.5 В resolver.py содаешь ContectResolver: ... и по примеру из TariffResolver пишешь только метод list, меняя tariff service and schema на contact service and schema 

**Тимофей**
1. Сделать так чтобы schema.json в s3 добавлялся
2. Для сохранения воспользуйся s3_client из /lib/s3.py (пример в /modules/link/strategies/check.py в методе save_check)
3. Вызывать сравнение слепков нужно в /modules/link/tasks.py (когда приступишь, напиши мне, чтобы я сказал, где конкретно вызывать)
