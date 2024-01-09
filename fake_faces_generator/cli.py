import pathlib

import click
from download import run


@click.command()
@click.argument(
        "data_dir",
        type=click.Path(
            exists=False,
            file_okay=False,
            dir_okay=True,
        ),
        required=True,
        )
@click.argument("n_images", type=int, required=True)
def cli(data_dir, n_images):
    """
    CLI tool to download unique images of human faces from thispersondoesnotexist.com.

    Args:
        DATA_DIR (str): Path to the directory where you'd like to store the images.

        N_IMAGES (int): Number of unique images to be generated (must be greater than 0).

    Examples:
    - To download 10 images to the 'images' directory: 
    
    $ fake_faces_generator /path/to/images 10
    """
    data_dir = pathlib.Path(data_dir)
    run(data_dir, n_images)

if __name__ == "__main__":
    cli()