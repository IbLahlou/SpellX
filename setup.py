import setuptools

with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

__version__ = "0.0.1"

REPO_NAME = "SpellX"
AUTHOR_USER_NAME = "IbLahlou"
SRC_REPO="SpellX"
AUTHOR_EMAIL = "ibrahimlahlou021@gmail.com"

setuptools.setup(
    name=REPO_NAME,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
)