import argparse
import os
import os.path
import sys
import time

from dotenv import load_dotenv

from beholder_api import BeholderAPI, BEHOLDER_URL

SUPPORTED_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]

load_dotenv()
API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    print("Error: No API_KEY given. This can be found in your Beholder SaaS profile once you've"
          + " signed up for a paid plan. Store the key in a environment variable called API_KEY"
          + " or put it into a .env file")
    sys.exit(-1)

def filter_filenames_by_extension(filename_list, supported_extensions):

    output_list = []
    for filename in filename_list:
        ext_idx = filename.rfind(".")
        if ext_idx >= 0:
            ext = filename[ext_idx+1:].lower()
            if ext in supported_extensions:
                output_list.append(filename)

    return output_list

def get_image_filenames(image_dirname):

    dir_contents = [os.path.join(image_dirname, f) for f in os.listdir(image_dirname)]
    dir_files = [f for f in dir_contents if os.path.isfile(f)]

    return filter_filenames_by_extension(dir_files, SUPPORTED_IMAGE_EXTENSIONS)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Build a model with Beholder API")
    parser.add_argument("image_dirname", help="The directory to load images from")
    parser.add_argument("-p", "--project-name", help="Name for the project. Defaults to the last part of the image dirname")
    parser.add_argument("-d", "--delete-existing-projects", action="store_true",
                        help="Delete any existing projects before starting")
    args = parser.parse_args()
    image_dirname = args.image_dirname.rstrip("/").rstrip("\\")
    project_name = args.project_name
    if project_name is None:
        project_name = os.path.basename(image_dirname)

    api = BeholderAPI(BEHOLDER_URL, API_KEY)
    user_data = api.get_current_user_data()

    if args.delete_existing_projects:
        # Delete any existing projects with those names
        projects = api.list_projects()
        for p in projects:

            if p["name"] == project_name:
                print(f"Deleting existing [{p['name']}] project")
                api.delete_project(p["id"])

    # Create the project and uploading images
    print(f"Creating project [{project_name}]")
    project_info = api.create_project(project_name)

    image_filenames_to_upload = get_image_filenames(image_dirname)

    print(f"Uploading [{len(image_filenames_to_upload)}] images")

    for image_filename in image_filenames_to_upload:
        with open(image_filename, "rb") as image_file:
            image_data = image_file.read()

            # First upload the image
            base_image_name = os.path.basename(image_filename)
            image_upload_name = f"{user_data['username']}/{project_info['id']}/{base_image_name}"
            upload_response = api.upload_image_data(image_upload_name, image_data)

            # Then link it to the project
            api.create_input_image(project_info['id'], base_image_name, upload_response["path"])

    # Run image alignment and construct mesh jobs
    print(f"Running image alignment for [{project_name}]")
    job = api.create_job(project_info["id"], "align_images", max_approved_credits=1000000)
    job_id = job["id"]

    finished = False
    while not finished:
        job = api.get_job(job_id)
        if job["state"] != "ST":
            finished = True
            if job["state"] == "ER":
                print(f"Error: Job [{job_id}] for [{project_name}] has failed with an error")
                sys.exit(-1)
        
        time.sleep(1)

    print(f"Running construct mesh job for for [{project_name}]")
    job = api.create_job(project_info["id"], "construct_mesh", max_approved_credits=1000000)
    job_id = job["id"]

    finished = False
    while not finished:
        job = api.get_job(job_id)
        if job["state"] != "ST":
            finished = True
            if job["state"] == "ER":
                print(f"Error: Job [{job_id}] for [{project_name}] has failed with an error")
                sys.exit(-1)
        
        time.sleep(1)

    if job["state"] == "CP":
        file_url = job["output_data"]["mesh_data"]
        api.refresh_cookies()

        print("Downloading", file_url)
        api.download_file(file_url)
        print("Done")