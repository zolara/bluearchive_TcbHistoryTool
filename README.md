<img src="https://124.223.5.69:3000/theme=booru-lewd&padding=7&offset=0&align=top&scale=1&pixelated=1&darkmode=auto">

<a href="https://star-history.com/#zolara/bluearchive_TcbHistoryTool&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=zolara/bluearchive_TcbHistoryTool&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=zolara/bluearchive_TcbHistoryTool&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=zolara/bluearchive_TcbHistoryTool&type=Date" />
 </picture>
</a>

<h2>请给作者点一个star，这是作者持续更新的动力。</h2>
目前已支持日服和国际服。<br>
QQ群 945558059 群头像为小瞬。

<h2>新学生数据包更新方法</h2>
将压缩包解压，并将其中data文件夹替换原本软件根目录下data文件。

<h2>通过可执行文件直接运行</h2>
请在右侧下载release版本，无需下载源码，无需考虑环境。

<h2>通过源码编译运行</h2>
推荐使用conda等版本依赖工具构建虚拟环境，本项目具有较严格的版本依赖环境。

```javascript
python==3.11.9
pandas==1.5.3
numpy==1.25.0
```
OCR模块安装教程<https://github.com/PaddlePaddle/PaddleOCR/blob/main/ppstructure/docs/PP-StructureV2_introduction.md>

<h2>通过pyinstaller编译源码打包运行</h2>

```javascript
pyinstaller.exe -i icon1.ico -D .\main.py --collect-all paddleocr --collect-all pyclipper --collect-all imghdr --collect-all skimage --collect-all imgaug --collect-all scipy.io --collect-all lmdb -p python_path\Lib\site-packages\scipy\_lib\array_api_compat\numpy\fft --hidden-import PySide6.QtSvg
```
报错解决方法
1. 编译中报错UserWarning: The numpy.array_api submodule is still experimental. See NEP 47.<br />解决方式：python_path\Lib\site-packages\Pyinstaller\building\build_main.py打开167行：
__import__(package)改成import package
2. 运行报错FileNotFoundError: [WinError 2] 系统找不到指定的文件。<br />解决办法：将 ‘your_path\dist\checknum\paddle\base\…\libs’<br />将python_path\Lib\site-packages下面的libs复制在your_path\dist\main\_internal\paddle下面，与\base平级
3. 运行报错ModuleNotFoundError: No module named 'scipy._lib.array_api_compat.numpy.fft'<br /> 解决办法：将python_path\Lib\site-packages\scipy\_lib复制array_api_compat文件夹到your_path\dist\main\_internal\scipy\_lib下面
4. 运行报错ModuleNotFoundError: No module named 'scipy.special._special_ufuncs'<br /> 解决办法：python_path\Lib\site-packages\scipy\复制special文件夹your_path\dist\main\_internal\scipy下面
