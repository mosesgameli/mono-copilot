from agents import Agent, Runner
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

load_dotenv()

app = FastAPI()

agent = Agent(
    name="History Tutor",
    instructions="You answer history questions clearly and concisely.",
)


class AgentRequest(BaseModel):
    user_input: str


class AgentResponse(BaseModel):
    response: str


def _mask_secret(value: str | None) -> str:
    if not value:
        return "<missing>"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"





@app.get("/")
def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.post("/agent", response_model=AgentResponse)
async def run_agent(request: AgentRequest) -> AgentResponse:
    try:
        result = await Runner.run(agent, request.user_input)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}") from exc

    return AgentResponse(response=str(result.final_output))


def run() -> None:
    uvicorn.run("copilot.main:app", host="127.0.0.1", port=8000, reload=False)


def dev() -> None:
    uvicorn.run("copilot.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()
