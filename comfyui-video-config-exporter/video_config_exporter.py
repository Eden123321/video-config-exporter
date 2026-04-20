"""
ComfyUI 节点：视频配置导出器
从 IMAGE 提取尺寸和帧数，生成 mask+rgb 布局的 config.json
"""

import json
import torch
import numpy as np
import os


class VideoConfigExporter:
    """从 IMAGE 获取信息并导出视频配置"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "图像序列"}),
                "filename": ("STRING", {"default": "output.mp4", "tooltip": "输出视频文件名"}),
            },
            "optional": {
                "config_filename": ("STRING", {"default": "config", "tooltip": "JSON 文件名（不含扩展名）"}),
            }
        }

    RETURN_TYPES = ("STRING", "DICT")
    RETURN_NAMES = ("json_string", "config_dict")
    FUNCTION = "export_config"
    CATEGORY = "video/postprocess"
    OUTPUT_NODE = True

    def export_config(self, images, filename="output.mp4", config_filename="config"):
        # images: torch.Tensor, shape (B, H, W, C) 或 (H, W, C)
        if isinstance(images, torch.Tensor):
            if images.ndim == 4:
                frame_count = images.shape[0]
                height, width = images.shape[1], images.shape[2]
            elif images.ndim == 3:
                frame_count = 1
                height, width = images.shape[0], images.shape[1]
            else:
                raise ValueError(f"无法解析 IMAGE 形状: {images.shape}")
        elif isinstance(images, np.ndarray):
            if images.ndim == 4:
                frame_count = images.shape[0]
                height, width = images.shape[1], images.shape[2]
            elif images.ndim == 3:
                frame_count = 1
                height, width = images.shape[0], images.shape[1]
            else:
                raise ValueError(f"无法解析 IMAGE 形状: {images.shape}")
        else:
            raise TypeError(f"不支持的输入类型: {type(images)}")

        single_width = width // 2
        single_height = height
        align = 8 if (single_width % 8 == 0 and single_height % 8 == 0) else 0

        config = {
            "portrait": {
                "v": 1,
                "path": filename,
                "align": align,
                "has_audio": 0,
                "f": frame_count,
                "aFrame": [0, 0, single_width, single_height],
                "rgbFrame": [single_width, 0, single_width, single_height],
                "videoW": width,
                "videoH": height,
                "w": single_width,
                "h": single_height
            }
        }

        json_string = json.dumps(config, separators=(',', ':'), ensure_ascii=False)

        # 保存到 output 目录
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(script_dir, "..", "output")
        output_dir = os.path.normpath(output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, f"{config_filename}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_string)

        return (json_string, config)


NODE_CLASS_MAPPINGS = {
    "VideoConfigExporter": VideoConfigExporter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoConfigExporter": "视频配置导出"
}
