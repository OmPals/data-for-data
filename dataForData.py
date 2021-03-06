# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VY-BSEvpP0nhXl5j5Pe_DcqqI6sgD9OW
"""

from google.colab import drive
drive.mount('/content/drive')

from keras.models import Sequential
from keras.models import Model
from keras.layers import *
from keras.layers import Convolution2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.preprocessing.image import ImageDataGenerator
from matplotlib import pyplot as plt
import numpy as np
from keras.preprocessing import image
from keras.layers import LeakyReLU
from keras.datasets import mnist
from keras.optimizers import Adam
from PIL import Image
import glob
import cv2

class GAN():
    def __init__(self):
        self.img_rows = 28
        self.img_cols = 28
        self.channels = 1
        self.img_shape = (self.img_rows, self.img_cols, self.channels, 1)

        optimizer = Adam(0.0002, 0.5)

        #discriminator
        self.discriminator = self.build_discriminator()
        self.discriminator.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

        #generator
        print("Generator is initialized")
        self.generator = self.build_generator()
        
        self.generator.compile(loss='binary_crossentropy', optimizer=optimizer)

        z = Input(shape=(100,))
        img = self.generator(z)
        #img = Image.open("/content/drive/My Drive/ice_cream_1/image_hi001.jpg")

        self.discriminator.trainable = False

        valid = self.discriminator(img)

        self.combined = Model(z, valid)
        self.combined.compile(loss='binary_crossentropy', optimizer=optimizer)

    def build_generator(self):

        noise_shape = (100,)

        model = Sequential()

        model.add(Dense(256, input_shape=noise_shape))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(512))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(1024))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(np.prod(self.img_shape), activation='tanh'))
        model.add(Reshape(self.img_shape))

        model.summary()

        noise = Input(shape=noise_shape)
        img = model(noise)

        return Model(noise, img)

    def build_discriminator(self):

        img_shape = (self.img_rows, self.img_cols, self.channels)

        model = Sequential()

        model.add(Flatten(input_shape=img_shape))
        model.add(Dense(512))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dense(256))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dense(1, activation='sigmoid'))
        model.summary()

        img = Input(shape=img_shape)
        validity = model(img)
        print("Validity:"+ str(validity))

        return Model(img, validity)

    def train(self, epochs, batch_size, save_interval):
        (X_train, Y_train), (X_test, Y_test) = mnist.load_data()
        print(X_train)
        # X_train=X_train[1]
        # print("Let's see what the f**k happens!")
        # print(X_train)
        print(X_train.shape)
        X_train=np.asarray(X_train)#[X_train.astype(int)]
      #  X_train = (X_train.astype(np.float32) - 127.5) / 127.5
      #  X_train=X_train.reshape(X_train,(28,28,1))
        #X_test=X_test.reshape([-1,28,28,1])
        print(X_train)
        print(X_train.shape)
        # X_train = np.expand_dims(X_train, axis=3)
        # #print(X_train)
        #print(X_train.shape)
        #X_train_l = [cv2.imread(file) for file in glob.glob("/content/drive/My Drive/ice_cream_1/*")]
        #X_train=np.array(X_train_l)
        half_batch = int(batch_size / 2)

        for epoch in range(epochs):

            #dicriminator training
            idx = np.random.randint(0, X_train.shape[0], half_batch, dtype='int')
            imgs = X_train[idx]
            noise = np.random.normal(0, 1, (half_batch, 100))
            gen_imgs = self.generator.predict(noise)

            d_loss_real = self.discriminator.train_on_batch(imgs,np.ones(half_batch),0,0)
            d_loss_fake = self.discriminator.train_on_batch(gen_imgs, np.zeros(half_batch))
            d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

            #generator training
            noise = np.random.normal(0, 1, (batch_size, 100))
            valid_y = np.array([1] * batch_size)

            g_loss = self.combined.train_on_batch(noise, valid_y)

            print ("%d [D loss: %f, acc.: %.2f%%] [G loss: %f]" % (epoch, d_loss[0], 100*d_loss[1], g_loss))

            if epoch % save_interval == 0:
                self.save_imgs(epoch)

    def save_imgs(self, epoch):
        r, c = 5, 5
        noise = np.random.normal(0, 1, (r * c, 100))
        gen_imgs = self.generator.predict(noise)

        gen_imgs = 0.5 * gen_imgs + 0.5

        fig, axs = plt.subplots(r, c)
        cnt = 0
        for i in range(r):
            for j in range(c):
                axs[i,j].imshow(gen_imgs[cnt, :,:,0], cmap='gray')
                axs[i,j].axis('off')
                cnt += 1
                fig.savefig("D:/hack_img_%d.png" % epoch)
                plt.close()

if __name__ == '__main__':
    gan = GAN()
    gan.train(epochs=1, batch_size=120000, save_interval=200)