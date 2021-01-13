import os
import sys
from github import Github
from datetime import datetime

def get_datetime_now():
  now = datetime.now().replace(microsecond=0)
  return now

def read_file_content(repo, filePath):
  return repo.get_contents(filePath).decoded_content.decode()

def get_last_version(repo):
  last_version = 'v0.0.0' # default first version
  if repo.get_releases().totalCount != 0:
    latestRelease = repo.get_latest_release()
    last_version = latestRelease.tag_name
  return last_version

def get_current_version(repo):
  content = read_file_content(repo, 'version.ini')
  current_version = content.replace('\n', '')
  return current_version

def get_start_date_of_latest_release(repo):
  start_date = get_datetime_now()
  if repo.get_releases().totalCount == 0:
    start_date = repo.created_at
  else:
    start_date = repo.get_latest_release().created_at
  return start_date

def get_release_name(tag_name, REPO_NAME):
  return tag_name + ' of ' + REPO_NAME

def get_release_message(repo, tag_name, REPO_NAME):
  release_message_dct = { 'main': [], 'develop': [], 'feature': []}
  release_message_str = ''
  start_date = get_start_date_of_latest_release(repo)
  pulls = get_pull_requests(repo, start_date)
  for pull in pulls:
    msg = '\n\u2022\t' + pull.title + '\t (#' + str(pull.number) + ') from head branch: ' + pull.head.ref 
    release_message_dct[pull.base.ref].append(msg)
  for baseBranch in release_message_dct:
    if len(release_message_dct[baseBranch]) != 0:
      release_message_str += '\n\n\tBase Branch -> ' + baseBranch
      for e in release_message_dct[baseBranch]:
        release_message_str += e
  format_release_message = tag_name + '\n' + 'Features added/improved in ' + REPO_NAME + ':\n\n' + 'Following are the PRs title which were merged since last release:\n' + release_message_str
  print('release msg', format_release_message)
  return  format_release_message

def get_inputs(input_name):
  return os.getenv('INPUT_{}'.format(input_name).upper())

def create_release(repo, tag_name, tag_message, release_name, release_message, is_draft, is_prerelease):  # https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html#github.Repository.Repository.create_git_tag_and_release
  branch = repo.get_branch("main")
  print(branch.commit.sha)
  tag = repo.create_git_tag(tag_name, tag_message, branch.commit.sha, 'commit')
  # tag = repo.create_git_tag(tag = tag_name, message = tag_message, type = 'commit', object = branch.commit.sha)
  ref = repo.create_git_ref('refs/tags/' + tag_name, tag.sha)
  release = repo.create_git_release(tag.tag, release_name, release_message, is_draft, is_prerelease)
  return release

def get_pull_requests(repo, start_date):
  pulls: List[PullRequest.PullRequest] = []
  try:
    for pull in repo.get_pulls(state='closed', sort='updated', direction='desc'):
      if not pull.merged_at:
        continue
      merged_dt = pull.merged_at
      updated_dt = pull.updated_at
      if merged_dt >= start_date:
        pulls.append(pull)
  except RequestException as e:
      print('Github pulls error (request)', e)
  except GithubException as e:
      print('Gihub pulls error (github)', e)
  return pulls

def compute(repo, REPO_NAME):
  current_version = get_current_version(repo)
  last_version = get_last_version(repo)
  # get_release_message(repo, current_version, REPO_NAME)

  if last_version < current_version:
    tag_name = current_version
    tag_message = 'Default'
    release_name = get_release_name(tag_name, REPO_NAME)
    release_message = get_release_message(repo, tag_name, REPO_NAME)
    is_draft = False
    is_prerelease = False
    release = create_release(repo, tag_name, tag_message, release_name, release_message, is_draft, is_prerelease)
    print('New Release is successfuly created with tag name: ', release.tag_name)
    exit
  elif last_version == current_version:
    print('The last_version is equal to the current version, So now we will create a draft release only if there is any merge since last release.')
    #     Is a new merge between main and develop, since last_release
    startDate = get_start_date_of_latest_release(repo)
    if len(get_pull_requests(repo, startDate)) != 0: # there is a new merge since last release
      if repo.get_latest_release().draft: # is last merge is a draft release
        print('The last release is a draft release. Hence, I will update_last_draft_release~~~~~~~~~~~~~~~~~~~~')
        exit
      else:
        print('new merged PRs detected. Now, I will create a new draft release.~~~~~~~~~~~~~~~~~~~')
        exit
    else:
      print('There is no new merge since last release!!!!!, action terminates here onwards')
      exit
  else:
    print('The current_version is smaller than the last version, which is not allowed, So the action terminates here onwards.')
    exit

def main():
  print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
  REPO_NAME = get_inputs('REPO_NAME')
  ACCESS_TOKEN = get_inputs('ACCESS_TOKEN')
  USER_NAME = get_inputs('USER_NAME')
  
  GH = Github(ACCESS_TOKEN)
  repo = GH.get_repo(USER_NAME + '/' + REPO_NAME)

  compute(repo, REPO_NAME)
 
if __name__ == "__main__":
    main()


# import os
# from github import Github
# import sys
# from datetime import datetime

# def get_datetime_now():
#   now = datetime.now().replace(microsecond=0)
#   return now
# def get_start_date_of_latest_release(repo):
#   startDate = get_datetime_now()
#   if repo.get_releases().totalCount == 0:
#     startDate = repo.created_at
#   else:
#     latestRelease = repo.get_latest_release()
#     startDate = latestRelease.created_at
#   return startDate
# def get_release_message(repo):
#   releaseMessage = { 'main': [], 'develop': [], 'feature': []}
#   releaseMsgStr = ''
#   startDate = get_start_date_of_latest_release(repo)
#   pulls = get_pull_requests(repo, startDate)
#   for pull in pulls:
#     log = '\n\u2022\t' + pull.title + '\t (#' + str(pull.number) + ') from head branch: ' + pull.head.ref 
#     releaseMessage[pull.base.ref].append(log)

#   for rel in releaseMessage:
#     releaseMsgStr += '\n\n\tBase Branch -> ' + rel
#     for log in releaseMessage[rel]:
#       releaseMsgStr += log
#   print('release msg', releaseMsgStr)
#   return releaseMsgStr
  
# def get_inputs(input_name):
#   return os.getenv('INPUT_{}'.format(input_name).upper())
# def create_release(repo, currentVersionTag, tagMessage, releaseName, releaseMessage, isDraft, isPrerelease):
# # https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html#github.Repository.Repository.create_git_tag_and_release
#   branch = repo.get_branch("main")
#   commitSha = branch.commit.sha
#   print('commitSha',commitSha)
#   tag = repo.create_git_tag(currentVersionTag, tagMessage, commitSha, 'commit')
#   print('tag', tag.sha)
#   ref = repo.create_git_ref('refs/tags/'+currentVersionTag, tag.sha)
#   release = repo.create_git_release(tag.tag, releaseName, releaseMessage, isDraft, isPrerelease)
#   return release
# def read_file_content(repo, filePath):
#   return repo.get_contents(filePath).decoded_content.decode().replace('\n', '')
# def get_commits(repo):
#   commits = repo.get_commits()
#   for commit in commits:
#     print(commit)
# def get_pull_requests(repo, start_date):
#   print('Began get_pull_requests()')
#   print('Total Count of pull requests that have been closed = ', repo.get_pulls(state='closed').totalCount)
#   pulls: List[PullRequest.PullRequest] = []
#   try:
#     for pull in repo.get_pulls(state='closed', sort='updated', direction='desc'):
#       if not pull.merged_at:
#         continue
#       merged_dt = pull.merged_at
#       updated_dt = pull.updated_at
# #       print(pull.title + '\t->\t' + pull.body)
# #       print('merged_dt ', merged_dt, '\nupdated_dt ', updated_dt)
# #       print('start_date',start_date)
#       if merged_dt >= start_date:
# #         print(pull.title)
#         pulls.append(pull)
#   except RequestException as e:
#       print('Github pulls error (request)', e)
#   except GithubException as e:
#       print('Gihub pulls error (github)', e)
#   return pulls

# def main():
#   print('Entered into main fun')
#   print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
#   REPO_NAME = get_inputs('REPO_NAME')
#   ACCESS_TOKEN = get_inputs('ACCESS_TOKEN')
#   USER_NAME = get_inputs('USER_NAME')
  
#   gh = Github(ACCESS_TOKEN)
#   repo = gh.get_repo(USER_NAME + '/' + REPO_NAME)
  
#   currentVersion = read_file_content(repo, 'version.ini')
#   lastVersion = 'v0.0.0' #default lastversion
#   tagMessage = 'Default Tag Message'
#   releaseName = 'Release'
#   releaseMessage = ''
#   isDraft = False
#   isPrerelease = False
  
#   if repo.get_releases().totalCount == 0:
#     print('There is no previous release, so lastVerseion is set to default - v0.0.0')
#     lastVersion = 'v0.0.0'
#   else:
#     latestRelease = repo.get_latest_release()
#     lastVersion = latestRelease.tag_name
#     print('lastVersion fetched from github tags is', lastVersion)
  
# #   print('get_release_message', get_release_message(repo))
#   if lastVersion < currentVersion:
#     releaseName = releaseName + ' ' + currentVersion + ' of ' + REPO_NAME
#     releaseMessage = currentVersion + '\n' + 'Features added/improved in ' + REPO_NAME + ':\n\n' + 'Following are the PRs title which were merged since last release:\n' + get_release_message(repo)
#     release = create_release(repo, currentVersion, tagMessage, releaseName, releaseMessage, isDraft, isPrerelease)
#     print('Creation of new Release is completed with its tag name as', release.tag_name)
#     exit
#   elif lastVersion == currentVersion:
#     print('The LastVersion is equal to the current version, So now we will create a draft release only if there is any merge since last release.')
#     #     if there is a new merge since last_release
#     startDate = get_start_date_of_latest_release(repo)
#     if len(get_pull_requests(repo, startDate)) != 0: # there is a new merge since last release
#       if repo.get_latest_release().draft:
#         print('update_last_draft_release~~~~~~~~~~~~~~~~~~~~')
# #         update_last_draft_release()
#       else:
#         print('new merged PRs detected, I will create a new draft release.~~~~~~~~~~~~~~~~~~~')
# #         isDraft = True
# #         release = repo.create_git_release( 'd0.0.1', releaseName, releaseMessage, isDraft, isPrerelease)
# #         create_release(repo, currentVersion, tagMessage, releaseName, releaseMessage, isDraft, isPrerelease)
#     else:
#       print('There is no new merge since last release!!!!!, programs terminates here onwards')
#       exit
#   elif lastVersion > currentVersion:
#     print('The currentVersion is smaller than the last version, which is not allowed, So the action terminates here onwards.')
#     exit
    
# if __name__ == "__main__":
#     main()
