#!/usr/bin/python
'''
Command line tool to get/create branch name by GitHub issue number.

@author: ekondrashev
'''
import argparse
import base64
import json
import subprocess
import urllib2
from collections import namedtuple
from getpass import getpass

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--issue', type=int)
parser.add_argument('-o', '--owner')
parser.add_argument('-r', '--repo')
parser.add_argument('-u', '--user', default='ekondrashev')
parser.add_argument('-c', '--create', default=False)


class GitHub(object):
    Account = namedtuple('Account', 'name password')
    Repo = namedtuple('Repo', 'name owner')
    Issue = namedtuple('Issue', 'nr title body')

    def __init__(self, repo, account):
        self.repo = repo
        self.account = account

    def issue(self, nr):
        base64string = base64.encodestring(
            '%s:%s' % (self.account.name, self.account.password))\
            .replace('\n', '')
        url = 'https://api.github.com/repos/%s/%s/issues/%d' % (
            self.repo.owner, self.repo.name, nr)
        request = urllib2.Request(url)
        request.add_header("Authorization", "Basic %s" % base64string)
        result = json.loads(urllib2.urlopen(request).read())
        return self.Issue(nr, result['title'], result['body'])


def branch_name_by_issue(issue):
    return '%d_%s' % (issue.nr, issue.title.replace(' ', '_').lower())


class Git(object):

    class Branch(object):
        def __init__(self, name):
            self.name = name

        def co(self, create=False):
            cmdline = ['git', 'checkout']
            if create:
                cmdline.append('-b')
            cmdline.append(self.name)
            print subprocess.check_output(cmdline)

    def pull(self, rebase=True):
        cmdline = ['git', 'pull']
        if rebase:
            cmdline.append('--rebase')
        print subprocess.check_output(cmdline)

    def st(self):
        print subprocess.check_output('git st'.split())

    def dirty(self):
        return len(subprocess.check_output(
            'git status --porcelain'.split()).strip()) > 0


def main(args):
    repo = GitHub.Repo(args.repo, args.owner)
    account = GitHub.Account(
        args.user,
        getpass('Password: ')
     )
    github = GitHub(repo, account)
    issue = github.issue(args.issue)
    branch = Git.Branch(branch_name_by_issue(issue))
    print 'Branch name: ', branch.name
    if args.create:
        git = Git()
        if git.dirty():
            print 'There are changes done to the repo, commit/reset first'
            return
        Git.Branch('master').co()
        git.pull()
        git.st()
        branch.co(create=True)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
