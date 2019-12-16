class Sequence:
    def __init__(
        self,
        label='',
        bbox_scale=1.0,
        tracker_name='kcf',
        anchor_bbox=[], # x, y, w, h
        anchor=0,
        insert=0,
        exit=0
        ):
        self.label = label
        self.bbox_scale = bbox_scale
        self.tracker_name = tracker_name
        self.anchor = anchor
