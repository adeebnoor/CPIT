import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.start:app", host="0.0.0.0", port=port, reload=False)
