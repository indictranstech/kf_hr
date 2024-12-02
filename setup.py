from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in kf_hr/__init__.py
from kf_hr import __version__ as version

setup(
	name="kf_hr",
	version=version,
	description="KFHR",
	author="indictrans",
	author_email="jitendra.r@indictranstech.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
