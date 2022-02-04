import setuptools

version_text = None
with open("finx_ib_reports/version.txt", "r", encoding="utf-8") as f:
    version_text = f.read()

with open("README.md", "r") as f:
    long_description = f.read()

deps = [
    "ib_insync",
    "loguru",
    "pandas >=1.3.0,<1.4",
    "numpy",
    "pydantic",
    "python-dotenv",
    "pytz",
    "requests",
]

test_deps = ["pytest"]

project_url = "https://github.com/westonplatter/finx-ib-reports"

setuptools.setup(
    name="finx_ib_reports",
    version=version_text,
    description="IBKR report data via ib_insync",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="westonplatter",
    author_email="westonplatter+finx@gmail.com",
    license="BSD-3",
    url=project_url,
    python_requires=">=3.6",
    packages=["finx_ib_reports"],
    install_requires=deps,
    tests_require=test_deps,
    project_urls={
        "Issue Tracker": f"{project_url}/issues",
        "Source Code": f"{project_url}",
    },
)
