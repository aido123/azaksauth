from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='azaksauth',
      zip_safe=True,
      version="0.0.1",
      packages=find_packages(),
      url='adrianhynes.com',
      author='adrianhynes',
      install_requires=requirements,
      author_email='adrianhynes@gmail.com',
      entry_points={
        'console_scripts': [
            'azaksauth = azaksauth.main:main',
        ]
    })