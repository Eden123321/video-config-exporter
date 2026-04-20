# ComfyUI Video Config Exporter

ComfyUI 自定义节点，用于从图像序列提取尺寸和帧数，生成 mask+rgb 布局的 config.json。

## 安装

将整个目录复制到 ComfyUI 的 `custom_nodes` 目录：

```
<ComfyUI>/custom_nodes/comfyui-video-config-exporter/
```

## 使用

1. 连接图像序列输出到 `images` 输入
2. 设置 `filename`（输出视频文件名，如 `output.mp4`）
3. 设置 `config_filename`（JSON 文件名，默认 `config`）
4. 运行后会在 ComfyUI output 目录生成 JSON 文件

## 输出格式

```json
{"portrait":{"v":1,"path":"output.mp4","align":8,"has_audio":0,"f":90,"aFrame":[0,0,720,1280],"rgbFrame":[720,0,720,1280],"videoW":1440,"videoH":1280,"w":720,"h":1280}}
```

| 字段 | 说明 |
|------|------|
| v | 版本号 |
| path | 输出视频文件名 |
| align | 宽高是否能被8整除 |
| has_audio | 是否有音频 |
| f | 总帧数 |
| aFrame | 遮罩区域 [x, y, w, h] |
| rgbFrame | 视频区域 [x, y, w, h] |
| videoW/videoH | 视频总尺寸 |
| w/h | 单帧尺寸 |
