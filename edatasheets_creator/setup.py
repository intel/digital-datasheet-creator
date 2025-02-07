from setuptools import find_packages, setup

packages = [
]

packages_to_include = ['edatasheets_creator', 'edatasheets_creator.*']

setup(
    name='edatasheets_creator',
    description='EDatasheet Creator Tool',
    version='1.0.1',
    packages=find_packages(include=packages_to_include),
    install_requires=packages,
    include_package_data=True
)
