# Single Class Label Tool

1. Edit ```predefined_classes.txt``` to include your desired class names, before starting ```label.py``` or ```batch-label.py```.  
2. Select image directory and annotation file.  
   * Images will be listed in ```Image Files``` list.  
   * If annotation file already exists, it'll be loaded. When you click on the image with annotation, its label will be selected.  
2. When you press ```Prev``` or ```Next```, annotation file will be saved if ```Auto Save``` is enabled.  
   * **Note. When navigating with ```Image Files``` list, annotation file will NOT be saved automatically even ```Auto Save``` is enabled.**  

## label.py

Label images one by one.  

startup:  

```
python label.py
```

## batch-label.py

Label batches of images.  

startup:  

```
python batch-label.py
```

You could expand the current selected label to other unlabeled images in the batch.  
All labels in the batch could be cleared by pressing ```Clear```.  
To show count of each class, press ```Statistics```.  
