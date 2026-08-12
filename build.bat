@echo off
chcp 65001 >nul
echo 正在打包 Relax XRD Plotter...
py -3 -m PyInstaller --noconfirm --clean --onedir --windowed ^
    --name "Relax XRD Plotter" ^
    --add-data "可爱有趣的XRD画图名字 (1)(1).png;." ^
    main.py
echo 打包完成！
echo 可执行文件位于 dist\Relax XRD Plotter\ 目录下
echo 将整个文件夹压缩后即可拷贝到任意 Windows 电脑运行。
pause
