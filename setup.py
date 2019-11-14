import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tubize",
    version="0.0.1",
    author="Oliver Vinn",
    author_email="oliver@vinn.co.uk",
    description="A small set of scripts to convert and use videos on the web.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/olivervinn/tubizescripts",
    package_dir={
        '': 'src',
    },
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)