import setuptools

with open("README.md", "r") as f:
    long_description = f.read()


setuptools.setup(
    name="FinanceHub",
    version="0.0.5",
    author="Finance Hub Community",
    author_email="vitor.eller30@gmail.com",
    description="A Finance utility Repository",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'numpy>=1.16.1',
        'pandas>=0.24.1',
        'sqlalchemy>=1.3.5',
        'pykalman>=0.9.5',
        'scipy>=1.2.1',
        'matplotlib>=3.0.2',
        'seaborn>=0.9.0'
    ]
)