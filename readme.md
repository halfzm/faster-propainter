# faster-propainter（仅适用静态水印）
核心思路：把水印区域裁剪出来，去水印，把去水印后的区域拼接回去

## 视频介绍
[百倍速去水印再加速，基于ptflow的propainter加速版AI视频去水印工具](https://www.bilibili.com/video/BV1MJ4m1M7nQ)

## 环境配置
在propainter项目的基础上安装`ptlflow`
```bash
pip install ptlflow 
```


## 快速启动
```globals.py```
里面配置输入文件、蒙版文件、输出文件路径

```python start.py```
开始执行

## 相关项目
[ProPainter](https://github.com/sczhou/ProPainter)
[ProPainter-Webui](https://github.com/halfzm/ProPainter-Webui)
