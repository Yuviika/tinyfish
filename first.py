from tinyfish import TinyFish, RunStatus
from dotenv import load_dotenv
import json

load_dotenv()
client = TinyFish()

GOAL = (
    "Find software or AI internships for students. "
    "Return JSON: a list of role, location, deadline, link."
)

URL = "https://www.janestreet.com/join-jane-street/open-roles/"
run = client.agent.run(url=URL, goal=GOAL)

if run.status == RunStatus.COMPLETED:
    print(run.result)