test:
	pytest --tb=short

# 常驻测试, 有代码改动就会运行测试用例
watch-tests:
	ls *.py | entr pytest --tb=short

black:
	black -l 86 $$(find * -name '*.py')
