import os
import glob
import pickle
import numpy as np
import sklearn
import cv2
import keras




class nnBatchGenerator(keras.utils.Sequence):

    def __init__(self, data, image_shape, batch_size=64):

        self.x = data[0]
        self.y = data[1]
        self.length = len(data[0])

        self.batch_size = batch_size
        self.image_shape = image_shape
        self.batches_per_epoch = int((self.length - 1) / batch_size) + 1



    def __getitem__(self, idx):

        batch_from = self.batch_size * idx
        batch_to   = batch_from + self.batch_size

        if batch_to > self.length:
            batch_to = self.length

        x_batch = []
        y_batch = []
        for i in range(batch_from, batch_to):
            _x = cv2.imread(self.x[i], cv2.IMREAD_COLOR)
            _x = self.preprocess(_x)
            x_batch.append(_x)
            y_batch.append(self.y[i])

        x_batch = np.asarray(x_batch)
        x_batch = x_batch.astype('float32') / 255.0

        y_batch = np.asarray(y_batch)

        return x_batch, y_batch



    def __len__(self):
        return self.batches_per_epoch





    def __get_padding(self, img):
        h, w, c = img.shape
        longest_edge = max(h, w)
        top = 0
        bottom = 0
        left = 0
        right = 0
        if h < longest_edge:
            diff_h = longest_edge - h
            top = diff_h // 2
            bottom = diff_h - top
        elif w < longest_edge:
            diff_w = longest_edge - w
            left = diff_w // 2
            right = diff_w - left
        else:
            pass

        img = cv2.copyMakeBorder(img, top, bottom, left, right,
                                 cv2.BORDER_CONSTANT, value=[0, 0, 0])
        return img



    def preprocess(self, img):
        img = self.__get_padding(img)
        img = cv2.resize(img, self.image_shape[:2])
        return img


    def on_epoch_end(self):
        pass







class nnBase:
    
        
    
    def __init__(self, base_object=None, image_shape=None, best_model=None, debug=False):
        
        if base_object is None:
            # variables for datasets
            self.data_path = {'training': None, 'validation': None, 'test': None}
            self.class_labels = None
            self.train_batches = None
            self.train_data = None
            self.test_batches = None
            self.test_data = None
            self.__class_label_dict = None
            self.fit_history = None
            
            self.image_shape = None
            if image_shape is None:
                raise ValueError('nnBase class initializer requires `image_shape` argument.')
            else:
                if len(image_shape) != 3:
                    raise ValueError('`image_shape` argument should be a list with 3 elements which are width, height, and channels.')
                else:
                    self.image_shape = image_shape

            self.model = None

            self.image_extension = ['jpeg', 'jpg', 'png', 'tif', 'tiff',
                                    'JPEG', 'JPG', 'PNG', 'TIF', 'TIFF']
            self.debug = debug

        else:
            # load nnBase class object from file
            with open(base_object, 'rb') as infh:
                _self = pickle.load(infh)

                self.data_path = _self.data_path
                self.class_labels = _self.class_labels
                self.train_batches = _self.train_batches
                self.train_data = _self.train_data
                self.test_batches = _self.test_batches
                self.test_data = _self.test_data
                self.__class_label_dict = _self.__class_label_dict
                self.fit_history = _self.fit_history
                self.model = _self.model
                self.image_shape = _self.image_shape
                self.image_extension = _self.image_extension
                self.debug = _self.debug

            if best_model is not None:
                self.model = keras.models.load_model(best_model)


    
    
    def __load_data(self, data_path, class_label=None):

        x = []
        y = []

        # if class_label is not given, then create it according to the directory names
        if class_label is None:
            class_label = sorted(os.listdir(data_path))

        # load data from all directories
        for _i, _d in enumerate(class_label):

            # skip if this is file
            if os.path.isfile(_d):
                continue

            # only load images from the target directory
            for ext in self.image_extension:
                for _f in glob.glob(os.path.join(data_path, _d, '*.' + ext)):
                    x.append(_f)
                    y.append(_i)
        
        
        # change images to array
        x = np.asarray(x)

        # change labels to array
        y = np.asarray(y)
        y = keras.utils.np_utils.to_categorical(y, num_classes=len(class_label))

        return [x, y, class_label]
    
    
    
    def __load_data_predict(self, data_path):
        
        x = []
        
        for ext in self.image_extension:
            for _f in glob.glob(os.path.join(data_path, '*' + ext)):
                x.append(_f)
            for _f in glob.glob(os.path.join(data_path, '*', '*' + ext)):
                x.append(_f)
            
        x = np.asarray(x)
        
        return x
        
    
    
    


    def load_data(self, data_path=None, dataset=None):

        if dataset is None:
            raise ValueError('Specify `train` or `predict` for `dataset` argument.')
        if data_path is None:
            raise ValueError('`load_data` method requires `data_path` argument.')
        
        self.data_path = data_path

        # load training data set
        if dataset == 'train':
            if not os.path.exists(data_path):
                raise ValueError('`load_data` method could not find train data set, set train data set in a `train` directory in ' + data_path)
            
            x, y, class_label = self.__load_data(data_path, None)
            self.train_data = [x, y]
            self.class_labels = class_label

        
        # load data for prediction
        if dataset == 'predict':
            if not os.path.exists(data_path):
                raise ValueError('`predict` method could not find data set for prediction, check the directory and put the data into the directory in ' + data_path)
            x = self.__load_data_predict(data_path)
            self.predict_data = [x, None]
    
    
    
    def load_model(self, model_path=None):
        print('The original model has been replaced with the model (' + model_path + ').')
        self.model = keras.models.load_model(model_path)
        
    
    

    def save(self, file_path=None):

        if file_path is None:
           raise ValueError('`save_model` method requires `file_path` argument.')

        with open(file_path, 'wb') as outfh:
            pickle.dump(self, outfh)





