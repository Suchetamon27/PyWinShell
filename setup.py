from setuptools import setup, find_packages

setup(
    name="pywinshell",
    version="1.0.0",
    description="A modern interactive shell for Windows written in Python",
    author="PyWinShell Developer",
    packages=find_packages(),
    install_requires=[
        "prompt-toolkit>=3.0.0",
        "rich>=13.0.0",
        "colorama>=0.4.6",
        "psutil>=5.9.0",
        "pywin32>=306; sys_platform == 'win32'",
    ],
    entry_points={
        "console_scripts": [
            "pywinshell=pywinshell.main:main",
        ],
    },
    python_requires=">=3.8",
)
