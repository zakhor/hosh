from glob import glob
from os.path import basename
from os.path import splitext
from setuptools import setup
from setuptools import find_packages

def _requires_from_file(filename):
    return open(filename).read().splitlines()

setup(
    name="Hosh Package",
    version="3.2.1",
    author="zakhor",
    url="https://github.com/zakhor/hosh",
    packages=find_packages(""),
    package_dir={"": "./"},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    install_requires=_requires_from_file('requirements.txt'),
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-cov"]
)