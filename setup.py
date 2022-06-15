import setuptools

setuptools.setup(
    name="fmg",
    version="0.0.1",
    author="reed",
    author_email="reed.topcode@gmail.com",
    description="Fuzzy match group",
    long_description="Fuzzy match group",
    long_description_content_type="text/plain",
    url="https://github.com/reed1/python-fmg",
    project_urls={
        "Bug Tracker": "https://github.com/reed1/python-fmg/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
