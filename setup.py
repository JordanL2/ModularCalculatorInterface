import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("config/ModularCalculator/version.yml", "r") as fh:
    version_yml = fh.read()
    versions = []
    for line in version_yml.split("\n"):
        if line.startswith('- '):
            versions.append(line[2:])

setuptools.setup(
    name="modularcalculatorinterface",
    version='.'.join(versions),
    author="Jordan Leppert",
    author_email="jordanleppert@gmail.com",
    description="A powerful, modular calculator written in Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JordanL2/ModularCalculator",
    packages=setuptools.find_packages() + setuptools.find_namespace_packages(include=['modularcalculatorinterface.*']),
    install_requires=[
        'modularcalculator>=1.3.0',
        'PyQt5',
        'pyyaml',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
    entry_points = {'console_scripts': ['modularcalculator = modularcalculatorinterface.main:main',], },
)
