# pylint: disable=exec-used
"""Set up"""

import os.path
from setuptools import setup, find_packages

__version__ = None

with open('requirements.txt', encoding='utf-8') as f:
    requirements = f.read().splitlines()
here = os.path.abspath(os.path.dirname(__file__))
exec(open(f"{here}/prismasase/_version.py", encoding='utf-8').read())
readme_path = os.path.join(here, "README.md")
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf-8')

setup(
    name='prisma-access-sase',
    version=__version__,
    author="atav928",
    author_email="adam@tavnets.com",
    maintainer_email="adam@tavnets.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    test_suite="tests",
    url='https://github.com/atav928/prisma-access-sase',
    keywords=['sase', 'prisma access', 'prisma', 'paloalto'],
    long_description=readme,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'prisma_yaml_script = prismasase.__main__:gen_yaml',
        ],
    },
)  # pragma: no cover
