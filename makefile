SHEll := /bin/zsh
.PHONY: venv

venv:
	@echo "Criando/Atualizando o ambiente virtual"
	@uv sync
	@echo "Ambiente virtual criado/atualizado com sucesso"

commit:
	@echo "Revisar mudanças para este commit: "
	@echo "-------------------------------------"
	@git status -s 
	@echo "-------------------------------------"
	@read -p "Commit msg: " menssagem ; \
	git add . ;\
	git commit -m "$$menssagem" ;\

update:
	@git fetch origin
	@git pull
	@$(MAKE) venv

lint:
	task lint \
	task format

dev:
	@echo "Iniciando servidor em modo de desenvolvimento"
	@echo "-------------------------------------"
	uvicorn app.startup:app --host 0.0.0.0 --port 8000 --reload


prod:
	@echo "Iniciando servidor em modo de produção"
	@echo "-------------------------------------"
	uvicorn app.startup:app --host 0.0.0.0 --port 8000
	@echo "-------------------------------------"
	@echo "Servidor iniciado com sucesso"
	@echo "Acesse: http://localhost:8000"

migrate:
	@echo "Criando nova migração"
	@echo "-------------------------------------"
	@echo "Lembre-se de colocar no arquivo .env do alembic o import do seu modelo novo"
	@echo "-------------------------------------"
	@read -p "Mensagem da migração: " msg ; \
	alembic revision --autogenerate -m "$$msg"

upgrade:
	@echo "Deseja realmente aplicar a ultima migração? (y/n)"
	@read -p "Resposta: " resposta ; \
	if [ $$resposta = "y" ]; then \
		alembic upgrade head ;\
	fi
	

downgrade:
	@echo "Deseja realmente reverter a ultima migração? (y/n)"
	@read -p "Resposta: " resposta ; \
	if [ $$resposta = "y" ]; then \
		alembic downgrade -1 ;\
	fi
	

test:
	@echo "Iniciando os Testes:"
	export PYTHONPATH=/workspace && pytest -s -x --cov=app -vv
	