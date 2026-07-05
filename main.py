import uvicorn

if __name__ == "__main__":
    # Goes to the app folder to run the fastapi instance that's called app in the file app.py. (folder.file:instance)
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
