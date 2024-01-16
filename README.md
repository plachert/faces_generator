# Fake Faces Generator
A simple unofficial CLI for downloading unique images of faces from [www.thispersondoesnotexist.com](https://thispersondoesnotexist.com). 

##  Description
There already exist at least two repositories for that:
1. [ThisPersonDoesNotExistAPI by David-Lor](https://github.com/David-Lor/ThisPersonDoesNotExistAPI/tree/master)
2. [Forked from ThisPersonDoesNotExistAPI repo by Alonso Silva](https://github.com/alonsosilvaallende/ThisPersonDoesNotExistAPI)

Both existing repositories appear to focus on generating a relatively small sample of images intended for test purposes. However, aiming to acquire thousands of fake images for GAN training, I developed a CLI optimized for this specific purpose. The optimization involved leveraging [aiohttp](https://docs.aiohttp.org/en/stable/) and implementing backoff strategies. By tweaking the parameters e.g. concurrency limit or the parameters of backoff policy I was able to download 10k unique images in less than an hour. 

## Version 0.1.1
- Tracking file (seen.pkl) is always saved (even when an error occurs). 

## Installing
Run the following command in your virtual env.

```shell
pip install git+https://github.com/plachert/fake-faces-generator
```

Verify installation:
```shell
(venv) foo@bar:~$ python
>>> import fake_faces_generator
>>> fake_faces_generator.__version__
'0.1.1'
>>>
```

## How to use
Run the following command to generate 100 images in `./generated_faces` (the directory will be created, you can provide any existing or non existing directory):
```shell
(venv) foo@bar:~$ fake_faces_generator ./generated_faces 100
```


## Licence

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/plachert/activation_tracker/blob/main/LICENSE)