# -*- coding: utf-8 -*-

import click
import logging
import sys
from root2hdf5.framework.driver import process

@click.command()
@click.argument('driver', nargs=1)
@click.argument('files', nargs=-1)
def main(driver="",files=None):
  logging.basicConfig(level=logging.INFO)
  if len(files) == 0:
    click.echo("usage: root2hdf5 --src filename.root [filename.root [...]]")
    sys.exit(0)
  process(driver, files)

if __name__ == "__main__":
    main()
