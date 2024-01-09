# Fake Faces Generator
A simple unofficial CLI for downloading unique images of faces from [www.thispersondoesnotexist.com](https://thispersondoesnotexist.com). 

##  Description
There already exist at least two repositories for that:
1. [ThisPersonDoesNotExistAPI by David-Lor](https://github.com/David-Lor/ThisPersonDoesNotExistAPI/tree/master)
2. [Forked from ThisPersonDoesNotExistAPI repo by Alonso Silva](https://github.com/alonsosilvaallende/ThisPersonDoesNotExistAPI)

However, they both seem to aim at generating a rather small sample of images for test purposes. Since I wanted to get thousands of fake images for training GANs, I created a CLI that is optimized for that. I optimized the process by using [aiohttp](https://docs.aiohttp.org/en/stable/) and backoff strategies. By tweaking the parameters e.g. concurrency limit or the parameters of backoff policy I was able to download 10k unique images in less than an hour. 

## Installing
Run the following command in your virtual env.

```shell
(venv) foo@bar:~$ pip install git+https://github.com/plachert/fake-faces-generator
```

Verify installation:
```shell
(venv) foo@bar:~$ python
>>> import fake_faces_generator
>>> fake_faces_generator.__version__
'0.1.0`
>>>
```

## How to use
Run the following command to generate 100 images in `./generated_faces` (the directory will be created, you can provide any existing or non existing directory):
```shell
(venv) foo@bar:~$ fake_faces_generator ./generated_faces 100
```


## Licence

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/plachert/activation_tracker/blob/main/LICENSE)