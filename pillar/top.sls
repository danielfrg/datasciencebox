#!py
import os

def run():
  '''
  Returns all the pillars in this directory if they exists
  Right now it only handles one level of depth
  '''
  pillar_dir = os.path.dirname(os.path.realpath(__file__))

  matches = []
  for pillar_file in os.listdir(pillar_dir):
    if not pillar_file.startswith('.'):
      pillar, ext = os.path.splitext(pillar_file)
      if ext == '.sls' or ext == '':
        matches.append(pillar)
  return {'base': {'*': matches}}

def is_available(pillar_path, pillar_name):
  if os.path.isfile(os.path.join(pillar_path, pillar_name + ".sls")):
    return True
  if os.path.isfile(os.path.join(pillar_path, pillar_name, 'init.sls')):
    return True
  return False
