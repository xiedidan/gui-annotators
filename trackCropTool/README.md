# Track Crop Tool

Automatically crop target from video frames, with a startup bbox and a tracker.  
Class label could be assigned to target.  

## 1. Paths  
   * Video Path - contains multiple video clips  
   * Metadata Path - save metadata for each video file  
   * Output Path - root path of exported crops and label lists  

## 2. Video List  
   * Specify video path with multiple video files, and videos will be list in ```Video List```.  

## 3. Target List  
   If metadata could be found for current video, targets will be automatically loaded.  
   * Target CRUD operations.  

## 4. Target Details  
   * Initial BBox  
   * Predefined Label List
   * Online Tracker Tuning:
      * Confidence Threshold  
      * NMS Threshold  
   * Frame Locator  
      * Start  
      * End (Auto or Specified)  
   * Crop Preview  
      * Crop Grid  
      * Page Slide  
      
## 5. Track Preview  
   * Preview  
      * BBox  
      * Target ID  
      * Tracker Confidence  
   * Simple Video Control  
      * Start  
      * Pause  
      * Stop  
      * Speed Grid  
         * Slow (2x, 3x, 4x, 5x or specified)  
         * Fast (2x, 3x, 4x, 5x or specified)  
      * Frame Slide
      * Current / Total Frame Display

## 6. Control Box  
   * Clear  
      * Current - clear all targets in current video  
      * All - clear all targets in all videos  
   * Save  
      * Current - save current metadata  
      * All - save all metadata  
   * Export 
      * Current - export current crops  
      * All - export all crops in all videos  
