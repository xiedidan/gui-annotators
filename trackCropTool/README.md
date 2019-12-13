# Track Crop Tool

Automatically crop target from video frames, with a startup bbox and a tracker.  
Class label could be assigned to target.  

Provided a anchor bbox, tracker will track forward and backward, to extract as many frames as possible.  
So we are creating target sequence in video time space.  

## GUI  

### 1. Paths  
   * Video Path - contains multiple video clips  
   * Metadata Path - save metadata for each video file  

### 2. Video List  
   * Specify video path with multiple video files, and videos will be list in ```Video List```.  

### 3. Sequence List  
   If metadata could be found for current video, sequences will be automatically loaded.  
   * Sequence CRUD operations.  

### 4. Sequence Details  
   * BBox scale  
   * Predefined Label List
   * Online Tracker Tuning:
      * Tracker Selector  
      * Confidence Threshold  
      * NMS Threshold  
   * Frame Info  
      * Anchor  
      * Start (Auto or Specified)  
      * End (Auto or Specified)  
   * Crop Preview  
      * Crop Grid  
      * Page Slide  
      * Drop Crop

### 5. Preview Window  
   * Preview  
      * Actual BBox / Scaled BBox  
      * Sequence ID  
      * Tracker Confidence  
   * Anchor BBox Selection  

### 6. Preview Control  
   * Simple Video Control  
      * Play  
         * Forward  
         * Rewind  
         * Pause  
      * Jump  
         * Insert  
         * Exit  
         * Anchor  
      * Speed Grid  
         * Slow (2x, 3x, 4x, 5x or specified)  
         * Fast (2x, 3x, 4x, 5x or specified)  
      * Current / Total Frame Display  
      * Frame Locator  
         * Anchor
         * Start  
         * End  
      * Frame Slide  

### 7. Control Box  
   * Mode  
      * Grayscale  
   * Clear  
      * Current - clear all sequences in current video  
      * All - clear all sequences in all videos  
   * Save  
      * Current - save current metadata  
      * All - save all metadata  
