# 新手使用说明

这份说明默认你已经完成了环境配置，并且当前就在项目根目录下。

## 1. 先确认你现在所在的位置

项目根目录里应该能看到这些文件或文件夹：

- `main.py`
- `launch_gui.py`
- `assets/`
- `models/`
- `.venv/`

如果这些都在，说明你就在正确位置。

## 2. 激活虚拟环境

在 PowerShell 中运行：

```powershell
.\.venv\Scripts\Activate.ps1
```

激活后，命令行前面一般会出现 `(.venv)`。

## 3. 准备测试素材

把你自己的测试文件放到下面两个目录中：

- 图片放到 `assets/inputs/images/`
- 视频放到 `assets/inputs/videos/`

例如：

- `assets/inputs/images/test.jpg`
- `assets/inputs/videos/test.mp4`

## 4. 最推荐的使用方式：命令行运行图片

如果你想识别一张图片，运行：

```powershell
python main.py --source image --input "assets/inputs/images/test.jpg"
```

运行完成后：

- 程序会进行识别
- 结果图片会默认保存到 `assets/outputs/images/`

例如输出文件可能是：

- `assets/outputs/images/test_result.jpg`

## 5. 命令行运行视频

如果你想识别一个视频，运行：

```powershell
python main.py --source video --input "assets/inputs/videos/test.mp4"
```

运行完成后：

- 程序会逐帧处理视频
- 结果视频会默认保存到 `assets/outputs/videos/`

例如输出文件可能是：

- `assets/outputs/videos/test_result.mp4`

## 6. 不想弹出识别窗口时

如果你只想生成结果文件，不想在识别过程中显示窗口，可以加上 `--no-display`：

图片：

```powershell
python main.py --source image --input "assets/inputs/images/test.jpg" --no-display
```

视频：

```powershell
python main.py --source video --input "assets/inputs/videos/test.mp4" --no-display
```

这个选项很适合批量测试和写报告时保存结果。

## 7. 如果你想自己指定输出位置

可以加 `--output` 参数。

例如图片：

```powershell
python main.py --source image --input "assets/inputs/images/test.jpg" --output "assets/outputs/images/my_result.jpg"
```

例如视频：

```powershell
python main.py --source video --input "assets/inputs/videos/test.mp4" --output "assets/outputs/videos/my_result.mp4"
```

## 8. 图形界面使用方法

如果你不想敲命令，可以直接启动图形界面：

```powershell
python launch_gui.py
```

打开后你会看到三个按钮：

- `Select Image`：选择图片进行识别
- `Select Video`：选择视频进行识别
- `Camera (Optional)`：摄像头功能，目前保留为扩展项

使用步骤：

1. 点击 `Select Image` 或 `Select Video`
2. 在弹出的窗口中选择文件
3. 等待识别完成
4. 查看弹窗提示中的保存位置

## 9. 识别结果怎么看

输出结果中会标出：

- 检测框
- 跟踪 ID
- 情绪标签

例如：

- `ID: 1 - Happy`
- `ID: 2 - Neutral`

当前模型使用的情绪类别包括：

- `Anger`
- `Contempt`
- `Disgust`
- `Fear`
- `Happy`
- `Neutral`
- `Sad`
- `Surprise`

## 10. 结果文件在哪

默认结果都保存在这里：

- 图片结果：`assets/outputs/images/`
- 视频结果：`assets/outputs/videos/`
- 报告截图：`assets/outputs/screenshots/`

如果你后面要写课程报告，建议把需要的运行截图也统一放到 `assets/outputs/screenshots/`。

## 11. 常见问题

### 1. 提示找不到输入文件

检查：

- 文件路径是否写对
- 文件是否真的放在 `assets/inputs/images/` 或 `assets/inputs/videos/` 下
- 文件名后缀是否正确

### 2. 程序运行很慢

这是正常现象，尤其是视频处理。

影响速度的常见原因：

- 视频分辨率较高
- 视频时长较长
- 电脑没有使用更强的 GPU

建议先用短视频测试。

### 3. 运行后没有识别到人脸

可能原因：

- 图片里的人脸太小
- 角度太偏
- 光线太暗
- 表情不明显

建议先用正脸、清晰、光线好的图片测试。

### 4. 输出成功但结果不理想

这是正常的。

因为当前阶段是“先跑通现成项目”，目标是先完成演示、测试和报告，不是重新训练自己的高精度模型。

## 12. 新手最建议的操作顺序

第一次使用建议按这个顺序来：

1. 激活虚拟环境
2. 先运行一张图片
3. 查看 `assets/outputs/images/` 中是否生成结果
4. 再运行一个短视频
5. 查看 `assets/outputs/videos/` 中是否生成结果
6. 最后再尝试 GUI

## 13. 你现在可以直接复制使用的命令

图片识别：

```powershell
python main.py --source image --input "assets/inputs/images/lena.jpg" --no-display
```

视频识别：

```powershell
python main.py --source video --input "assets/inputs/videos/face_walk.mp4" --no-display
```

启动 GUI：

```powershell
python launch_gui.py
```
