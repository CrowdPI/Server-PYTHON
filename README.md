# CrowdPI > Server : Python


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