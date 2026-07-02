from agents.sandbox import SandboxAgent, SandboxRunConfig
from agents.sandbox.capabilities import Capabilities, Skills
from agents.sandbox.entries import GitRepo
from agents.run import Runner, RunConfig
from agents.sandbox.sandboxes.unix_local import UnixLocalSandboxClient

agent = SandboxAgent(
    name="Tax prep assistant",
    instructions="Use the mounted skill before preparing the return.",
    capabilities=Capabilities.default() + [
        Skills(from_=GitRepo(repo="mosesgameli/myagentskills", ref="main")),
    ]
)


async def run() -> None:
    result = await Runner.run(agent, "run git status and return the output",  run_config=RunConfig(
            sandbox=SandboxRunConfig(client=UnixLocalSandboxClient()),
            workflow_name="Unix-local sandbox review",
        ),)
    
    print(f"Final output: {result.final_output}")


def main() -> None:
    import asyncio

    asyncio.run(run())