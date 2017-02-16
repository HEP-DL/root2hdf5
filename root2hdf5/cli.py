# -*- coding: utf-8 -*-

import click
import logging
import sys

@click.command()
def main(args=None):
    logging.setBasicConfig(level=logging.INFO)
    if args == None:
      cick.echo("Please Supply Filenames to Convert")
    from root2hdf5.converters.larcv_file import LArCVFile
    LArCVFile(args).setup().go()

if __name__ == "__main__":
    main()
