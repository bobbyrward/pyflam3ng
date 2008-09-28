

all:
	 python setup.py build_ext --inplace
	 
test:
	 python tests/test.py  

clean:
	rm -rf build pyflam3ng/_flam3.c pyflam3ng/_flam3.so
