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
def abspath(path):
    """Return an absolute path."""
    path = os.fspath(path)
    if isinstance(path, bytes):
        if not path.startswith(b'/'):
            path = join(os.getcwdb(), path)
    else:
        if not path.startswith('/'):
            path = join(os.getcwd(), path)
    return normpath(path)
```

## 问题解决
首先, 这个函数的逻辑是: 
1. 确定给定的路径不是一个绝对路径, 具体在 Linux 中有一个用于确定的函数, 在 Windows 中则是是否以"/"开头.
2. 如果不是一个绝对路径, 则将给定的路径与现有的工作目录进行拼接, 因为一个相对路径必须要有一个基准路径. 注意: 这个基准路径不是当前文件所在的路径, 而是当前工作目录.
3. 如果是一个绝对路径, 则直接返回这个路径.
4. 返回时调用 normpath 函数, 用于规范化路径.

其次, 问题的关键在于 normpath 函数, 这个函数在 Windows 和 Linux 中的表现是不一样的.

以下是 Windows 中的 normpath 函数的源码:
```python
def normpath(path):
	"""Normalize path, eliminating double slashes, etc."""
	path = os.fspath(path)
	if isinstance(path, bytes):
		sep = b'/'
		dot = b'.'
		dotdot = b'..'
	else:
		sep = '/'
		dot = '.'
		dotdot = '..'
	if not path:
		return dot
	_, initial_slashes, path = splitroot(path)
	comps = path.split(sep)
	new_comps = []
	for comp in comps:
		if not comp or comp == dot:
			continue
		if (comp != dotdot or (not initial_slashes and not new_comps) or
				(new_comps and new_comps[-1] == dotdot)):
			new_comps.append(comp)
		elif new_comps:
			new_comps.pop()
	comps = new_comps
	path = initial_slashes + sep.join(comps)
	return path or dot
```
由此可以看出在 Windows 中 Python 主动将路径中的 "." 部分解释为当前路径, ".." 部分解释为上级路径, 而在 Linux 中则不会.