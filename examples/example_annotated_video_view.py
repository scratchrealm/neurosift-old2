from typing import List
import numpy as np
import figneuro.misc.views as mv
import kachery_cloud as kcl
import cv2

# 228 MB
camera_ogv_uri = 'sha1://93600401859d5c45a48c49b78034214b4106ad28?label=2021_08_10_15_10_41_494305_cam_b.ogv'

nose_annotations_npy_uri = 'sha1://e2f20d56d6e4ecbce18112027a8cc13e3554d3ac?label=nose_annotations_noInterp.npy'
butt_annotations_npy_uri = 'sha1://d35f0f5a6deceb49c3fd0528ee52566a804ccd37?label=butt_annotations_noInterp.npy'
head_annotations_npy_uri = 'sha1://e1c57fb7dac7c493db5b884d43c819763011a779?label=head_annotations_noInterp.npy'


def main():
    V = create_annotated_video_view()
    

def create_annotated_video_view():
    ogv_fname = kcl.load_file(camera_ogv_uri)

    vid = cv2.VideoCapture(ogv_fname)
    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = vid.get(cv2.CAP_PROP_FPS)
    num_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f'height/width: {height}/{width}')
    print(f'fps: {fps}')
    print(f'num_frames: {num_frames}')

    head_annotations = kcl.load_npy(head_annotations_npy_uri).astype(np.float32)
    butt_annotations = kcl.load_npy(butt_annotations_npy_uri).astype(np.float32)
    nose_annotations = kcl.load_npy(nose_annotations_npy_uri).astype(np.float32)

    annotation_frames: List[mv.AnnotationFrame] = []
    for j in range(num_frames):
        elements: List[mv.AnnotationElement] = []
        p_head = head_annotations[j]
        p_butt = butt_annotations[j]
        p_nose = nose_annotations[j]
        if not np.isnan(p_head[0]):
            elements.append(mv.NodeElement('h', x=p_head[0], y=p_head[1]))
        if not np.isnan(p_butt[0]):
            elements.append(mv.NodeElement('b', x=p_butt[0], y=p_butt[1]))
        if not np.isnan(p_nose[0]):
            elements.append(mv.NodeElement('n', x=p_nose[0], y=p_nose[1]))
        if not np.isnan(p_nose[0]) and not np.isnan(p_head[0]):
            elements.append(mv.EdgeElement('n-h', id1='n', id2='h'))
        if not np.isnan(p_head[0]) and not np.isnan(p_butt[0]):
            elements.append(mv.EdgeElement('h-b', id1='h', id2='b'))
        F = mv.AnnotationFrame(elements=elements)
        annotation_frames.append(F)
    annotations_uri = mv.create_annotations_uri(annotation_frames)

    nodes: List[mv.AnnotatedVideoNode] = [
        mv.AnnotatedVideoNode(id='n', label='nose', color_index=0),
        mv.AnnotatedVideoNode(id='h', label='head', color_index=1),
        mv.AnnotatedVideoNode(id='b', label='butt', color_index=2)
    ]

    V = mv.AnnotatedVideo(
        video_uri=camera_ogv_uri,
        video_width=width,
        video_height=height,
        video_num_frames=num_frames,
        sampling_frequency=fps,
        annotations_uri=annotations_uri,
        nodes=nodes
    )
    return V

if __name__ == '__main__':
    main()