# 第一阶段测试记录

## 测试环境

- 系统：Windows
- Python：3.12.10
- 虚拟环境：`.venv`
- 主要依赖：
  - `numpy 1.26.4`
  - `opencv-python 4.11.0.86`
  - `ultralytics 8.3.86`
  - `deep-sort-realtime 1.3.2`

## 执行命令

```bash
python main.py --source image --input "assets/inputs/images/lena.jpg" --no-display
python main.py --source image --input "assets/inputs/images/no_face.jpg" --no-display
python main.py --source video --input "assets/inputs/videos/two_people_pan.mp4" --no-display
python main.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```

## 测试结果

- 图片测试 1：`lena.jpg`
  - 程序正常执行
  - 结果图已保存到 `assets/outputs/images/lena_result.jpg`
- 图片测试 2：`no_face.jpg`
  - 程序正常执行
  - 在无明显人脸目标情况下仍能完成输出保存
  - 结果图已保存到 `assets/outputs/images/no_face_result.jpg`
- 视频测试 1：`two_people_pan.mp4`
  - 程序正常执行
  - 结果视频已保存到 `assets/outputs/videos/two_people_pan_result.mp4`
- 视频测试 2：`face_walk.mp4`
  - 程序正常执行
  - 结果视频已保存到 `assets/outputs/videos/face_walk_result.mp4`

## 报告可用素材

- 图片结果截图：
  - `assets/outputs/screenshots/lena_result.png`
  - `assets/outputs/screenshots/no_face_result.png`
- 视频关键帧截图：
  - `assets/outputs/screenshots/two_people_pan_result_frame1.png`
  - `assets/outputs/screenshots/face_walk_result_frame1.png`

## 已知说明

- `deep_sort_realtime` 在运行时会输出一条 `pkg_resources` 弃用警告，但不影响本阶段功能验证。
- 当前阶段已优先验证图片和视频输入，摄像头模式保留为后续扩展项。
