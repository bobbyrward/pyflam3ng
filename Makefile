

all:
	 python setup.py build_ext --inplace
	 
test:
	 python tests/test_ImageComments.py  
	 python tests/test_RenderStats.py
	 python tests/test_Frame.py
	 python tests/test_Palette.py

clean:
	rm -rf build _flam3.c _flam3.so
