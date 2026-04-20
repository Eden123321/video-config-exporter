"""
ComfyUI 节点：视频配置导出器
从 IMAGE 或 VIDEO 提取尺寸和帧数，生成 mask+rgb 布局的 config.json
"""

import json
import torch
import numpy as np
import cv2
import os


class VideoConfigExporter:
    """从 IMAGE 或 VIDEO 获取信息并导出视频配置"""

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
                # (B, H, W, C) -> 图像序列
                frame_count = images.shape[0]
                height, width = images.shape[1], images.shape[2]
            elif images.ndim == 3:
                # (H, W, C) -> 单张图像
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

        # 保存到 output 目录，自动递增编号
        # 优先使用 ComfyUI 标准 output 目录
        possible_paths = [
            os.path.join(os.getcwd(), "output"),
            "/opt/tiger/ComfyUI/ComfyUI/output",
            "C:/aki1.7/ComfyUI-aki-v1.7/ComfyUI/output",
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "output"),
        ]

        output_dir = None
        for p in possible_paths:
            p = os.path.normpath(p)
            if os.path.exists(p) or os.access(os.path.dirname(p), os.W_OK):
                output_dir = p
                break

        if output_dir is None:
            output_dir = possible_paths[0]

        os.makedirs(output_dir, exist_ok=True)

        # 查找已有文件的最新编号
        try:
            existing_files = [f for f in os.listdir(output_dir) if f.startswith(config_filename) and f.endswith('.json')]
            if existing_files:
                numbers = []
                for f in existing_files:
                    try:
                        num_str = f.replace(config_filename, '').replace('.json', '')
                        if num_str.isdigit():
                            numbers.append(int(num_str))
                    except:
                        pass
                next_num = max(numbers) + 1 if numbers else 1
            else:
                next_num = 1
        except:
            next_num = 1

        output_filename = f"{config_filename}{next_num:05d}.json"
        output_path = os.path.join(output_dir, output_filename)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_string)
        except Exception as e:
            # 写入失败时尝试使用 temp 目录
            import tempfile
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_string)

        return (json_string, config)


NODE_CLASS_MAPPINGS = {
    "VideoConfigExporter": VideoConfigExporter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoConfigExporter": "视频配置导出"
}
