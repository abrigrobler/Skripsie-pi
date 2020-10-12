#%%
from sklearn.cluster import KMeans
import cv2
import imutils
import numpy as np
import glob
import os

#%%
model = KMeans(n_clusters=2)

files = glob.glob('../bin/saved_images' + '/*.jpg')
imgs = []

for img in files:
    img = cv2.imread(img)
    img = imutils.resize(img, 700)
   # img = cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2GRAY)
    imgs.append(img)

imgs = np.array(imgs)
imgs = imgs/255.0
imgs = imgs.reshape(len(imgs), -1)
print(imgs.shape)

print("Starting fit...")

model.fit(imgs)
print("Done fitting")

#%%
labels = []
i = 0
for img in files:
    label = model.labels_[i]
    if label == 1:
        os.rename(img, "../bin/storage/" + img[19:])
        print("Moving image")
    i = i + 1

cv2.destroyAllWindows()


#print(imgs)
# %%
