# Database (Postgres)

## ORM: [SQLAlchemy](https://www.sqlalchemy.org/)

## Migrations: [Alembic](https://github.com/sqlalchemy/alembic)

### Create Migration

1. Update `models.py` file
2. Enter virtual environment
3. AutoGenerate alembic > version
    ```
    alembic revision --autogenerate -m "<NAME_OF_REVISION>"
    ```
4. Push latest version to database
    ```
    alembic upgrade head
    ```

### Resources
- [YT - Demo - 1](https://www.youtube.com/watch?v=bfelC61XKO4)
- [TY - Demo - 2](https://www.youtube.com/watch?v=i9RX03zFDHU)