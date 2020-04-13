from urllib import request
from json import loads
from tabulate import tabulate


class Repo(object):
    def __init__(self, name, pulls, description):
        self._name = name
        self._pulls = pulls
        self._description = description
        self._count = 'nan'
        self._images = []

    @property
    def name(self):
        return self._name

    @property
    def pulls(self):
        return self._pulls

    @property
    def description(self):
        return self._description

    @property
    def count(self):
        return self._count

    @property
    def images(self):
        return self._images

    def load(self):
        data = loads(request.urlopen('https://hub.docker.com/v2/repositories/ghdl/%s/tags/?page_size=100' % self._name).read())
        if data["next"]:
            raise Exception("'next' not None!")
        self._count = data["count"]
        for tag in data["results"]:
            img = tag["images"][0]
            self._images += [Image(
                tag["name"],
                '%.2f' % (img["size"]/1024**2),
                img["digest"][7:],
                tag["last_updated"]
            )]

    def to_tab(self):
        return [[img.name, img.size, img.digest, img.last_updated] for img in self._images]


class Image(object):
    def __init__(self, name, size, digest, last_updated):
        self._name = name
        self._size = size
        self._digest = digest
        self._last_updated = last_updated

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    @property
    def digest(self):
        return self._digest

    @property
    def last_updated(self):
        return self._last_updated


def get_repos():
    """
    Retrieve list of 'ghdl' repositories from hub.docker.com through the v2 API
    """
    d = loads(request.urlopen('https://hub.docker.com/v2/repositories/ghdl').read())
    if d["next"]:
        raise Exception("'next' not None!")
    return [Repo(
        f["name"],
        f["pull_count"],
        f["description"]
    ) for f in d["results"]]


def get_all_registry_info():
    """
    Retrieve list of 'ghdl' repositories, and details about all the tags from hub.docker.com through the v2 API
    """
    repo_list = get_repos()
    for repo in repo_list:
        print("Get '%s' info" % repo.name)
        repo.load()
    return repo_list


def print_repos(repo_list):
    """
    Print image repositories to stdout as a tables
    """
    print(tabulate(
        [[repo.name, repo.pulls, repo.description] for repo in repo_list],
        headers=["name", "pull count", "description"]
    ))


def print_tags(repo_list):
    """
    Print all image tags to stdout as a table
    """
    data = []
    for repo in repo_list:
        data += [['> %s [%d]' % (repo.name, repo.count), "", "", ""]] + repo.to_tab() + [[]]
    print(tabulate(
        data,
        headers=["tag", "size (MB)", "digest", "last updated"]
    ))
