from setuptools import find_packages, setup

setup(
    name="ag-mode-manager",
    version="2.1.3",
    description="Cross-Platform AntiGravity Mode, Rules, Knowledge & Quality-Control System",
    author="Muhammad Wasif",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "rich>=13.0.0",
        "prompt-toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ag-mode=ag_mode.cli.main:main",
            "agmm=ag_mode.cli.main:main",
        ],
    },
    python_requires=">=3.10",
)
