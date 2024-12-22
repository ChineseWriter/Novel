# 关于 Python 的 abspath 函数的讨论

最近写这个项目时发现在 Ubuntu 系统上运行出了点问题.

主要是 Settings 模块, 其中有一个全局设置用到了 Python 的 os.path.abspath() 函数, 即 DATA_DIR.

问题具体表现为 获取到得绝对路径成为了 ".../.\data", 这并不是我想看到的.

在 Windows 系统中, 这个".\\"部分可以被正确解释为一个相对路径的表示, 但是在 Ubuntu 系统中不行.

## abspath 函数源码
在 Ubuntu 系统上, 我找到的源码是这样的:
```python
def abspath(path):
    """Return an absolute path."""
    path = os.fspath(path)
    if not isabs(path):
        if isinstance(path, bytes):
            cwd = os.getcwdb()
        else:
            cwd = os.getcwd()
        path = join(cwd, path)
    return normpath(path)
```

在 Windows 系统上, 我找到的源码是这样的:
```python
# TODO 补全这里的源码
```

## 问题解决
首先, 这个函数的逻辑是将给定的 path 变量和目前的工作目录直接进行拼接, 所以传入的路径都是相对于目前的工作目录而言的.

其次, 这个函数使用同在这个模块内的 join 函数进行拼接路径, 所以这里只能使用这个函数允许的分隔符进行表示, 在 Ubuntu 系统中允许的是"/".