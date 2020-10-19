
import numpy as np
from sklearn import linear_model
import glob
import os
import cv2

class ML:

    def __init__(self, files):
        self.files = files
        self.classifier = linear_model.LogisticRegression(tol=0.1)

    def generate_labels(self, files):
        '''
        LABELS
        0 - D0
        1 - D1
        2 - A0
        3 - A1
        4 - N1
        5 - N2
        '''
        print("Generating labels...")
        labels = []
        
        for name in files:
            if name.startswith('../bin/train/D0'):
                labels.append(0)
            elif name.startswith('../bin/train/D1'):
                labels.append(1)
            elif name.startswith('../bin/train/A0'):
                labels.append(2)
            elif name.startswith('../bin/train/A1'):
                labels.append(3)
            elif name.startswith('../bin/train/N0'):
                labels.append(4)
            elif name.startswith('../bin/train/N1'):
                labels.append(5)
            else:
                print(name)
                return None

        return np.array(labels)
    
    def train(self):

        print("[INFO] Creating data array")
        imgs = []

        for img in self.files:
            img = cv2.imread(img)
            scale_percent = 50 # percent of original size
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)
            # resize image
            img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            # img = cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2GRAY)
            imgs.append(img.flatten())

        imgs = np.array(imgs)
        imgs = imgs/255.0
        imgs = imgs.reshape(len(imgs), -1)
        labels = self.generate_labels(self.files)

        print("[INFO] Starting fit")
        print(imgs.shape)
        self.classifier.fit(imgs, labels)

        print("[INFO] Fit completed")

    def test(self, files):
        true_labels = self.generate_labels(files)
        imgs = []

        for img in files:
            img = cv2.imread(img)
            scale_percent = 50 # percent of original size
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)
            # resize image
            img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            # img = cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2GRAY)
            imgs.append(img.flatten())

        imgs = np.array(imgs)
        imgs = imgs/255.0
        imgs = imgs.reshape(len(imgs), -1)

        predicted_labels = self.classifier.predict(imgs)

        print (true_labels)
        print (predicted_labels)

files = glob.glob('../bin/train' + '/*.jpg')
test_files = glob.glob('../bin/test' + '/*.jpg')
model = ML(files = files)

model.train()

model.test(test_files)