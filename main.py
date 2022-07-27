import config
import requests
import json
import logging


def get_pipelines(username: str, password: str, workspace: str, repo_slug: str):
    size = None
    page_size = None
    page = 1
    headers = {
        "Accept": "application/json"
    }
    while size is None or size/page_size > page:
        if size:
            print(f"Downloading page {page}/{size / page_size}")
        url = (f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/"
               f"pipelines/?page={page}&sort=-created_on")
        response = requests.request(
            "GET",
            url,
            headers=headers, auth=(username, password)
        )
        pipelines = json.loads(response.text)
        logging.info(json.dumps(pipelines, sort_keys=True, indent=4, separators=(",", ": ")))
        if size is None:
            size = pipelines['size']
            page_size = pipelines['pagelen']
        for pipeline in pipelines['values']:
            yield pipeline
        page += 1


def start_pipeline(username, password, workspace, repo_slug, branch):
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pipelines/"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "target": {
            "ref_type": "branch",
            "type": "pipeline_ref_target",
            "ref_name": branch
        }
    })

    response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=(username, password)
    )
    logging.debug(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    if response.ok:
        return True
    else:
        return False


def check_pipelines():
    workspace = config.config_vars['workspace']
    repo_slug = config.config_vars['repo_slug']
    username = config.config_vars['username']
    password = config.config_vars['password']

    pipelines = get_pipelines(username, password, workspace, repo_slug)
    pipelines = (pipeline for pipeline in pipelines if pipeline['target'].get('ref_type') == 'branch')
    pipelines = (pipeline for pipeline in pipelines if pipeline['target']['ref_name'].startswith("dev-"))
    completed_branches = []

    for pipeline in pipelines:
        if pipeline['target']['ref_name'] in completed_branches:
            continue
        if pipeline['state']['name'] == 'COMPLETED':
            completed_branches.append(pipeline['target']['ref_name'])
            continue
        if pipeline['state']['name'] == 'IN_PROGRESS' and pipeline['state']['stage']['name'] != 'HALTED':
            print(f"Pipeline already running for branch {pipeline['target']['ref_name']}")
            break
        print(f"Attempting to start pipeline for branch {pipeline['target']['ref_name']}")
        if start_pipeline(username, password, workspace, repo_slug, pipeline['target']['ref_name']):
            break
        else:
            print(f"Pipeline start failed for branch {pipeline['target']['ref_name']}")


def main(data, context):
    check_pipelines()


if __name__ == '__main__':
    main('data', 'context')
