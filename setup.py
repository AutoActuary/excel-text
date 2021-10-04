import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="excel-text",
    author="Bart-Jan Hulsman",
    author_email="hulsmanbj@gmail.com",
    description="Python implementation of the excel text function",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AutoActuary/excel-text",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    use_scm_version={
        "write_to": "excel_text/version.py",
    },
    setup_requires=[
        "setuptools_scm",
    ],
    install_requires=[
        'locate',
    ],
)
