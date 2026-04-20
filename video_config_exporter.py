"""
ComfyUI 节点：视频配置导出器
读取视频元信息并导出 config.json
"""

import cv2
import json
import os


class VideoConfigExporter:
    """读取视频并生成后处理导出配置"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {"default": "", "tooltip": "视频文件路径"}),
            },
            "optional": {
                "output_json_path": ("STRING", {"default": "config.json", "tooltip": "输出 JSON 文件路径"}),
            }
        }

    RETURN_TYPES = ("STRING", "DICT")
    RETURN_NAMES = ("json_string", "config_dict")
    FUNCTION = "export_config"
    CATEGORY = "video/postprocess"
    OUTPUT_NODE = True

    def export_config(self, video_path, output_json_path="config.json"):
        if not video_path or not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频: {video_path}")

        # 获取视频基本信息
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 检查是否有音频 (OpenCV 本身不支持，这里假设无音频或通过其他方式检测)
        has_audio = 0

        cap.release()

        # 计算 align：宽高都能被8整除则为8
        align = 8 if (width % 8 == 0 and height % 8 == 0) else 0

        # 构建配置
        # 假设输入视频是拼接后的 (mask + rgb 水平拼接)
        single_width = width // 2
        single_height = height

        config = {
            "portrait": {
                "v": 1,
                "path": video_path,
                "align": align,
                "has_audio": has_audio,
                "f": int(fps) if fps == int(fps) else fps,
                "aFrame": [0, 0, single_width, single_height],
                "rgbFrame": [single_width, 0, single_width, single_height],
                "videoW": width,
                "videoH": height,
                "w": single_width,
                "h": single_height
            }
        }

        json_string = json.dumps(config, indent=2, ensure_ascii=False)

        # 可选：写入文件
        if output_json_path:
            output_dir = os.path.dirname(output_json_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(output_json_path, 'w', encoding='utf-8') as f:
                f.write(json_string)

        return (json_string, config)


NODE_CLASS_MAPPINGS = {
    "VideoConfigExporter": VideoConfigExporter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoConfigExporter": "视频配置导出"
}
