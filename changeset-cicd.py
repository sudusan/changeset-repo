import boto3
import os
import shutil
import zipfile
import json
from botocore.vendored import requests

def cleanup():
  # Cleans up tmp dir
  os.chdir('/tmp')
  for i in os.listdir("."):
      if os.path.isfile(i):
          os.remove(i)
      elif os.path.isdir(i):
          shutil.rmtree(f'/tmp/{i}')
  print(f'Cleaned up! tmp dir: {os.listdir("/tmp")}')


def clone_repo(branch):

  url = f"{os.environ['REPO_URL']}/zipball/{branch}"
  git_user = os.environ['GIT_USER']
  git_password = os.environ['GIT_PASSWORD']
  local_file = '/tmp/repo.zip'

  r = requests.get(url, auth=(git_user, git_password))

  # Write to file
  with open(local_file, 'wb') as fp:
      fp.write(r.content)

  return local_file


def unzip_repo(file_path):

  extract_path = '/tmp/isoc-repo'

  # Unzip it
  with zipfile.ZipFile(file_path, 'r') as zip_ref:
      zip_ref.extractall(extract_path)

  # Get the name of the extracted dir
  dir_name = os.listdir(extract_path)[0]

  # Return the full path for the extracted file
  return f'{extract_path}/{dir_name}'


def copy_buildspec(root_dir):

  content = f
  file = 'buildspec.yml'
  with open(f'{root_dir}/{file}', 'w') as fp:
      fp.write(content)
  script = f
  file = 'params.py'
  with open(f'{root_dir}/{file}', 'w') as fp:
      fp.write(script)

def zip_dir(root_dir):

  path = '/tmp/files'
  shutil.make_archive(path, 'zip', root_dir)

  return f'{path}.zip'


def upload_s3_file(bucket, local_path, final_fname):

  s3 = boto3.client('s3')
  s3.upload_file(local_path, bucket, final_fname)
  print('Successfully uploaded!')
  return final_fname


def getrepo(bucket, branch):

  # Clean up /tmp dir
  cleanup()

  # Clone branch
  repo_path = clone_repo(branch)

  # Unzip the repo in /tmp/repo
  unzip = unzip_repo(repo_path)

  # Copy the buildscpec file to the repo's root dir
  copy_buildspec(unzip)

  # Zip it back
  zipped_file = zip_dir(unzip)

  # Uploads it to s3
  upload_s3_file(bucket, zipped_file, 'files.zip')

def lambda_handler(event, context):
  getrepo(os.environ['S3BUCKET'], 'IAC')