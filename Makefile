.DEFAULT_GOAL := help

CFG?=DJANGO_SETTINGS_MODULE=cfg.settings

dep_back: ## install backend deps
	cd backend && pipenv install

dep_front: ## install frontend deps
	cd frontend &&  npm install

build_front: ## build frontend
	cd frontend && node node_modules/.bin/ng build;

format: ## format code with yapf
	cd backend && pipenv run isort -rc .
	cd backend && pipenv run yapf -r -i --verbose .

lint: ## run flake8 linter
	cd backend && pipenv run flake8 --max-line-length=120 --exclude migrations .

pylint: ## run pylint
	cd backend && pipenv run pylint --max-line-length=120 amocrm appuser blog cfg core shop static support

tslint: ## run tslint
	cd frontend && node_modules/.bin/tslint -c tslint.json --project .         

test: ## run python tests
	${CFG} cd backend && pipenv run python manage.py test 

run: ## run site
	-mkdir -p backend/log
	${CFG} cd backend && pipenv run python manage.py runserver

vagrant: ## Create ubuntu18.04 VM with vagrant
	vagrant up

help: 
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	
