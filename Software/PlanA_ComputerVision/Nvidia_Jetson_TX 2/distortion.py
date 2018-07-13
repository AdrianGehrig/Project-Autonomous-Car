import numpy
import cv2
import glob


### termination criteria ###
# algorithm stops when a specified accuracy epsilon (0.001) is reached
#or after a specified number of iterations (30)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

### prepare object points, (0,0,0) ... (9,9,0) ###
# numpy.zeros(shape, dtype)
# shape of array in this case 9*9 is the amount of corners that can be detected, so it depends
# on the size of the chessboard, 81 points in total, each point has 3 parameters (XYZ)
# the array is filled with zeros

objp = numpy.zeros((9*9,3), numpy.float32)

# fill the array with ascending x and y coordinates, so that each of the possible 81
# object points are defined
# numpy.mgrid creates a meshed array, see
# https://stackoverflow.com/questions/42308270/python-numpy-mgrid-and-reshape
# T means transpose, and reshape turns it into a 81x2 matrix
# this matrix is put inro the first two colums of objp

objp[:,:2] = numpy.mgrid[0:9,0:9].T.reshape(-1,2)

# setup lists to store all found image and object points
objpoints = []
imgpoints = []

# load all images from a given directory
images = glob.glob('*.jpg')
print ("loaded pictures")
# for each found picture in the given directory, import the picture and convert it to gray
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # find the chessboard corners (image, corners, flags)
    ret, corners = cv2.findChessboardCorners(gray, (9,9), None)
    print (ret)
    # if corners are found, an object point is added to the objpoint list
    if ret == True:
        objpoints.append(objp)

        # refinement of corner locations
        # (input, initial corners, search window, dead window, termination criteria)
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,1), criteria)

        # adding the refinded corners to the image point list
        imgpoints.append(corners2)

        # draw and display the corners
        cv2.drawChessboardCorners(img, (9,9), corners, ret)
        cv2.imshow('img', img)
        cv2.waitKey(2000)

cv2.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    
# save distortion matrix and distortion coefficient

mtx.dump("mtx.dat")
dist.dump("dist.dat")

print("Calibration process complete!")


