#!/bin/bash
cd ~
git clone https://github.com/opencv/opencv
git clone https://github.com/opencv/opencv_contrib
export CPLUS_INCLUDE_PATH="/Users/pgieschen/anaconda/include/python3.6m/"
cd ~/opencv
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D PYTHON3_LIBRARY=/Users/phillipgieshen/anaconda/lib/libpython3.6m.dylib \
    -D PYTHON3_INCLUDE_DIR=/Users/phillipgieshen/anaconda/include/python3.6m \
    -D PYTHON_DEFAULT_EXECUTABLE=/Users/phillipgieshen/anaconda/bin/python3 \
    -D PYTHON_PACKAGES_PATH=/Users/phillipgieshen/anaconda/lib/python3.6/site-packages \
    -D INSTALL_C_EXAMPLES=OFF \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D BUILD_EXAMPLES=ON \
    -D BUILD_opencv_python3=ON \
    -D BUILD_opencv_python2=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules ..
make -j4
sudo make install


cd ~/opencv/lib/python3.6/site-packages
mv cv2.cpython-36m-darwin.so cv2.so

cp cv2.so /Users/phillipgieshen/anaconda/lib/python3.6/site-packages
cp cv2.so /Users/phillipgieshen/anaconda/env/finalProject/lib/python3.6/site-packages
