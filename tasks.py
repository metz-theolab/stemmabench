"""Module defining a set of userfule tasks for CI/CD.
"""
from invoke import task
import platform


def get_virtualenv_cmd():
    """Get the right command to activate the virtualenv depending on the
    target platform.
    """
    if platform.system() == "Windows":
        return ".\\.env\\Scripts\\activate"
    else:
        return "source .env/bin/activate"


@task
def install(c, proxy="", extra=""):
    """Install the package.

    Args:
        c (Invoke context): Invoke context
        proxy (str, optional): The value of a proxy.
            Defaults to "".
        extra (str, optional): The extra packages to install.
            Defaults to "".
    """
    extra_cmd = f"[{extra}]" if extra else ""
    # Create a virtualenv
    c.run("virtualenv .env")
    # Get virtualenv command for the platform
    virtualenv_cmd = get_virtualenv_cmd()
    # Install package within virtualenv
    with c.prefix(virtualenv_cmd):
        install_cmd = "pip install ." + extra_cmd
        proxy_cmd = f" --proxy {proxy}" if proxy else ""
        c.run(install_cmd + proxy_cmd)


@task
def test(c, cov=True):
    """Run the unit tests of the packages, within the virtualenv.
    The extra packages related to testing must be installed
    before hand.
    """
    virtualenv_cmd = get_virtualenv_cmd()
    coverage = "--cov=./src/stemmabench" if cov else ""
    with c.prefix(virtualenv_cmd):
        c.run(f"pytest {coverage} ./src/tests")


@task
def typecheck(c):
    """Check the type of the code using mypy.
    """


@task
def lint(c):
    """Lint the package using flake8.
    """
    c.run("flake8 .\src\ --exclude=tests")


@task
def build(c):
    """Build the package wheel.
    """
    c.run("flake8 .\src\ --exclude=tests")
