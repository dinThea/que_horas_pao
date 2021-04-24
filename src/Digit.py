from __future__ import absolute_import

from .operations import ThreshImage
import os
import cv2
from skimage.metrics import structural_similarity as ssim

class Digit():
    
    def __init__(self, thresh, digit_path='./amath'):
        self._digit_path = digit_path
        self.thresh = thresh

    def gather_digits(self):

        self._digits = {}
        for idx, path in enumerate(os.listdir('./amatch')):
            
            digitCnts = []
            image = cv2.imread(os.path.join('./amatch', path))
            self._digits[int(path.replace('.jpg', ''))] = self.thresh.thresh(image)

    def _create_border(self, image, largest_h, largest_w):
        return cv2.copyMakeBorder(
            image, 
            0,
            largest_h-image.shape[0],
            0,
            largest_w-image.shape[1],
            cv2.BORDER_CONSTANT
        )

    def _adjust_images(self, image, digit, largest_h, largest_w):
        return self._create_border(image, largest_h, largest_w), self._create_border(digit, largest_h, largest_w)

    def get_digit(self, image):
        
        digit = '.' 
        max_score = 0
        for key, digit_image in self._digits.items():
            
            largest_h, largest_w = map(max, zip(image.shape, digit_image.shape)) 
            image_copy, digit_image_copy = self._adjust_images(image, digit_image, largest_h, largest_w)

            (score, diff) = ssim(digit_image_copy, image_copy, full=True)
            diff = (diff * 255).astype("uint8")
            if score > max_score and score > 0.7:
                digit = key
                max_score = score

        return digit