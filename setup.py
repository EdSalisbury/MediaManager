from setuptools import setup, find_packages

setup(
    name='MediaManager',
    version='1.0.0',
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    scripts=[
        'bin/mediamanager'
    ],
    author='Ed Salisbury',
    author_email='ed.salisbury@gmail.com',
    description='A tool for managing photo and video files.',
    license='MIT',
    url='https://github.com/edsalisbury/MediaManager',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ]
)