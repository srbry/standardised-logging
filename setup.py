import sys

from setuptools import setup

assert sys.version_info >= (3, 6, 0), "standardised_logging requires Python 3.6+"
from pathlib import Path  # noqa E402

CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))  # for setuptools.build_meta

setup(
    name="standardised_logging",
    description="A logging library to standardise log formats in JSON format",
    url="https://github.com/srbry/standardised-logging",
    license="MIT",
    packages=["standardised_logging"],
    package_dir={"": "."},
    package_data={"standardised_logging": ["py.typed"]},
    python_requires=">=3.6",
    install_requires=[
        "pytz>=2020.4",
    ],
    test_suite="tests.test_logging",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
