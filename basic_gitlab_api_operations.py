import requests
import functools


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

        :return:
        """
        page = 1
        api = self.api_url + "search?scope=users&search={0}&per_page=100&page={1}"
        headers = {
            'Private-Token': self.access_token,
            "Content-Type": "application/json"
        }
        while not self.user_id:
            url = api.format(self.user_name, page)
            data = requests.get(url=url, headers=headers)
            if data.ok:
                data = data.json()
            else:
                break
            if data:
                for i in data:
                    if i["username"] == self.user_name:
                        self._user_id = i["id"]
                        break
                page += 1
            else:
                break

        return self._user_id

    def get_user_projects(self):
        """

        :return:
        """
        if not self.user_id:
            self.get_user_id()
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

        :param project_name:
        :return:
        """
        if not self.user_id:
            self.get_user_id()
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
            for i in data:
                if i["name"] == project_name:
                    project_id = i["id"]
            page += 1

        return project_id

    def get_branches(self, project_id):
        """

        :param project_id:
        :return:
        """
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

    def get_project_files(self, project_id, branch="master"):
        """

        :param project_id:
        :param branch:
        :return:
        """
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

    def get_file_raw(self, project_id, path, branch="master"):
        """

        :param project_id:
        :param path:
        :param branch:
        :return:
        """
        project_file_raw = None
        api = self.api_url + "projects/{0}/repository/files/{1}/raw?ref={2}"
        headers = {
            'Private-Token': self.access_token,
            "Content-Type": "application/json"
        }
        path = path.replace("/", "%2F")
        path = path.replace(".", "%2E")
        url = api.format(project_id, path, branch)
        data = requests.get(url=url, headers=headers)
        if data.ok:
            data = data.content
        if data:
            project_file_raw = data

        return project_file_raw


def main():
    """

    :return:
    """
    gl = GitLab(user_name="username", access_token="access_token")
    user_id = gl.get_user_id()
    projects = gl.get_user_projects()
    project_id = gl.get_project_id(project_name="project_name")
    project_branches = gl.get_branches(project_id=project_id)
    files = gl.get_project_files(project_id=project_id)
    file_content = gl.get_file_raw(project_id=project_id, path="path to file eg: test/foo.txt")


if __name__ == "__main__":
    main()
