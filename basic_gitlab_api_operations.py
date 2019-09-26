"""
Basic git lab GET operations using gitlab APIs and python

Supports :

1. user id based on user name upon object creation
2. user projects
3. project id based on project name
4. branches based on project name
5. project files based on project id
6. file content based on project id and file path

"""
import functools
import sys

import requests

if sys.version_info.major == 3:
    import urllib.parse as parser
else:
    import urllib as parser


def handle_exception(function):
    """

    :param function:
    :return:
    """

    @functools.wraps(function)
    def func(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as exe:
            return {"function": function.__name__, "message": exe}

    return func


class ErrorHandler(type):
    """

    """

    def __new__(mcs, name, bases, dct):
        """

        :param name:
        :param bases:
        :param dct:
        :return:
        """
        for m in dct:
            if hasattr(dct[m], '__call__'):
                dct[m] = handle_exception(dct[m])
        return type.__new__(mcs, name, bases, dct)


class GitLab:
    """
    GitLab GET APIs operations
    """
    __metaclass__ = ErrorHandler

    def __init__(self, user_name, access_token):
        self._user_name = user_name
        self._access_token = access_token
        self._user_id = None
        self._api_url = "https://gitlab.com/api/v4/"

    @property
    def user_name(self):
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        self._user_name = user_name

    @user_name.deleter
    def user_name(self):
        del self._user_name

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, access_token):
        self._access_token = access_token

    @access_token.deleter
    def access_token(self):
        del self._access_token

    @property
    def api_url(self):
        return self._api_url

    @property
    def user_id(self):
        return self._user_id

    def __repr__(self):
        return {"user_name": self._user_name, "access_token": self._access_token}

    def __str__(self):
        return "Auth(user_name= {0}, access_token= {1})".format(self.user_name, self.access_token)

    def get_user_id(self):
        """
        Gets user id based on the given user_name upon object creation
        :return: user id of type int
        """
        api = self.api_url + "user"
        url = api
        headers = {
            'Private-Token': self.access_token,
            "Content-Type": "application/json"
        }
        data = requests.get(url=url, headers=headers)
        if data.ok:
            data = data.json()
            self._user_id = data["id"]
        else:
            self._user_id = data.json()

        return self._user_id

    def get_user_projects(self):
        """
        Gets projects related to user based on user id
        :return: array of dictionaries containing project details
        """
        if not self.user_id:
            self.get_user_id()
        if type(self.user_id).__name__ == "dict":
            return self.user_id
        projects = []
        page = 1
        api = self.api_url + "users/{0}/projects?page_size=100&page={1}"
        headers = {
            'Private-Token': self.access_token,
            "Content-Type": "application/json"
        }
        while True:
            url = api.format(self.user_id, page)
            data = requests.get(url=url, headers=headers)
            if data.ok:
                data = data.json()
            else:
                break
            if data:
                projects += data
            else:
                break
            page += 1

        return projects

    def get_project_id(self, project_name):
        """
        Gets project id based on project name
        :param project_name: string containing project name
        :return: project id of type integer
        """
        if not self.user_id:
            self.get_user_id()
        if type(self.user_id).__name__ == "dict":
            return self.user_id
        project_id = None
        page = 1
        api = self.api_url + "users/{0}/projects?search={1}&page_size=100&page={2}"
        headers = {
            'Private-Token': self.access_token,
            "Content-Type": "application/json"
        }
        while not project_id:
            url = api.format(self.user_id, project_name, page)
            data = requests.get(url=url, headers=headers)
            if data.ok:
                data = data.json()
            else:
                break
            if not data:
                break
            data_len = len(data)
            if data_len == 1:
                if data[0]["name"] == project_name:
                    project_id = data[0]["id"]
                    break
            else:
                for i in range(-(data_len // 2)):
                    if data[i]["name"] == project_name:
                        project_id = data[i]["id"]
                        break
                    if data[data_len - i]["name"] == project_name:
                        project_id = data[data_len - i]["id"]
                        break
            page += 1

        return project_id

    def get_branches(self, project_id):
        """
        Gets branches based on the project id
        :param project_id: integer containing project id
        :return: array of dictionaries containing branch details
        """
        if not self.user_id:
            self.get_user_id()
        if type(self.user_id).__name__ == "dict":
            return self.user_id
        branches = []
        page = 1
        api = self.api_url + "projects/{0}/repository/branches?page_size=100&page={1}"
        headers = {
            'Private-Token': self.access_token,
            "Content-Type": "application/json"
        }
        while True:
            url = api.format(project_id, page)
            data = requests.get(url=url, headers=headers)
            if data.ok:
                data = data.json()
            else:
                break
            if data:
                branches += data
            else:
                break
            page += 1

        return branches

    def get_all_project_files(self, project_id, branch="master"):
        """
        Gets files related to the project id
        :param project_id: integer containing project id
        :param branch: string containing the branch name from which the files are to be fetched
        :return: array of dictionaries containing details regarding project files
        """
        if not self.user_id:
            self.get_user_id()
        if type(self.user_id).__name__ == "dict":
            return self.user_id
        project_files = []
        page = 1
        api = self.api_url + "projects/{0}/repository/tree?ref={1}&recursive=1&per_page=100&page={2}"
        headers = {
            'Private-Token': self.access_token,
            "Content-Type": "application/json"
        }
        while True:
            url = api.format(project_id, branch, page)
            data = requests.get(url=url, headers=headers)
            if data.ok:
                data = data.json()
            else:
                break
            if data:
                project_files += data
            else:
                break
            page += 1

        return project_files

    def get_project_files(self, project_id, path, branch="master"):
        """
        Gets files related to the project id and path
        :param path: string containing path from which files are to be retrieved
        :param project_id: integer containing project id
        :param branch: string containing the branch name from which the files are to be fetched
        :return: array of dictionaries containing details regarding project files
        """
        if not self.user_id:
            self.get_user_id()
        if type(self.user_id).__name__ == "dict":
            return self.user_id
        project_files = self.get_all_project_files(project_id=project_id, branch=branch)

        files = []
        path = path.strip("/")
        path_len = len(path)
        for file in project_files:
            if file["type"] == "blob" and file["path"][:path_len] == path:
                files.append(file)

        return files

    def get_file_raw(self, project_id, path, branch="master"):
        """
        Gets raw content from the given file path
        :param project_id: integer containing project id
        :param path: string containing the path to the file for which the raw content is to be fetched
        :param branch: string containing the branch name from which the files are to be fetched
        :return: string containing raw file data
        """
        if not self.user_id:
            self.get_user_id()
        if type(self.user_id).__name__ == "dict":
            return self.user_id
        project_file_raw = None
        api = self.api_url + "projects/{0}/repository/files/{1}/raw?ref={2}"
        headers = {
            'Private-Token': self.access_token,
            "Content-Type": "application/json"
        }
        path = parser.quote(path, safe="")
        url = api.format(project_id, path, branch)
        data = requests.get(url=url, headers=headers)
        if data.ok:
            data = data.content
        if data:
            project_file_raw = data

        return project_file_raw


def main():
    """
    main
    :return: None
    """
    gl = GitLab(user_name="vishnu2981997", access_token="access_token")
    user_id = gl.get_user_id()
    projects = gl.get_user_projects()
    project_id = gl.get_project_id(project_name="wasup_bro")
    project_branches = gl.get_branches(project_id=project_id)
    project_files = gl.get_all_project_files(project_id=project_id, branch="master")
    file_content = gl.get_file_raw(project_id=project_id, path="booo/booo_file_1.py", branch="master")
    files = gl.get_project_files(project_id=project_id, path="/booo/", branch="master")


if __name__ == "__main__":
    main()
