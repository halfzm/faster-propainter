
import os
import tempfile

import globals
from pre_post_process import crop_video_mask, merge_videos_with_mask
from watermark import pipeline


def resolve_relative_path(path: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

def start(crop=True) -> None:

    with tempfile.TemporaryDirectory() as tmpdir:
        # tmpdir = "./tmp" # 调试的时候便于查看输入图像

        video_fp = resolve_relative_path(globals.source_path)
        mask_fp = resolve_relative_path(globals.target_path)
        out_fp = resolve_relative_path(tmpdir)
        if crop:
            cropped_video_fp = os.path.join(tmpdir, "cropped_video.mp4")
            cropped_mask_fp = os.path.join(tmpdir, "cropped_mask.png")
            mask_x, mask_y, mask_w, mask_h = crop_video_mask(
                video_fp, mask_fp, cropped_video_fp, cropped_mask_fp
            )
            pipeline(
                cropped_video_fp,
                cropped_mask_fp,
                out_fp,
                fp16=True,
                mask_dilation=4,
                subvideo_length=80,
                neighbor_length=20,
            )
        else:
            out_fp = os.path.join(globals.output_path)
            pipeline(
                video_fp,
                mask_fp,
                out_fp,
                fp16=True,
                mask_dilation=4,
                subvideo_length=80,
                neighbor_length=20,
            )


        if crop:
            video_name = os.path.basename(cropped_video_fp).split(".")[0]
            impaint_video_fp = os.path.join(tmpdir, video_name, "inpaint_out.mp4")
            out_fp = os.path.join(globals.output_path, "output.mp4")
            merge_videos_with_mask(
                video_fp,
                mask_fp,
                impaint_video_fp,
                cropped_mask_fp,
                out_fp,
                mask_x,
                mask_y,
                mask_w,
                mask_h,
            )


if __name__ == "__main__":
    start()
