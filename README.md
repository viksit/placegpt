## Run
```bash
pip install -r requirements.txt
python server.py
```

## Build and Run with Docker
```shell
docker build . -t simple-todo-plugin-no-auth
docker run -it --rm -p 8080:8080 simple-todo-plugin-no-auth
```
