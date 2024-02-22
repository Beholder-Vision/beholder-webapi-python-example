
import argparse
import os
import os.path
import sys
import datetime

from dotenv import load_dotenv

from beholder_api import BeholderAPI, BEHOLDER_URL

load_dotenv()
API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    print("Error: No API_KEY given. This can be found in your Beholder SaaS profile once you've"
          + " signed up for a paid plan. Store the key in a environment variable called API_KEY"
          + " or put it into a .env file")
    sys.exit(-1)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Download a previously built model with Beholder API")
    parser.add_argument("project_name")
    parser.add_argument("-o", "--output-filename", help="Filename to write to downloaded model to")
    args = parser.parse_args()

    api = BeholderAPI(BEHOLDER_URL, API_KEY)

    projects = api.list_projects()
    project_id = None
    for p in projects:

        if p["name"] == args.project_name:
            project_id = p["id"]
            break

    if project_id is None:
        print(f"Error: Unable to find project with name {args.project_name}")
        sys.exit(-1)

    jobs = api.list_jobs()
    last_job_time = None
    last_construct_mesh_job = None
    for j in jobs:
        if j["project"] == project_id and j["type"] == "construct_mesh" and j["state"] == "CP":
            job_time = datetime.datetime.strptime(j["end_time"], "%Y-%m-%dT%H:%M:%S.%fZ")

            if last_job_time is None or job_time > last_job_time:
                last_job_time = job_time
                last_construct_mesh_job = j

    if last_construct_mesh_job is None:
        print(f"Error: Unable to find construct_mesh job for project called [{args.project_name}]")

    file_url = last_construct_mesh_job["output_data"]["mesh_data"]
    api.refresh_cookies()

    print("Downloading", file_url)
    if args.output_filename:
        print("Saving as", args.output_filename)
    api.download_file(file_url, args.output_filename)
    print("Done")