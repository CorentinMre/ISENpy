import setuptools

setuptools.setup(
    name='ISENpy',
    version='0.1.0',    
    description='A python API wrapper for ISEN-OUEST',
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