# dashproc
Dashcam video processing

Please modify the following cmmand to obtain random video snippets from a sequence of innovv k5 videos.

```
from process import process

process(dir="/Users/dpadmana/Documents/RoadTrips/Conoor - 202401/",
        CD=5,
        title="Conoor - 202401",
        audio_loc="clip/conoor.mp3",
        final_loc="clip/random.mp4",
        final_height=1080)

```

Please modify the following cmmand to obtain selected video snippets from a sequence of innovv k5 videos, where you specify start and end times. You can also add images in this particular method to display between videos, as per the sequence in the array.

```
from process import process_manual

dir="/Users/dpadmana/Documents/RoadTrips/Honnavar - 202311/"
x=[]
x.append(dict({"type":"image","name":dir+"pics/WhatsApp Image 2023-11-04 at 10.52.22.jpeg"}))
x.append(dict({"type":"video","name":dir+"2023_1103_060826_R.MP4","st":40,"et":43}))
x.append(dict({"type":"image","name":dir+"pics/WhatsApp Image 2023-11-04 at 10.52.22 (1).jpeg"}))
x.append(dict({"type":"image","name":dir+"pics/WhatsApp Image 2023-11-04 at 10.52.22 (2).jpeg"}))
x.append(dict({"type":"video","name":dir+"2023_1103_081519_FG.MP4","st":1,"et":3}))


process_manual(x,
        title="Kundapur/Honnavar - Nov 2023",
        audio_loc=dir+"clip/honnavar.mp3",
        final_loc=dir+"clip/select.mp4",
        final_height=1080)

```

You could modify the exif processing utilities in `mapvid.py` to work with other dashcams or action cams like go pro or insta360.
