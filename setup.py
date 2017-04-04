
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.sdist import sdist


# update version info when build new
version = "1.1.3"

# basic info
appname = "hotspots_modder"
author = "minu jeong"
email = "mjung@ea.com"
maintainer = author
maintainer_email = email


class InstallAction(install):
    '''
    Custom action on install
    '''

    def run(self):
        install.run(self)
        print("Welcome to {}!".format(appname))
        print("You have installed, {} version.".format(version))
        print("Contact for help: {} ({}, {})".format(author, email, maintainer_email))


class SourceDistributeAction(sdist):
    '''
    Custom action on sdist
    '''

    def run(self):

        sdist.run(self)

        with open("dist/quick_install.bat", "w") as ff:
            ff.write("mayapy -m pip install {}-{}.tar.gz\npause".format(appname, version))


# do setup
setup(
    # basic info
    name=appname,
    version=version,
    author=author,
    author_email=email,
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    description="Maya 2016 tool for modifying hotspots files for FIFA online 3",

    # consider as static
    install_requires=["BeautifulSoup4"],
    packages=find_packages(),
    package_data={
        "HOTSPOTS": [
            "res/*.tga",
            "res/jersey_meshes/*.ma",
            "res/shorts_meshes/*.ma",
            "res/shader/*.ma"
        ]
    },

    # add custom actions
    cmdclass={
        "install": InstallAction,
        "sdist": SourceDistributeAction
    }
)
