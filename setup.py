import os
from setuptools import setup, find_packages


def get_package_info():
    cwd = os.path.abspath(os.path.dirname(__file__))
    info = dict()
    with open(os.path.join(cwd, "dive3m", "__about__.py")) as f:
        exec(f.read(), info)
    return info

def readme():
    with open("README.md", "r") as f:
        content = f.read()
    return content


def get_install_requires() -> list:
    out = []
    with open("requirements.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line)
    return out


if __name__ == "__main__":
    info = get_package_info()
    setup(
        name=info["__title__"],
        description=info["__description__"],
        version=info["__version__"],
        author=info["__author__"],
        author_email=info["__author_email__"],
        url=info["__url__"],
        long_description=readme(),
        long_description_content_type="text/markdown",
        packages=find_packages(),
        python_requires="==3.9.*",
        zip_safe=False,
        install_requires=get_install_requires(),
    )
