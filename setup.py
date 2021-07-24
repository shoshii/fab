from setuptools import setup, find_packages
from myfab.app import __VERSION__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="myfab",
    version=__VERSION__,
    author="Shogo Hoshii",
    author_email="treasurehunt0102@gmail.com",
    description="A small sample application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'jinja2',
        'fabric'
    ],
    entry_points={
        "console_scripts": [
            "myfab=myfab.app:app.run",
        ]
    },
)