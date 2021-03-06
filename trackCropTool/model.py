class Sequence:
    def __init__(
        self,
        label='',
        bbox_scale=1.0,
        tracker_name='kcf',
        anchor_bbox=[], # x, y, w, h
        anchor=0,
        insert=0,
        exit=0,
        grayscale=False
        ):
        self.label = label
        self.bbox_scale = bbox_scale
        self.tracker_name = tracker_name

        self.anchor_bbox = anchor_bbox
        self.anchor = anchor
        
        self.insert = insert
        self.exit = exit

        self.grayscale = grayscale

    def __str__(self):
        return '{}, {}, {}, {}'.format(
            self.label,
            self.tracker_name,
            self.anchor,
            self.anchor_bbox
        )
        