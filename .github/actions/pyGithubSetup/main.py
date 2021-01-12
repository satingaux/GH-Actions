import os
from github import Github
import sys
from datetime import datetime

def get_datetime_now():
  now = datetime.now().replace(microsecond=0)
  return now
def get_release_message(repo):
  releaseMessage = ''
  startDate = get_datetime_now()
  endDate = get_datetime_now()
  if repo.get_releases().totalCount == 0:
    startDate = repo.created_at
  else:
    latestRelease = repo.get_latest_release()
    startDate = latestRelease.created_at
  pulls = get_pull_requests(repo, startDate, endDate, 100)
  for pull in pulls:
    releaseMessage = releaseMessage + pull.title + '\n'
  return releaseMessage
  
def get_inputs(input_name):
  return os.getenv('INPUT_{}'.format(input_name).upper())
def createRelease(repo, currentVersionTag, tagMessage, releaseName, releaseMessage, isDraft, isPrerelease):
# https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html#github.Repository.Repository.create_git_tag_and_release
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
def get_commits(repo):
  commits = repo.get_commits()
  for commit in commits:
    print(commit)
def get_pull_requests(repo, start_date, end_date, max_pull_requests):
  print('Began get_pull_requests()')
  print('Total Count of pull requests that have been closed = ', repo.get_pulls(state='closed').totalCount)
  pulls: List[PullRequest.PullRequest] = []
  pulls_str = ''
  try:
    for pull in repo.get_pulls(state='closed', sort='updated', direction='desc'):
      if not pull.merged_at:
        continue
      merged_dt = pull.merged_at
      updated_dt = pull.updated_at
#       merged_dt = dtutil.UTC_TZ.localize(pull.merged_at)
#       updated_dt = dtutil.UTC_TZ.localize(pull.updated_at)
      print('merged_dt', pull.merged_at, 'updated_dt', pull.updated_at)
      print('start_date',start_date,'end_date',end_date)
      if merged_dt < start_date:
        print(pull.title)
        pulls_str += pull.title
        pulls.append(pull)
#       if merged_dt > end_date:
#         continue
#       if updated_dt < start_date:
#         return pulls
      
#       if len(pulls) >= max_pull_requests:
#         return pulls
  except RequestException as e:
      print('Github pulls error (request)', e)
  except GithubException as e:
      print('Gihub pulls error (github)', e)
  return pulls

def main():
  print('Entered into main fun')
  print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
  REPO_NAME = get_inputs('REPO_NAME')
  ACCESS_TOKEN = get_inputs('ACCESS_TOKEN')
  USER_NAME = get_inputs('USER_NAME')
  
  gh = Github(ACCESS_TOKEN)
  repo = gh.get_repo(USER_NAME + '/' + REPO_NAME)
  
  currentVersion = read_file_content(repo, 'version.ini')
  lastVersion = 'v0.0.0' #default lastversion
  tagMessage = 'Default Tag Message'
  releaseName = 'Default Release Name'
  releaseMessage = 'Release Message as the list of all the PRs title ' + get_release_message(repo)
  isDraft = False
  isPrerelease = False
  print('get_release_message(repo):', get_release_message(repo))
  
  
  
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
  elif lastVersion == currentVersion:
    print('The LastVersion is equal to the current version, So the action terminates here onwards.')
    exit
  elif lastVersion > currentVersion:
    print('The currentVersion is smaller than the last version, which is not allowed, So the action terminates here onwards.')
    exit
    
if __name__ == "__main__":
    main()
