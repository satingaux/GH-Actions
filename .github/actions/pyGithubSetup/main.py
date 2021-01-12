import os
from github import Github
import sys

def get_inputs(input_name):
  return os.getenv('INPUT_{}'.format(input_name).upper())
def createRelease(repo, currentVersionTag, tagMessage, releaseName, releaseMessage, isDraft, isPrerelease):
  branch = repo.get_branch("main")
  commitSha = branch.commit.sha
  print('commitSha',commitSha)
  tag = repo.create_git_tag(currentVersionTag, tagMessage, commitSha, 'commit')
  print('tag', tag.sha)
  ref = repo.create_git_ref('refs/tags/'+currentVersionTag, tag.sha)
  release = repo.create_git_release(tag.tag, releaseName, releaseMessage, isDraft, isPrerelease)
  return release
def read_file_content(repo, filePath):
  return repo.get_contents(filePath).decoded_content.decode().replace('\n', '')

def main():
  print('Entered into main fun')
  print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
  REPO_NAME = get_inputs('REPO_NAME')
  CUR_VERSION = get_inputs('CUR_VERSION')
  ACCESS_TOKEN = get_inputs('ACCESS_TOKEN')
  USER_NAME = get_inputs('USER_NAME')

  currentVersion = CUR_VERSION.replace('\n','')
  lastVersion = 'v0.0.0' #default lastversion
  tagMessage = 'Default Tag Message'
  releaseName = 'Default Release Name'
  releaseMessage = 'Release Message'
  isDraft = False
  isPrerelease = False
  target_commitish = 'target_commitish'
  

  gh = Github(ACCESS_TOKEN)
  repo = gh.get_repo(USER_NAME + '/' + REPO_NAME)
  labels = repo.get_labels()
  
  #   read version.ini file
  file_content = read_file_content(repo, 'version.ini')
  print('VVVVVVVVVVVVVVVVVVVVVVVersion file: ', file_content,'~~~~~~')
  
  if repo.get_releases().totalCount == 0:
    print('There is no previous release, so lastVerseion is set to default - v0.0.0')
    lastVersion = 'v0.0.0'
  else:
    latestRelease = repo.get_latest_release()
    lastVersion = latestRelease.tag_name
    print('lastVersion fetched from github tags is', lastVersion)


  if lastVersion < currentVersion:
    release = createRelease(repo, currentVersion, tagMessage, releaseName, releaseMessage, isDraft, isPrerelease)
    print('Creation of new Release is completed with its tag name as', release.tag_name)
    #   https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html#github.Repository.Repository.create_git_tag_and_release
  elif lastVersion == currentVersion:
    print('The LastVersion is equal to the current version, So the action terminates here onwards.')
    exit
  elif lastVersion > currentVersion:
    print('The currentVersion is smaller than the last version, which is not allowed, So the action terminates here onwards.')
    exit

  print(REPO_NAME, USER_NAME, CUR_VERSION, ACCESS_TOKEN)



  
if __name__ == "__main__":
    main()
 
# REPO_NAME = get_inputs('REPO_NAME')
# CUR_VERSION = get_inputs('CUR_VERSION')
# ACCESS_TOKEN = get_inputs('ACCESS_TOKEN')
# USER_NAME = get_inputs('USER_NAME')

# currentVersion = CUR_VERSION.replace('\n','')
# lastVersion = 'v0.0.0' #default lastversion
# tagMessage = 'Default Tag Message'
# releaseName = 'Default Release Name'
# releaseMessage = 'Release Message'
# isDraft = False
# isPrerelease = False
# target_commitish = 'target_commitish'

# gh = Github(ACCESS_TOKEN)
# repo = gh.get_repo(USER_NAME + '/' + REPO_NAME)
# labels = repo.get_labels()
# print('repo.get_releases()',)
# if repo.get_releases().totalCount == 0:
#   print('There is no previous release, so lastVerseion is set to default - v0.0.0')
#   lastVersion = 'v0.0.0'
# else:
#   latestRelease = repo.get_latest_release()
#   lastVersion = latestRelease.tag_name
#   print('lastVersion fetched from github tags is', lastVersion)
  
  
# if lastVersion < currentVersion:
#   branch = repo.get_branch("main")
#   commitSha = branch.commit.sha
#   print('commitSha',commitSha)
#   tag = repo.create_git_tag(currentVersion, tagMessage, commitSha, 'commit')
#   print('tag',tag.sha)
#   ref = repo.create_git_ref('refs/tags/'+currentVersion, tag.sha)
#   release = repo.create_git_release(tag.tag, releaseName,releaseMessage, isDraft, isPrerelease)
#   print('Creation of new Release is completed with its tag name as', release.tag_name)
#   #   https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html#github.Repository.Repository.create_git_tag_and_release
# elif lastVersion == currentVersion:
#   print('The LastVersion is equal to the current version, So the action terminates here onwards.')
#   exit
# elif lastVersion > currentVersion:
#   print('The currentVersion is smaller than the last version, which is not allowed, So the action terminates here onwards.')
#   exit
  
# print(REPO_NAME, USER_NAME, CUR_VERSION, ACCESS_TOKEN)
