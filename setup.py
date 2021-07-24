from setuptools import setup, find_packages
from myapp.app import __VERSION__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="myapp",
    version=__VERSION__,
    author="Shogo Hoshii",
    author_email="treasurehunt0102@gmail.com",
    description="A small sample application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'jinja2',
        'fabric'
    ],
    entry_points={
        "console_scripts": [
            "myapp=myapp.app:app.run",
        ]
    },
)