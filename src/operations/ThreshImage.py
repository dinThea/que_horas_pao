
from __future__ import absolute_import
import cv2

class ThreshImage:
    def __init__(self):
        pass

    def thresh(self,image):

        # image = cv2.imread(os.path.join('./amatch', path))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 200, 255)
        thresh = cv2.threshold(gray, 0, 255,
            cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        thresh = self.erosion(thresh, 0)
        thresh = cv2.bitwise_not(thresh)
        return thresh

    def morph_shape(self, val):
        if val == 0:
            return cv2.MORPH_RECT
        elif val == 1:
            return cv2.MORPH_CROSS
        elif val == 2:
            return cv2.MORPH_ELLIPSE

    def erosion(self, image, val):
        erosion_size = 4
        erosion_shape = self.morph_shape(0)
        
        element = cv2.getStructuringElement(erosion_shape, (2 * erosion_size + 1, 2 * erosion_size + 1),
                                        (erosion_size, erosion_size))
        
        erosion_dst = cv2.erode(image, element)
        return erosion_dst


    def dilatation(self, image, val):
        dilatation_size = 10
        dilation_shape = self.morph_shape(0)
        element = cv2.getStructuringElement(dilation_shape, (2 * dilatation_size + 1, 2 * dilatation_size + 1),
                                        (dilatation_size, dilatation_size))
        dilatation_dst = cv2.dilate(image, element)
        return dilatation_dst