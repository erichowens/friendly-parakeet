from setuptools import setup, find_packages

setup(
    name="friendly-parakeet",
    version="0.1.0",
    description="A little buddy who tracks your coding progress and velocity",
    author="Eric Howens",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "gitpython>=3.1.0",
        "flask>=2.0.0",
        "jinja2>=3.0.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "parakeet=parakeet.cli:main",
        ],
    },
    python_requires=">=3.8",
)
