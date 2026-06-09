from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import teams, login, players, users, weeks, weekdays, days, matches

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(weeks.router)
app.include_router(weekdays.router)
app.include_router(days.router)
app.include_router(matches.router)


@app.get("/")
async def root():
    return {"message": "This is the API homepage"}