from setuptools import find_packages, setup

setup(
    name="kanada_alphabets",
    version="1.0",
    packages=find_packages(),
    license="Private",
    description="Learn Kanada Alphabets with Spaced Repetetion for Kids ",
    author="sukhbinder",
    author_email="sukh2010@yahoo.com",
    entry_points={
        'console_scripts': ['lkanada= src.kanada:main',
        'bkanada=src.tkinterAPP:main']
    },

    install_requires=["pandas","colorama",
    "pywin32 >= 1.0;platform_system=='Windows'"],
    )
