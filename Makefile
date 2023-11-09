requirements.txt:
	 pip freeze > requirements.txt

list_poetry:
	poetry env list

clear_poetry:
	poetry env remove --all

close:
	python tests/close_mido.py