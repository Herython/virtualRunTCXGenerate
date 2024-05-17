## 使用方法

```
python formalBetter.py
```

### Something need to pay attention to:

1. 里面的时区采用的事标准时区，所以需要转换一下时区，在最新的文件中已经写了转换成北京时间的脚本
2. 需要轨迹的经纬度坐标，可以通过[GoogleMap](https://www.google.com/maps)获取，国内的地图导入会有坐标偏移。
3. 目前的插值模拟路径并不太完美仍然需要改进
4. 需要修改跑步的细致参数，可以让GPT帮忙修改

## Awesome

- [华为运动健康在线导入](https://h5hosting.dbankcdn.com/cch5/healthkit/data-import/pages/oauth-callback.html#/)
- [FitConverter](https://www.fitconverter.com/):部分参考导出导入数据的教程
- [Hitrava](https://github.com/CTHRU/Hitrava):能把华为运动健康数据的json格式转化为可导入第三方平台的tcx格式的Github项目
- [Hitrava-Web](https://cthru.hopto.org/hitrava-web/):Hitrava的WebUI
- [Running Page](https://github.com/yihong0618/running_page):一个能够帮助制作个人跑步界面的Github项目
