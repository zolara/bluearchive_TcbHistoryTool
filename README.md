<img src="https://count.getloli.com/@zolara?name=zolara&theme=booru-lewd&padding=7&offset=0&align=top&scale=1&pixelated=1&darkmode=auto">

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

<h2>使用方法Usage</h2>

![rm_img0](https://github.com/user-attachments/assets/795dd269-e293-438c-8014-1b1a8c198964)

首次使用请先运行根目录下update.bat更新数据包。
1. 点击新建记录表，新建一张空白的记录表；
2. 点击查看记录表，打开刚才新建的记录表；
3. 点击保存记录，选择战报截图导入。

<h2>注意事项</h2>
1. 截图导入目前仅支持1080*1920的图像，若是国服则可以自行配置/data/screenshot_param/SC_1080p.json中的参数。
2. 软件与截图保存路径不支持中文，请先修改模拟器截图保存路径。


<h2>新学生数据包更新方法</h2>
运行根目录下update.bat自动下载更新数据包。

<h2>运行方法</h2>
<h3>推荐——通过可执行文件直接运行</h3>
请在右侧下载release版本，无需下载源码，无需考虑环境。

<h3>不推荐——通过源码编译运行</h3>
推荐使用conda等版本依赖工具构建虚拟环境，本项目具有较严格的版本依赖环境。

```javascript
python==3.11.9
pandas==1.5.3
numpy==1.25.0
```
OCR模块安装教程<https://github.com/PaddlePaddle/PaddleOCR/blob/main/ppstructure/docs/PP-StructureV2_introduction.md>

<h3>极不推荐——通过pyinstaller编译源码打包运行</h3>

```javascript
pyinstaller.exe -i icon1.ico -D .\main.py --collect-all paddleocr --collect-all pyclipper --collect-all imghdr --collect-all skimage --collect-all imgaug --collect-all scipy.io --collect-all lmdb -p python_path\Lib\site-packages\scipy\_lib\array_api_compat\numpy\fft --hidden-import PySide6.QtSvg
```
报错解决方法
1. 编译中报错UserWarning: The numpy.array_api submodule is still experimental. See NEP 47.<br />解决方式：python_path\Lib\site-packages\Pyinstaller\building\build_main.py打开167行：
\_\_import\_\_(package)改成import package
2. 运行报错FileNotFoundError: [WinError 2] 系统找不到指定的文件。<br />解决办法：将 ‘your_path\dist\checknum\paddle\base\…\libs’<br />将python_path\Lib\site-packages下面的libs复制在your_path\dist\main\_internal\paddle下面，与\base平级
3. 运行报错ModuleNotFoundError: No module named 'scipy._lib.array_api_compat.numpy.fft'<br /> 解决办法：将python_path\Lib\site-packages\scipy\_lib复制array_api_compat文件夹到your_path\dist\main\_internal\scipy\_lib下面
4. 运行报错ModuleNotFoundError: No module named 'scipy.special._special_ufuncs'<br /> 解决办法：python_path\Lib\site-packages\scipy\复制special文件夹your_path\dist\main\_internal\scipy下面
