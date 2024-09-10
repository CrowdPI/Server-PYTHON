# CrowdPI > Server : Python

## Database (Postgres)

### Migrations (Alembic)

- [YT - Demo - 1](https://www.youtube.com/watch?v=bfelC61XKO4)
- [TY - Demo - 2](https://www.youtube.com/watch?v=i9RX03zFDHU)

#### Create Migration

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

## Setup
1. Create Virtual Environment (adds venv directory to project)
```bash
python3 -m venv venv
```

2. Active Virtual Environment
```bash
source venv/bin/activate
```

> you should see `(venv)` at the beginning of your prompt indicating you are in the `venv` virtual environment

3. Install Project Packages into Active Virtual Environment

    ```bash
    pip3 install -r requirements.txt
    ```

    - To update the requirements.txt file
        ```
        # WARNING: this will override the existing file
        pip3 freeze > testing-req-updates.txt
        pip3 freeze > requirements.txt
        ```

4. Run Server

```bash
python3 index.py
```