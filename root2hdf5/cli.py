# -*- coding: utf-8 -*-

import click
import logging
import sys


@click.command()
@click.argument('file', nargs=-1)
def main(files=None):
    logging.basicConfig(level=logging.INFO)
    if files == None:
      click.echo("usage: root2hdf5 --src filename.root [filename.root [...]]")
      sys.exit(0)
    from root2hdf5.converters.larcv_file import LArCVFile
    LArCVFile(files).setup().go()

if __name__ == "__main__":
    main()
