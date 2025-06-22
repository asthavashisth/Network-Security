from setuptools import setup, find_packages
from typing import List
HYPEN_E_DOT = '-e .'
def get_requirements()->List[str]:
    requirements=[]
    with open('requirements.txt') as file:
        requirements=file.readlines()
        requirements=[req.strip() for req in requirements if req.strip()]
        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)
    return requirements
   
setup(
    name='Network Phising',
    version='0.0.1',
    author='Astha Vashisth',
    author_email='astha.vashisth136@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements(),
    description='A project to detect phishing websites using machine learning'
)