import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ISENpy',
    version='0.2.4',    
    description='A python API wrapper for ISEN-OUEST',
    long_description_content_type = "text/markdown",
    long_description=long_description,
    url='https://github.com/CorentinMre/ISENpy',
    author='CorentinMre',
    author_email='corentin.marie@isen-ouest.yncrea.fr',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=['requests',
                      'bs4',  
                      'lxml',                   
                      ],

    classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ]
)