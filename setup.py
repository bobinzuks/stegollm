from setuptools import setup, find_packages

# Read requirements
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f.readlines() if not line.startswith("#")]

# Read the README for the long description
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="stegollm",
    version="0.1.0",
    description="A local proxy app for compressing LLM prompts using steganography",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="StegoLLM Team",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/stegollm",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "stegollm=stegollm.main:main",
        ],
    },
)