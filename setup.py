from setuptools import setup, find_packages

setup(
    name="Android_tcpdump-tool",  # 工具名称
    version="1.0.0",  # 版本号
    author="Dubai",  # 作者
    author_email="fjing2022@whu.edu.cn",  # 作者邮箱
    description="A command-line tool for capturing Android app traffic using tcpdump.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/idontknowoman/Android_tcpdump_tool",  # 项目主页（可选）
    packages=find_packages(),  # 自动发现所有包
    include_package_data=True,
    install_requires=[],  # 如果有依赖包，可以在这里列出
    entry_points={
        "console_scripts": [
            "tcpdump-tool=tcpdump_tool.tcpdump:main",  # 定义命令行工具的入口点
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # 支持的 Python 版本
)