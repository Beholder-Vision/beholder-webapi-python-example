
import os.path
import requests
import shutil

BEHOLDER_URL = "https://beholder.vision"

# You can view documentation for the REST API at https://beholder.vision/docs/ (need to be logged in)
class BeholderAPI:

    def __init__(self, beholder_url, auth_token):
        self._session = requests.Session()
        self._session.headers.update({ "Authorization": f"Bearer {auth_token}" })
        self._beholder_url = beholder_url

    def _check_response(self, response):
        if not response.ok:
            raise Exception(f"Request failed. Got response of [{response.status_code}] and [{response.text}]")

    def get(self, url):
        response = self._session.get(url)
        self._check_response(response)
        return response
    
    def delete(self, url):
        response = self._session.delete(url)
        self._check_response(response)
        return response
    
    def post(self, url, data=None):
        response = self._session.post(url, data=data)
        self._check_response(response)
        return response
    
    def put(self, url, data=None):
        response = self._session.put(url, data=data)
        self._check_response(response)
        return response
    
    def download_file(self, url, filename=None):
        """
        In order to download an image or model from Beholder the following cookies must be set,
        CloudFront-Policy, CloudFront-Signature and CloudFront-Key-Pair-Id. The can be obtained
        by calling refresh_cookies.
        """

        if filename is None:
            filename = os.path.basename(url)

        with self._session.get(url, stream=True) as response:
            with open(filename, "wb") as output_file:
                shutil.copyfileobj(response.raw, output_file)

    def get_current_user_data(self):
        response = self.get(self._beholder_url + "/core/api/currentuser")
        return response.json()

    def list_projects(self):
        response = self.get(self._beholder_url + "/core/api/projects")
        return response.json()

    def delete_project(self, project_id):
        response = self.delete(self._beholder_url + "/core/api/projects/{project_id}")
        return response.json()

    def create_project(self, project_name):
        data = {
            "name": project_name,
        }
        response = self.post(self._beholder_url + "/core/api/projects", data=data)
        return response.json()

    def upload_image_data(self, filename, filedata):
        response = self.put(self._beholder_url + f"/core/api/internal_input_data/{filename}", data=filedata)
        return response.json()

    def create_input_image(self, project_id, image_name, image_path):
        data = {
            "project": project_id,
            "name": image_name,
            "path": image_path,
        }
        response = self.post(self._beholder_url + "/core/api/input_images", data=data)
        return response.json()

    def delete_input_image(self, input_image_id):
        response = self.delete(self._beholder_url + f"/core/api/input_images/{input_image_id}")
        return response.json()

    def list_jobs(self):
        response = self.get(self._beholder_url + "/core/api/jobs")
        return response.json()

    def create_job(self, project_id, job_type, max_approved_credits):
        data = {
            "project": project_id,
            "job_type": job_type,
            "max_approved_credits": max_approved_credits,
        }
        response = self.post(self._beholder_url + "/core/api/jobs", data=data)
        return response.json()

    def get_job(self, job_id):
        response = self.get(self._beholder_url + f"/core/api/jobs/{job_id}")
        return response.json()

    def refresh_cookies(self):
        self._session.get(self._beholder_url + "/core/api/refresh_cookies")

        #print(self._session.cookies)

