import argparse
import os

import selenium

def create_project_dir(name,storage):
        if storage == "dev" or "projects":
            storage_path = f"c:/{storage}"
            project_dir = name
            os.mkdir(os.path.join(storage_path, project_dir))
            return True

def initiate_git(directory):

        class ChangeDirectory():
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parse project name and storage name")
    parser.add_argument("-p",dest="projectName",type=str,help="Project name")
    parser.add_argument("-s",dest="storage",type=str,help="Storage name")
    args = parser.parse_args()

    if create_project_dir(args.projectName,args.storage):
        directory = f"c:/{args.storage}/{args.projectName}"
        initiate_git(directory)
