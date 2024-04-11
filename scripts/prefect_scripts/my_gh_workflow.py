import httpx  # an HTTP client library and dependency of Prefect
from prefect import flow, task


@task(retries=2)
def get_repo_info(repo_owner: str, repo_name: str):
    """Get info about a repo - will retry twice after failing"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    api_response = httpx.get(url)
    api_response.raise_for_status()
    repo_info = api_response.json()
    return repo_info


@task
def get_contributors(repo_info: dict):
    """Get contributors for a repo"""
    contributors_url = repo_info["contributors_url"]
    response = httpx.get(contributors_url)
    response.raise_for_status()
    contributors = response.json()
    return contributors


@flow(log_prints=True, persist_result=True)
def repo_info(repo_owner: str = "PrefectHQ", repo_name: str = "prefect"):
    """
    Given a GitHub repository, logs the number of stargazers
    and contributors for that repo and return the two numbers.
    """
    info = get_repo_info(repo_owner, repo_name)
    stars = info["stargazers_count"]
    print(f"Stars 🌠 : {stars}")

    contributors = get_contributors(info)
    num_contributors = len(contributors)
    print(f"Number of contributors 👷: {num_contributors}")

    return stars, num_contributors


if __name__ == "__main__":
    repo_info(repo_owner="AccelerationConsortium", repo_name="ac-training-lab")
