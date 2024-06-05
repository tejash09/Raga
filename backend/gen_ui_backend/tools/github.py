import os
import requests
from langchain.pydantic_v1 import BaseModel, Field
from typing import Dict, Union
from langchain_core.tools import tool

class GithubRepoInput(BaseModel):
    owner: str = Field(..., description="The name of the repository owner.")
    repo: str = Field(..., description="The name of the repository.")

@tool("github-repo", args_schema=GithubRepoInput, return_direct=True)
def github_repo(input: GithubRepoInput) -> Union[Dict, str]:
    if not os.environ.get("GITHUB_TOKEN"):
        raise ValueError("Missing GITHUB_TOKEN secret.")
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    url = f"https://api.github.com/repos/{input.owner}/{input.repo}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repo_data = response.json()
        return {
            **input.dict(),
            "description": repo_data.get("description", ""),
            "stars": repo_data.get("stargazers_count", 0),
            "language": repo_data.get("language", ""),
        }
    except requests.exceptions.RequestException as err:
        print(err)
        return "There was an error fetching the repository. Please check the owner and repo names."