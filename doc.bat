rem pip install sphinx sphinx_rtd_theme
rem md doc && cd doc && sphinx-quickstart
rem cd doc && sphinx-apidoc -o ./source ../pybeans
cd doc && make clean && make html && start build\html\index.html