# -*- coding: utf-8 -*-

import click
import logging



@click.command()
def main(args=None):
    logging.setBasicConfig(level=logging.INFO)
    """Console script for root2hdf5"""
    click.echo("Replace this message by putting your code into "
               "root2hdf5.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    from converters import *
    for _file in args:
      pass


if __name__ == "__main__":
  files = os.listdir('./dl')
  exclude = []#['eminus_test.root']
  for _file in files:
    if _file in exclude:
      continue
    try:
      convert_file(_file)
    except Exception as e:
      print "COULD NOT CONVERT FILE: ",_file
      print e

if __name__ == "__main__":
    main()
