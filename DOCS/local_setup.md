# Local Setup
1. Install Postgres
    ```
    brew install postgresql@14
    ```

2. Start Postgres
    ```
    brew services run postgresql@14
    ```

3. Create Database
    ```
    psql postgres

    postgres=# create database crowdpi;
    ```

4. Create Virtual Environment (adds venv directory to project)
    ```bash
    python3 -m venv venv
    ```

5. Active Virtual Environment
    ```bash
    source venv/bin/activate
    ```

> you should see `(venv)` at the beginning of your prompt indicating you are in the `venv` virtual environment

6. Install Project Packages into Active Virtual Environment

    ```bash
    pip3 install -r requirements.txt
    ```

    - To update the requirements.txt file
        ```
        # WARNING: this will override the existing file
        pip3 freeze > testing-req-updates.txt
        pip3 freeze > requirements.txt
        ```

7. Run Server
    ```bash
    python3 index.py
    ```