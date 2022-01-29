import click
from loguru import logger

from finx_ib_reports.download_trades import execute


@click.group()
def core():
    pass


@core.command()
@click.option(
    "--report-name",
    default="annual",
    help="Report name use in the env file. Eg, 'IB_REPORT_ID_[report_name]'",
)
def download(report_name: str):
    logger.info(f"Fetching IB Report (name={report_name})")
    execute(report_name)


if __name__ == "__main__":
    core()
