"""Module defining a set of userfule tasks for CI/CD.
"""
from invoke import task


@task
def install(c, proxies=""):
    """Install the package.
    """
    install_dependencies_cmd = "pip install -r requirements.txt"
    if proxies:
        install_dependencies_cmd += "--proxy {proxies}"
    c.run(install_dependencies_cmd)
    c.run("pip install .")


@task
def test(c):
    """Run the unit tests of the package.
    """
    c.run("pytest ./src/tests")


@task
def typecheck(c):
    """Check the type of the code using mypy.
    """


@task
def lint(c):
    """Lint the package using flake8.
    """
    c.run("flake8 .\src\ --exclude=tests")
