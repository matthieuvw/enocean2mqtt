
clean:

	rm -Rf ./dist
	rm -Rf ./build
	rm -Rf ./enocean2mqtt.egg-info

package:

	python3 setup.py sdist bdist_wheel

publish-test:

	twine upload --repository testpypi dist/*

publish:

	twine upload --repository pypi dist/*
