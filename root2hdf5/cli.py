# -*- coding: utf-8 -*-

import click
import logging
import sys

@click.command()
def main(args=None):
    logging.basicConfig(level=logging.INFO)
    if args == None:
      click.echo("usage: root2hdf5 filename.root [filename.root [...]]")
      sys.exit(0)
    from root2hdf5.converters.larcv_file import LArCVFile
    LArCVFile(args).setup().go()

if __name__ == "__main__":
    main()
