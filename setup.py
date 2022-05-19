import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="modularcalculatorinterface",
    version="1.2.0",
    author="Jordan Leppert",
    author_email="jordanleppert@gmail.com",
    description="A powerful, modular calculator written in Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JordanL2/ModularCalculator",
    packages=setuptools.find_packages() + setuptools.find_namespace_packages(include=['modularcalculatorinterface.*']),
    install_requires=[
        'modularcalculator',
        'PyQt5',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: LGPL-2.1 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points = {'console_scripts': ['modularcalculator = modularcalculatorinterface.interface:main',], },
)
