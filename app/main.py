from fastapi import FastAPI
from app.routes import poem_routes
from app.routes import process_prompt_route

app = FastAPI()

# Include the poem_routes router
app.include_router(poem_routes.router)

# Include the process_prompt_route router
app.include_router(process_prompt_route.router)
