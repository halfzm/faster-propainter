import cv2
import scipy
import numpy as np
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import crop


def find_bounding_box(mask):
    # 将灰度图像转换为二值图像
    binary_mask = np.where(mask > 0, 1, 0)

    # 找到有像素的点的坐标
    nonzero_indices = np.nonzero(binary_mask)
    x_coords = nonzero_indices[1]
    y_coords = nonzero_indices[0]

    # 找到最左坐标、最右坐标、最上坐标和最下坐标
    min_x = np.min(x_coords)
    max_x = np.max(x_coords)
    min_y = np.min(y_coords)
    max_y = np.max(y_coords)

    return min_x, max_x, min_y, max_y


def crop_mask(mask, x, y, w, h, out_fp):
    cropped_image = mask[y : y + h, x : x + w]
    cv2.imwrite(out_fp, cropped_image)


def crop_video_mask(
    video_fp,
    mask_fp,
    cropped_video_fp="./cropped_video.mp4",
    cropped_mask_fp="./cropped_mask.png",
):
    # 读取蒙版文件
    mask = cv2.imread(mask_fp, cv2.IMREAD_GRAYSCALE)
    full_height, full_width = mask.shape

    # 找到蒙版对应的最小矩形框
    min_x, max_x, min_y, max_y = find_bounding_box(mask)
    min_width = max(128, max_x - min_x)
    min_height = max(128, max_y - min_y)
    original_width = max_x - min_x
    original_height = max_y - min_y
    shift_x = abs(original_width - min_width) // 2 + int(original_width * 0.2)
    shift_y = abs(original_height - min_height) // 2 + int(original_height * 0.2)
    x = max(0, min_x - shift_x)
    y = max(0, min_y - shift_y)
    w = min(max_x - min_x + shift_x * 2, full_width)
    h = min(max_y - min_y + shift_y * 2, full_height)
    w = w - w % 16
    h = h - h % 16

    # 保存裁剪后的蒙版
    cropped_image = mask[y : y + h, x : x + w]
    cv2.imwrite(cropped_mask_fp, cropped_image)

    # 读取视频文件、裁剪并保存
    video_clip = VideoFileClip(video_fp)
    video_clip = crop(video_clip, x1=x, y1=y, x2=x + w, y2=y + h)
    video_clip.write_videofile(cropped_video_fp, logger=None)

    return x, y, w, h


def merge_videos_with_mask(
    bg_video_fp, bg_mask_fp, fg_video_fp, fg_mask_fp, output_path, x, y, w, h
):
    # 打开视频A和视频B
    cap_bg = cv2.VideoCapture(bg_video_fp)
    cap_fg = cv2.VideoCapture(fg_video_fp)

    # 检查视频A和视频B是否成功打开
    if not cap_bg.isOpened() or not cap_fg.isOpened():
        raise ValueError("无法打开视频文件")

    # 获取视频A和视频B的帧率和尺寸
    fps = cap_bg.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap_bg.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap_bg.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 读取蒙版文件
    mask_bg = cv2.imread(bg_mask_fp, cv2.IMREAD_GRAYSCALE)
    mask_fg = cv2.imread(fg_mask_fp, cv2.IMREAD_GRAYSCALE)

    mask_bg = (
        scipy.ndimage.binary_dilation(mask_bg, iterations=8).astype(np.uint8) * 255
    )
    mask_fg = (
        scipy.ndimage.binary_dilation(mask_fg, iterations=8).astype(np.uint8) * 255
    )

    # 创建一个VideoWriter对象来写入输出视频
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 使用mp4编码器
    out = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (frame_width, frame_height),
        isColor=True,
    )

    while True:
        # 读取视频A和视频B的帧
        ret_bg, frame_a = cap_bg.read()
        ret_fg, frame_b = cap_fg.read()

        # 如果任一视频结束，则退出循环
        if not ret_bg or not ret_fg:
            break

        # 将视频B的蒙版部分应用到视频A上
        frame_bg_masked = cv2.bitwise_and(
            frame_a, frame_a, mask=255 - mask_bg
        )  # 非蒙版部分保留

        frame_fg_masked = cv2.bitwise_and(
            frame_b, frame_b, mask=mask_fg
        )  # 蒙版部分提取

        # 合并两个视频帧
        # merged_frame = cv2.add(frame_a_masked, frame_b_masked)
        frame_bg_masked[y : y + h, x : x + w] += frame_fg_masked

        # 写入帧到输出视频
        out.write(frame_bg_masked)

    # 释放资源
    cap_bg.release()
    cap_fg.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    video_file = "./cropped_video.mp4"
    mask_file = "./cropped_mask.png"
    base_video = "./720.mp4"
    base_mask = "./720_mask.png"

    x, y, w, h = crop_video_mask(base_video, base_mask)
