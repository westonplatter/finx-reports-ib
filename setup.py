import setuptools

version_text = None
with open("finx_reports_ib/version.txt", "r", encoding="utf-8") as f:
    version_text = f.read()

with open("README.md", "r") as f:
    long_description = f.read()

deps = [
    "ib_insync",
    "loguru",
    "pandas",
    "numpy",
    "pydantic",
    "python-dotenv",
    "pytz",
    "requests",
]

project_url = "https://github.com/westonplatter/finx-reports-ib"

setuptools.setup(
    name="finx_reports_ib",
    version=version_text,
    description="IBKR report data via ib_insync",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="westonplatter",
    author_email="westonplatter+finx@gmail.com",
    license="BSD-3",
    url=project_url,
    python_requires=">=3.6",
    packages=["finx_reports_ib"],
    install_requires=deps,
    project_urls={
        "Issue Tracker": f"{project_url}/issues",
        "Source Code": f"{project_url}",
    },
)
