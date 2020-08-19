import argparse
import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from decouple import config

from projectorEmail import ReadEmail


timestamp = datetime.today().strftime("%Y-%m-%d %H:%M:%S")


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
        print(f"[{timestamp}] Git initiated \n")


def create_repo(driver, repo_name):
    """
    Create new github repository
    """
    new_project_btn = driver.find_element_by_link_text("New")
    new_project_btn.click()

    time.sleep(3)

    repository_name = driver.find_element_by_id("repository_name")
    repository_name.clear()
    repository_name.send_keys(repo_name)

    create_repository_btn = driver.find_element_by_xpath(
        "//div[@class='js-with-permission-fields']/button[last()]"
    )

    if create_repository_btn:
        driver.execute_script("arguments[0].scrollIntoView();", create_repository_btn)
        time.sleep(2)
        create_repository_btn.click()
        print(f"[{timestamp}] Repo created: {repo_name}")


# REMOTE REPOSITORY
def remote_repository(url, repo_name):
    try:
        driver = webdriver.Firefox()
        driver.get(url)
        print(f"[{timestamp}] Projector in {driver.title}")
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

        print(
            f"[{timestamp}] Projector has logged in user: '{config('GITHUB_USERNAME', cast=str)}' into {driver.title}"
        )

        time.sleep(3)

        try:
            """
            Error handling for element (new_project_btn) not found.
            Verification sent to email from github (sent to phone for 2F-AUTH)
            """

            # Create new repo
            create_repo(driver, repo_name)
        except NoSuchElementException as e:
            print(e.msg, sep="\n")
            print(
                f"[{timestamp}] Opening email client to read verification code",
                sep="\n",
            )
            get_mail = ReadEmail(
                config("EMAIL_ADDRS", cast=str), config("EMAIL_PASSWORD", cast=str)
            )
            otp_code = get_mail.read_email()

            verification_otp_field = driver.find_element_by_id("otp")
            verification_otp_field.clear()
            verification_otp_field.send_keys(otp_code)

            verify_btn = driver.find_element_by_class_name("btn-block")
            verify_btn.click()

            # Create new repo
            create_repo(driver, repo_name)

        # print(f"[timestamp] Closing browser...")
        time.sleep(3)
        # driver.close()

    except WebDriverException as e:
        # print(f"[{timestamp}] Unable to reach website: {url}")
        print(e.screen)


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
