import argparse
import os
import time
from decouple import config

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchElementException


def create_project_dir(name, storage):
    if storage == "dev" or "projects":
        """
            storage_path = f"c:/{storage}"
            project_dir = name
            os.mkdir(os.path.join(storage_path, project_dir))
            """
        return True


def initiate_git(directory):
    class ChangeDirectory:
        """Handles projector directory change"""

        def __init__(self, dir):
            self.change_dir = os.chdir(dir)

        def __enter__(self):
            return self.change_dir

        def __exit__(self, type, value, traceback):
            os.chdir(os.getcwd())

    with ChangeDirectory(directory):
        os.system("echo . > .gitignore && echo . > README.md")
        os.system("git init")
        os.system("git add . && git commit -m 'test'")
        print(f"Git initiated at {args.projectName} \b\b")


# REMOTE REPOSITORY
def remote_repository(url, repo_name):
    try:
        driver = webdriver.Firefox()
        driver.get(url)
        assert f"Projector in {driver.title}"
        driver.find_element_by_link_text("Sign in").click()

        time.sleep(3)

        username_field = driver.find_element_by_id("login_field")
        password_field = driver.find_element_by_id("password")

        username_field.clear()
        password_field.clear()

        username_field.send_keys(config("GITHUB_USERNAME", cast=str))
        password_field.send_keys(config("GITHUB_PASSWORD", cast=str))

        sign_in_btn = driver.find_element_by_name("commit")
        sign_in_btn.click()

        assert f"Projector has logged in user: {config('GITHUB_USERNAME', cast=str)}"

        time.sleep(3)

        """
            Error handling for element (new_project_btn) not found.
            Verification sent to email from github (sent to phone for 2F-AUTH)
        """
        try:
            new_project_btn = driver.find_element_by_link_text("New")
            new_project_btn.click()

            time.sleep(3)

            repository_name = driver.find_element_by_id("repository_name")
            repository_name.clear()
            repository_name.send_keys(repo_name)

            create_repository = driver.find_elements_by_xpath(
                "//form[@id='new_repository']/button[@type='submit']"
            )
            # create_repository.click()
            if create_repository:
                print("Create button")

            assert f"Projector has created repository: {repo_name}"
        except NoSuchElementException as e:
            print(e.msg, sep="\n")
            print("Opening email client to read verification code...", sep="\n")

        print("Closing browser...")
        time.sleep(3)
        driver.close()

    except WebDriverException:
        print(f"Can't reach website: {url}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse project name and storage name")
    parser.add_argument("-p", dest="projectName", type=str, help="Project name")
    parser.add_argument("-s", dest="storage", type=str, help="Storage name")
    args = parser.parse_args()

    if create_project_dir(args.projectName, args.storage):
        directory = f"c:/{args.storage}/{args.projectName}"
        # initiate_git(directory)
        remote_repo_url = "https://github.com"
        remote_repository(remote_repo_url, args.projectName)
