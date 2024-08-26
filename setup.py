from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='django-modeltranslation-admin',  
    version='0.1.0',  
    author='Your Name',
    author_email='your_email@example.com',
    description='A Django extension for seamless model translations in the admin interface.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/shotiko13/django-Model-Translations.git',  # Your GitHub repo URL
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",  

        'Framework :: Django',
        'Framework :: Django :: 3.2',  
        'Framework :: Django :: 4.0', 
    ],
    install_requires=[
        'Django>=3.2',  
    ],
    python_requires='>=3.6',
)