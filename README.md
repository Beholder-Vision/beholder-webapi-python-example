## Beholder WebAPI Python Example

This repo gives an example of how to use the Beholder Vision SaaS Web API (https://beholder.vision)
to build a 3D models from photos using Photogrammetry.

You can view documentation for the REST API at https://beholder.vision/docs/ (need to be logged in to view)

### Python Setup

Setup a Python environment (venv etc) with requests installed

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Provide your API key

An API key is required to make use of the Beholder SaaS web API. You can find your API key in
the profile section of the Beholder Vision website once you've signed up for a paid plan.

Copy the API key and set it as an environment variable called API_KEY. This can be done by using the
set/export shell command or by copying .env.template, renaming it to be .env and putting your API 
key in there.

### Building a 3D model

To build a 3D model you'll need a set of photos of the object you want to build. To build a 3D model
of an object you'll need at least 20 photos of that object, taken in a ring around the object with good
overlap between each photo. To improve the quality of your output model the general rule of thumb is 
to use more photos of higher quality, i.e. increase the resolution of the photos and/or use a tripod
when taking them.

If you don't have any photos to hand then you can get a known good dataset at https://beholder.vision/data/tutorials/getting-started/lion.zip

Put the images in a folder and run the build_model.py script

```
python build_model.py IMAGES_DIR
```

Extra options let you set the project name or delete any pre-existing project. To view the help run

```
python build_model.py --help
```

The build_model.py script will upload the images to the Beholder Vision SaaS, use them to build a
model and then download that model as a .glb file.

### Downloading the 3D model

After the build_model.py script has finished building a model it will download it. You can also download
models from projects built earlier on by using the download_model.py script. Usage for that script is.

```
python download_model.py PROJECT_NAME
```

### Problems?

If you run into an issue with this example code then in the first instance please open an issue in this 
repository. Alternatively you can send an email to [support@beholder.vision](mailto:support@beholder.vision).