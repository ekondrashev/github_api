# What it is about

This repository is an effort to wrap GitHub REST API into something OOP based.

Additionally, there is logic available, that is able to compose git branch name by GItHub issue number, team and repo.
Please see `branch_by_github_issue.py` for details.


# Coming next

Cmdline tool to create PR by branch name.

# Usage

## branch_by_github_issue.py

`branch_by_github_issue.py -o teamed -r xockets-xjm -i 737 -u ekondrashev`

where
`-o` is an owner of a repo
`-r` is a repo name
`-i` is issue number
`-u` account name to access the GitHub, optional for public repos