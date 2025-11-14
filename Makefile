###############################################################################
#
# Download reports
#
# Note: These targets have been removed as cli.py has been deleted
# If you need to run these commands, use the Python functions directly:
# uv run python -c "from ngv_ibkr_reports.download_trades import execute_csv_for_accounts; execute_csv_for_accounts('annual', cache=True)"

###############################################################################
#
# dev commands
#
changelog:
	git-chglog -o CHANGELOG.md

changelog.commit: changelog
	git add CHANGELOG.md && git commit CHANGELOG.md -m "update changelog"

test:
	uv run pytest .

###############################################################################
#
# release
#
release: release.applytag release.check release.build release.upload

release.applytag:
	echo $$(git describe --tags --abbrev=0 ) > ngv_ibkr_reports/version.txt

release.check:
	pre-commit run -a
	git diff --quiet

release.build:
	uv build

release.upload:
	twine upload dist/*
