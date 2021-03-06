import os
import sys
import re
import glob
import errno
import shutil
import random
import numpy as np
import cv2
import skimage
import skimage.io
import skimage.transform
import skimage.filters
import joblib



class imgUtils:
    
    
    
    def __init__(self):
        
        self.image_extension = ['.jpeg', '.jpg', '.png', '.tif', '.tiff',
                                '.JPEG', '.JPG', '.PNG', '.TIF', '.TIFF']
    
    
    
    def train_test_split(self, data_dirpath=None, output_dirpath=None, test_size=0.20):
        '''Split datasets into two subsets for training and test.
        
        The original directory should contains several sub-directories.
        Each sub-directories' nanme are the class label
        and each sub-directory should contains the images
        
        ```
        data_dirpath ----- class_1 ---- image01.jpg
                     |             |--- image02.jpg
                     |             \--- image03.png
                     |---- class_2 ---- image01.jpg
                     |             |--- image02.jpg
                     |             \--- image03.png
                     :                      :
        ```
        
        The output direcotry contains two sub-direcotries which named 'train' and 'test'.
        The 'train' and 'test' directories contains the sub-directoires which names indicate
        class labels, respectively.
        
        ```
        output_dirpath ----- train ----- class_1 ---- image01.jpg
                       |           |             \--- image02.jpg
                       |           |---- class_2 ---- image01.jpg
                       |           |             \--- image03.png
                       |           :                      :
                       ----- test  ----- class_1 ---- image03.png
                                   |             \--- image04.jpg
                                   |---- class_2 ---- image02.jpg
                                   |             \--- image04.png
                                   :                      :
        ```
        
        
        Args:
            data_dirpath (str): A path to a directory which contains whole datasets.
            output_dirpath (str): A path to a directory to store the split subsets.
            test_size (float): the ratio to split.
        '''
        
        
            
        if not os.path.exists(data_dirpath):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), data_dirpath)
        
        train_output_dirpath = os.path.join(output_dirpath, 'train')
        test_output_dirpath = os.path.join(output_dirpath, 'test')
        
        if not os.path.exists(train_output_dirpath):
            os.mkdir(train_output_dirpath)
            
        if not os.path.exists(test_output_dirpath):
            os.mkdir(test_output_dirpath)
        
        for class_label in os.listdir(data_dirpath):
            _train_output_dirpath = os.path.join(train_output_dirpath, class_label)
            _test_output_dirpath = os.path.join(test_output_dirpath, class_label)
        
            if not os.path.exists(_train_output_dirpath):
                os.mkdir(_train_output_dirpath)
            
            if not os.path.exists(_test_output_dirpath):
                os.mkdir(_test_output_dirpath)
            
            for ext in self.image_extension:
                for _f in glob.glob(os.path.join(data_dirpath, class_label, '*' + ext)):
                    if random.random() > test_size:
                        shutil.copy(_f, os.path.join(_train_output_dirpath, os.path.basename(_f)))
                    else:
                        shutil.copy(_f, os.path.join(_test_output_dirpath, os.path.basename(_f)))
        
    
    
    def parse_PascalVOC(self, file_path):
    
        objects = []
        img_shape = [None, None, None]
        object_dict = {'name': None, 'xmin': None, 'ymin': None, 'xmax': None, 'ymax': None}
        
        # regex for searching object's information
        re_width = re.compile(r'<width>([0-9]+)</width>')
        re_height = re.compile(r'<height>([0-9]+)</height>')
        re_depth = re.compile(r'<depth>([0-9]+)</depth>')
        re_name = re.compile(r'<name>(.+)</name>')
        re_xmin = re.compile(r'<xmin>([0-9]+)</xmin>')
        re_ymin = re.compile(r'<ymin>([0-9]+)</ymin>')
        re_xmax = re.compile(r'<xmax>([0-9]+)</xmax>')
        re_ymax = re.compile(r'<ymax>([0-9]+)</ymax>')
    
        # open Pascal VOC XML and read object information
        with open(file_path, 'r') as xmlfh:

            is_object_record = False
        
            for line in xmlfh:
                if not is_object_record:
                    m = re_width.search(line)
                    if m:
                        img_shape[0] = int(m.group(1))
                    m = re_height.search(line)
                    if m:
                        img_shape[1] = int(m.group(1))
                    m = re_depth.search(line)
                    if m:
                        img_shape[2] = int(m.group(1))
                    
                if '<object>' in line:
                    is_object_record = True
                    continue
            
                if '</object>' in line:
                    objects.append(object_dict)
                    object_dict = {'name': None, 'xmin': None, 'ymin': None, 'xmax': None, 'ymax': None}
                    is_object_record = False
                    continue
            
                if is_object_record:
                    m = re_name.search(line)
                    if m:
                        object_dict['name'] = m.group(1)

                    m = re_xmin.search(line)
                    if m:
                        object_dict['xmin'] = int(m.group(1))
    
                    m = re_ymin.search(line)
                    if m:
                        object_dict['ymin'] = int(m.group(1))
                
                    m = re_xmax.search(line)
                    if m:
                        object_dict['xmax'] = int(m.group(1))
                    
                    m = re_ymax.search(line)
                    if m:
                        object_dict['ymax'] = int(m.group(1))
                
        return {'shape': tuple(img_shape), 'objects': objects}
    
    
    
    
    
    def crop_images(self, file_path, objects, output_dirpath=None):
    
        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    
        if output_dirpath is None:
            raise ValueError('crop_images` function requires `output_dir` to save cropped images.')
    
        if not os.path.exists(output_dirpath):
            os.mkdir(output_dirpath)
    
        for obj in objects:
            class_label = obj[0]
        
            _output_dirpath = os.path.join(output_dirpath, class_label)
            if not os.path.exists(_output_dirpath):
                os.mkdir(_output_dirpath)
            
            _xmin = obj[1]
            _xmax = obj[3]
            _ymin = obj[2]
            _ymax = obj[4]
            img_cropped = img[_ymin:_ymax, _xmin:_xmax]
            
            cv2.imwrite(os.path.join(_output_dirpath, '_'.join(map(str, obj))) + '.png', img_cropped)
        
        


    def crop_blocks(self, file_path, objects, output_dirpath=None, block_size=3, n_blocks=1000):
    
        img = cv2.imread(file_path)
    
        if output_dirpath is None:
            raise ValueError('crop_blocks` function requires `output_dir` to save cropped images.')
    
        if not os.path.exists(output_dirpath):
            os.mkdir(output_dirpath)
    
        # grouped objects by class labels
        objects_dict = {}
        for obj in objects:
            if obj[0] not in objects_dict:
                objects_dict.update({obj[0]: []})
            objects_dict[obj[0]].append(obj)
        
        
        # crop blocks
        for class_label, object_list in objects_dict.items():
            
            # creat an empty directories to save cropped images
            _output_dirpath = os.path.join(output_dirpath, class_label)
            if not os.path.exists(_output_dirpath):
                os.mkdir(_output_dirpath)
            
            # crop a number of `n_blocks` blocks
            i = 0
            while  i < n_blocks:
                obj = random.choice(object_list)
                
                # skip small objects, too small to crop a block from the object
                if obj[4] - obj[2] < block_size or obj[3] - obj[1] < block_size:
                    continue
                
                # set start position for cropping
                yaxis = random.randint(obj[2], obj[4] - block_size)
                xaxis = random.randint(obj[1], obj[3] - block_size)
                
                # crop a block from an object
                img_cropped = img[yaxis:(yaxis + block_size), xaxis:(xaxis + block_size), :]
                
                # flip the cropped block
                random_num = random.random()
                if 0.25 < random_num and random_num <= 0.50:
                    img_cropped = cv2.flip(img_cropped, 0)
                elif 0.50 < random_num and random_num <= 0.75:
                    img_cropped = cv2.flip(img_cropped, 1)
                elif 0.75 < random_num and random_num <= 1:
                    img_cropped = cv2.flip(img_cropped, -1)
                
                output_img_name = '_'.join(map(str, obj)) + '_' + str(i) + '.png'
                cv2.imwrite(os.path.join(_output_dirpath, output_img_name), img_cropped)
            
                i += 1
        

    
    
    
    def __augmentation_rotation(self, img):
        r = np.random.rand(1)
        random_degree = random.uniform(0, 90)
        img = skimage.transform.rotate(img, random_degree, resize=True, cval=0)
        return img
    
    
    def __augmentation_flip(self, img):
        r = np.random.rand(1)
        if r < 1/3:
            img = img[:, ::-1, :]
        elif r < 2/3:
            img = img[::-1, :, :]
        return img
    
    
    def __augmentation_noise(self, img):
        r = np.random.rand(1)
        if r < 0.15:
            img = skimage.util.random_noise(img, mode='localvar')
        elif r < 0.30:
            img = skimage.util.random_noise(img, mode='salt')
        elif r < 0.45:
            img = skimage.util.random_noise(img, mode='s&p')
        elif r < 0.60:
            img = skimage.util.random_noise(img, mode='speckle', var=0.01)
        elif r < 0.75:
            img = skimage.util.random_noise(img, mode='poisson')
        elif r < 0.95:
            img = skimage.util.random_noise(img, mode='gaussian', var=0.01)
        img = img * 255
        img = img.astype(np.uint8)
        return img
    
    
    def __augmentation_generate_background(self, img):
        bg_img = self.__augmentation_flip(img)
        
        # crop background image
        x0 = random.randint(0, int(bg_img.shape[0] / 3))
        x1 = random.randint(int(2 * bg_img.shape[0] / 3), bg_img.shape[0])
        y0 = random.randint(0, int(bg_img.shape[1] / 3))
        y1 = random.randint(int(2 * bg_img.shape[1] / 3), bg_img.shape[1])
        bg_img = bg_img[x0:x1, y0:y1]
            
        # resize background image
        w = random.randint(int(bg_img.shape[0] * 5), bg_img.shape[0] * 8)
        h = random.randint(int(bg_img.shape[1] * 5), bg_img.shape[1] * 8)
        bg_img = skimage.transform.resize(bg_img, (w, h), mode='constant')
        
        # rotate background image
        bg_img = self.__augmentation_rotation(bg_img)
       
        # filter
        r = np.random.rand(1)
        if r > 0.5:
            bg_img = skimage.filters.gaussian(bg_img, sigma=random.uniform(0.5, 2.0), multichannel=True)
        
        return bg_img
 


       
    def __zero_padding(self, v, w, iaxis, kwargs):
        v[:w[0]] = 0.0
        v[-w[1]:] = 0.0
        return v
            
        
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
         
        img_constant = cv2.copyMakeBorder(img, top, bottom, left, right,
                                          cv2.BORDER_CONSTANT, value=[0, 0, 0])   
        return img_constant
        
        
        
    def __augmentation_fill_background(self, img, bg_img_tmpl):
        
       
        
        block_size = img.shape[0] if img.shape[0] > img.shape[1] else img.shape[1]
        
        # get background and crop it to nxn sizes block
        bg_img = self.__augmentation_generate_background(bg_img_tmpl)
        x0 = int((bg_img.shape[0] - block_size) / 2)
        x1 = x0 + block_size
        y0 = int((bg_img.shape[1] - block_size) / 2)
        y1 = y0 + block_size
        bg_img = bg_img[x0:x1, y0:y1]
        
        img = self.__get_padding(img)
        
        # make mask
        mask = skimage.color.rgb2gray(img)
        mask = np.pad(skimage.transform.resize(mask, (mask.shape[0] - 10, mask.shape[1] - 10), mode='constant'),
                      5, self.__zero_padding)
        
        img[mask < 0.001] = bg_img[mask < 0.001]
        return img
        
        
    
    
    def augmentation_ss(self, input_path=None, output_dirpath=None, n=100, output_prefix='augmented_image'):
        
        
        if os.path.isfile(input_path):
            image_files = [input_path]
        elif os.path.isdir(input_path):
            image_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f))]
        else:
            raise ValueError('Unknown types of this file: ' + input_path + '.')
        
        n = n + 1
        i = 1
        while i < n:
            
            # randomly chose an image from the directory
            image_path = random.choice(image_files)
            
            img = skimage.io.imread(image_path)[:, :, :3]
            
            # randomly rotation
            img_ag = self.__augmentation_rotation(img)
            
            # fill up background (some case can not perform zero-padding)
            _img_ag = self.__augmentation_fill_background(img_ag, img)
            if _img_ag is None:
                print('==> aug found None image in __augmentation_fill_background: ' + input_path + '.')
                _img_ag = img_ag
            img_ag = _img_ag

           
            # randomly reflection
            img_ag = self.__augmentation_flip(img_ag)
            
            # randomly add noises
            img_ag = self.__augmentation_noise(img_ag)
            
            new_file_path = os.path.join(output_dirpath, output_prefix + '_' + str(i) + '.png')
            skimage.io.imsave(new_file_path, img_ag)
            
            i = i + 1



    
    def augmentation(self, input_path=None, output_dirpath=None, n=100, output_prefix='augmented_image', n_jobs=-1):
        
        if os.path.isfile(input_path):
            image_files = [input_path]
        elif os.path.isdir(input_path):
            image_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f)) and (not f.startswith('.'))]
        else:
            raise ValueError('Unknown types of this file: ' + input_path + '.')
        
        
        def __augmentation_ss(i):
            # randomly chose an image from the directory
            img_file = random.choice(image_files)
            img = skimage.io.imread(img_file)[:, :, :3]
            
            # randomly rotation
            img_ag = self.__augmentation_rotation(img)
            
            # fill up background (some case can not perform zero-padding)
            try:
                img_ag = self.__augmentation_fill_background(img_ag, img)
            except:
                print('image: ' + img_file)
            
            # randomly reflection
            img_ag = self.__augmentation_flip(img_ag)
            
            # randomly add noises
            img_ag = self.__augmentation_noise(img_ag)
            
            new_file_path = os.path.join(output_dirpath, output_prefix + '_' + str(i) + '.png')
            skimage.io.imsave(new_file_path, img_ag)
        
        
        r = joblib.Parallel(n_jobs=n_jobs, verbose=0)([joblib.delayed(__augmentation_ss)(i + 1) for i in range(n)])




    def synthesis(self, input_path=None, bg_path=None, output_dirpath=None, n=100, output_prefix='synthetic_image', n_jobs=-1):
        
        mask_image_files = []
        bg_image_files = []
        
        
        # make mask image list for random sampling afterward
        if os.path.isfile(input_path):
            mask_image_files = [input_path]
        elif os.path.isdir(input_path):
            mask_image_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f)) and (not f.startswith('.'))]

        # make background image list for random sampling afterward
        if os.path.isfile(bg_path):
            bg_image_files = [bg_path]
        elif os.path.isdir(bg_path):
            bg_image_files = [os.path.join(bg_path, f) for f in os.listdir(bg_path) if os.path.isfile(os.path.join(bg_path, f)) and (not f.startswith('.'))]
        
        def __synthesis_ss(i):
            # load images to objects
            mask_image_file = random.choice(mask_image_files)
            bg_image_file = random.choice(bg_image_files)
            mask_image = skimage.io.imread(mask_image_file)[:, :, :3]
            bg_image = skimage.io.imread(bg_image_file)[:, :, :3]
            
        
            img_ag = self.__augmentation_rotation(mask_image)
            try:
                img_ag = self.__augmentation_fill_background(img_ag, bg_image)
            except:
                print('maskimage: ' + mask_image_file)
                print('bgimage: ' + bg_image_file)
                print(bg_image.shape)
                print(img_ag.shape)
                print('--------')
            
            img_ag = self.__augmentation_flip(img_ag)
            img_ag = self.__augmentation_noise(img_ag)
            
            new_file_path = os.path.join(output_dirpath, output_prefix + '_' + str(i) + '.png')
            skimage.io.imsave(new_file_path, img_ag)
            
        
        r = joblib.Parallel(n_jobs=n_jobs, verbose=0)([joblib.delayed(__synthesis_ss)(i + 1) for i in range(n)])

        
    
    
    def resize(self, input_path, size = (1024, 768), output_dirpath=None, output_prefix='resized_image', n_jobs=-1):
        
       
        def __resize(img_path, size, output_dirpath, output_prefix):
            print(img_path)
            # open the original image
            img_original = skimage.io.imread(img_path)[:, :, :3]
            h, w, c = img_original.shape
            
            resize_ratio = None
            if max(h, w) == h:
                resize_ratio = size[1] / h
            else:
                resize_ratio = size[0] / w
        
            # resize the original image to target size
            img = skimage.transform.rescale(img_original, resize_ratio, mode='reflect', anti_aliasing=True, multichannel=True)
        
            # make background
            img_original_2x = skimage.transform.rescale(img_original, 1.5, mode='reflect', anti_aliasing=True, multichannel=True)
            bg_img = self.__augmentation_generate_background(img_original_2x)
            bh, bw, bc = bg_img.shape
            block_size = img.shape[0] if img.shape[0] > img.shape[1] else img.shape[1]
            x0 = int((bg_img.shape[0] - block_size) / 2)
            x1 = x0 + block_size
            y0 = int((bg_img.shape[1] - block_size) / 2)
            y1 = y0 + block_size
            bg_img = bg_img[x0:x1, y0:y1]
        
            # synthesis
            img = self.__get_padding(img)
            mask = skimage.color.rgb2gray(img)
            mask = np.pad(skimage.transform.resize(mask, (mask.shape[0] - 2, mask.shape[1] - 2), mode='constant'),
                          1, self.__zero_padding)
            img[mask < 0.001] = bg_img[mask < 0.001]
        
            # print out resized image
            if output_dirpath is None:
                output_dirpath = ''
            new_file_path = os.path.join(output_dirpath, output_prefix + '_' + os.path.basename(img_path))
            skimage.io.imsave(new_file_path, img)
        
            # print out xml, if given
            xml_path = os.path.splitext(img_path)[0] + '.xml'
            new_file_path = os.path.join(output_dirpath, output_prefix + '_' + os.path.basename(xml_path))
            print(new_file_path)
            if xml_path is not None:
                # shift
                if max(h, w) == h:
                    shift_h = 0
                    shift_w = (h - w) * resize_ratio / 2
                else:
                    shift_w = 0
                    shift_h = (w - h) * resize_ratio / 2
                
                re_width = re.compile(r'<width>([0-9]+)</width>')
                re_height = re.compile(r'<height>([0-9]+)</height>')
                re_xmin = re.compile(r'<xmin>([0-9]+)</xmin>')
                re_xmax = re.compile(r'<xmax>([0-9]+)</xmax>')
                re_ymin = re.compile(r'<ymin>([0-9]+)</ymin>')
                re_ymax = re.compile(r'<ymax>([0-9]+)</ymax>')
                with open(xml_path, 'r') as inxml, open(new_file_path, 'w') as outxml:
                    for buf in inxml:
                        v = None
                        if '<width>' in buf:
                            v = re_width.search(buf).group(1)
                            buf = buf.replace(v, str(img.shape[1]))
                        elif '<height>' in buf:
                            v = re_height.search(buf).group(1)
                            buf = buf.replace(v, str(img.shape[0]))
                        elif 'xmin' in buf:
                            v = re_xmin.search(buf).group(1)
                            buf = buf.replace(v, str(int(int(v) * resize_ratio + shift_w)))
                        elif 'xmax' in buf:
                            v = re_xmax.search(buf).group(1)
                            buf = buf.replace(v, str(int(int(v) * resize_ratio + shift_w)))
                        elif 'ymin' in buf:
                            v = re_ymin.search(buf).group(1)
                            buf = buf.replace(v, str(int(int(v) * resize_ratio + shift_h)))
                        elif 'ymax' in buf:
                            v = re_ymax.search(buf).group(1)
                            buf = buf.replace(v, str(int(int(v) * resize_ratio + shift_h)))
                    
                        outxml.write(buf)
                     
        
               
        image_files = []
        if os.path.isfile(input_path):
            image_files = [input_path]
        elif os.path.isdir(input_path):
            print(input_path)
            for f in os.listdir(input_path):
                if os.path.splitext(f)[1] in self.image_extension:
                    image_files.append(os.path.join(input_path, f))
        
        r = joblib.Parallel(n_jobs=n_jobs, verbose=0)([joblib.delayed(__resize)(image_file, size,
                        output_dirpath, output_prefix) for image_file in image_files])
            
            

if __name__ == '__main__':
    
    pass
    
    



