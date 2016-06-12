#!/usr/bin/python
'''
Command line tool to get/create branch name by GitHub issue number.

@author: ekondrashev
'''
import argparse
import base64
import json
import re
import subprocess
import sys
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
    return '%d_%s' % (issue.nr, re.sub(r'[.,\-\s:]', '_', issue.title)
	.strip('_').lower())


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
    if args.create and query_yes_no('Would you like to create the branch?'):
        git = Git()
        if git.dirty():
            print 'There are changes done to the repo, commit/reset first'
            return
        Git.Branch('master').co()
        git.pull()
        git.st()
        branch.co(create=True)

import sys

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
