from setuptools import setup, find_packages

setup(
    name="gitcommitai",
    version="1.0.0",
    packages=find_packages(where="src"),
    pack_dir={"":"src"},
    install_requires=[
        "llama-cpp-python>=0.3.9",
        "psutil>=5.9.0",
        "rich>=13.0.0",
        "typer>=0.9.0"
    ],
    entry_points={
        "console_scripts": [
            "gitcommitai=gitcommitai.cli:app"
        ]
    },
    include_package_data=True,
    author="Santhosh Dhaipule Chandrakanth",
    author_email="you@example.com",  # 🔧 Replace with a real email before publishing
    url="https://github.com/yourname/gitcommitai",  # 🔧 Replace with your GitHub repo
    description="Local-first AI Git commit assistant using Phi-3 and LLMs offline",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
