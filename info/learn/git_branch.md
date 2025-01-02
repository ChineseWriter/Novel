# Git 分支管理规范
## 常用的分支(组)介绍
### master 分支(常驻)
主分支, 又叫 Production 分支.  
该分支主要用于记录上线版本的迭代.  
该分支代码与线上代码是完全一致的, 即它的内容是最近发布到生产环境的代码, 即 Release 的部分.  
*注意: 这个分支只能从其他分支合并, 不能在这个分支直接修改, 即该分支不应该存在 Commit, 每次合并应当打 Tag.*

### dev 分支(常驻)
开发分支, 即 Develop 分支.  
该分支主要用于日常开发工作的进行, 并记录相对稳定的版本, 下一个要 Release 的版本应从它之上分出.  
大部分开发相关的分支应当从它之上分出, 开发完成后再合并到该分支上.  

### release 分支组(临时)
发布分支.  
该分支主要用于做发布前的测试, 即上线准备.  
该分支应基于 dev 分支创建, 完成后合并到 master 和 dev 分支上.  
发现 Bug 时应直接在这上面进行修复.  

### feature 分支组(临时)
功能分支, 也叫特性分支.  
该分支主要用于开发一个特定的新功能.  
该分支应基于 dev 分支创建, 完成后合并到 dev 分支.  
不同的功能创建不同的 feature 分支.  

### bugfix 分支组(临时)
普通修复分支.  
该分支主要用于修复普通的 Bug.  
该分支应基于 dev 分支创建, 完成后合并到 dev 分支.  
不同的 Bug 修复应创建不同的 bugfix 分支.  

### hotfix 分支组(临时)
紧急修复分支.  
该分支主要用于修复紧急的 Bug.  
该分支应基于 master 分支创建, 完成后合并到 master 和 dev 分支.
不同的 Bug 修复应创建不同的 hotfix 分支.  

## 分支(组)命名规范
&emsp;&emsp;常驻分支中, master 分支一般保留这个本名, dev 分支也可以命名为 develop 分支.  
&emsp;&emsp;临时分支组中, 应当按照"分支名/YYYYMMDD_名字"来命名, 名字中, feature 和 release 应当参照功能名或版本(别)名, bugfix 和 hotfix 应当参照 bug 名或 bug 编号(bug 编号更常用), 比如"feature/20241215_book_obj".  

## 分支使用流程
&emsp;&emsp;项目创建时, 会有一个自动创建的 master 分支, 此时应当同时创建 dev 分支, 并使用它进行日常开发.  
&emsp;&emsp;当需要上线一个新功能时, 创建一个 feature 分支, 并切换到该分支工作.  
&emsp;&emsp;当需要修复一个 bug 时, 创建一个 bug 分支, 并切换到该分支工作.  
&emsp;&emsp;*注意: 可以同时创建多个 feature 分支和 bugfix 分支, 但是请确保修改项目的部分尽量不重复.*  
&emsp;&emsp;feature 分支和 bugfix 分支工作完毕后将其合并到 dev 分支, 然后可删除该分支.  
&emsp;&emsp;当 dev 分支开发到一个阶段之后, 可从 dev 分支分出 release 分支, 用于上线前的测试, 测试完以后将其合并到 master 分支及 dev 分支.  
&emsp;&emsp;出现需要紧急修复的 bug 时, 应当从 master 分支分出 hotfix 分支, bug 修复完成后将其合并到 master 分支和 dev 分支