# Android_tcpdump_tool

`Android_tcpdump_tool` 是一个用于抓取 Android 应用流量的命令行工具。

## 安装

```bash
pip install Android_tcpdump_tool
```

## 使用方法
- -a 或 --apk: 目标应用的 APK 文件路径。
- -t 或 --timeout: 抓包超时时间（秒），默认为 300 秒。
- -o 或 --output: 流量文件存储位置

## 示例

```bash
Android_tcpdump_tool -n com.example.app -t 600
```
