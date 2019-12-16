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

## Design  

### 1. Loop  
There are 2 event loops:  
   1. cv2 window event loop - which requires at least cv2.waitKey(1)  
   2. GUI event loop  

Let's put cv2 window into a track-and-render (TAR) process and leave GUI in main process.  
They talk with each other with python queues.  
Main process sends commands and parameters, while TAR process sends progress and roi selected by user.  
Refresh intervals are seperate in these processes.  

However, for main process, window reading must be non-blocking, since TAR process will send progress info to drive GUI.  

### 2. MVP  
Model-View-Presenter pattern is used.  
The presenter handles GUI event and updates model in actions. It also renders model to GUI in binders.  
Presenter holds both view and model, so actions and binders could visit any info they needed.  
Binder functions are implemented as decorators (to decorate actions).  
In this way, we bind rendering to model updating.  
