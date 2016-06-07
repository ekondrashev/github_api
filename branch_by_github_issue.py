#!/usr/bin/python
'''
Command line tool to get branch name by github issue number.

@author: ekondrashev
'''
import argparse
import base64
import json
import urllib2
from collections import namedtuple
from getpass import getpass

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--issue', type=int)
parser.add_argument('-o', '--owner')
parser.add_argument('-r', '--repo')
parser.add_argument('-u', '--user', default='ekondrashev')
parser.add_argument('-v', '--verbose', default=True)


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


if __name__ == "__main__":
    args = parser.parse_args()
    repo = GitHub.Repo(args.repo, args.owner)
    account = GitHub.Account(
        args.user,
        getpass('Password: ')
     )
    github = GitHub(repo, account)
    issue = github.issue(args.issue)
    print branch_name_by_issue(issue)
