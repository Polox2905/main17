import uvicorn
from fastapi import FastAPI
from routers import task
from routers import user


app = FastAPI()


@app.get("/")
async def welcom():
    return {"message": "Welcome to Taskmanager"}


app.include_router(task.router)
app.include_router(user.router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)