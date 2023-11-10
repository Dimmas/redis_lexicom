Дано две таблицы в СУБД Postgres short_names на 700 000 записей и full_names на 500 000записей
В обеих таблицах поля name и status.
В одной таблице хранятся имена файлов без расширения. В другой хранятся имена файлов с
расширением. Одинаковых названий с разными расширениями быть не может, количество
расширений не определено, помимо wav и mp3 может встретиться что угодно.
Нам необходимо минимальным количеством запросов к СУБД перенести данные о статусе из
таблицы short_names в таблицу full_names.
Необходимо понимать, что на выполнение запросов / время работы скрипта нельзя тратить
больше 10 минут. Лучшее время выполнения этого тестового задания в 2022 году - 45 секунд на
SQL запросе.
Необходимо предоставить два и более варианта решения этой задачи.

# Решение задания
Создадим эти таблицы и заполним данными
``` 
CREATE FUNCTION tables_create() RETURNS integer AS $$
DECLARE
    name text;
    st integer := 0;
    i integer := 0;
BEGIN
  CREATE TABLE short_names (name text, status integer);
  CREATE TABLE full_names (name text, status integer);
  
  WHILE i < 700000 LOOP
    name := 'name' || i;
    INSERT INTO short_names (name, status) VALUES (name , st);
    IF i < 500000 THEN
      name := name || '.mp3';
      INSERT INTO full_names (name, status) VALUES (name, NULL);
    END IF;
    i := i + 1;
    IF st = 1 THEN
       st := 0;
    ELSE
       st := 1;
    END IF;
  END LOOP;
  RETURN i;
END;
$$ LANGUAGE plpgsql;

SELECT tables_create();
```

# Решение 1:
Создадим представление соединения таблиц full_names и short_names
```
CREATE VIEW sh_names AS select full_names.status, full_names.name from full_names join short_names on position(short_names.name || '.' in full_names.name) <> 0
AND short_names.status = 1;

CREATE RULE SH_NAMES_Update AS
ON UPDATE TO sh_names DO INSTEAD
( 
  UPDATE full_names SET status = new.status
    WHERE full_names.name=old.name;
)

```
Применим изменение статуса
```
UPDATE sh_names SET status = 1;
COMMIT;
```


# Решение 2:
Создадим представление таблицы short_names
``` 
CREATE VIEW sh_names AS select status, substring(name from 1 for (position('.' in name) - 1)) as sh_name  from full_names
```

Выполним запрос на обновление данных
``` 
UPDATE sh_names SET status =
    (SELECT status FROM short_names
     WHERE short_names.name = sh_names.sh_name AND short_names.status = 1);
COMMIT;
```


