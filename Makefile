download:
	@python cli.py download --report-name=annual

download.daily:
	@python cli.py download --report-name=daily --cache

download.weekly:
	@python cli.py download --report-name=weekly --cache

changelog:
	git-chglog -o CHANGELOG.md

changelog.commit: changelog
	git add CHANGELOG.md && git commit CHANGELOG.md -m "update changelog"

test:
	pytest .
