移动生活小秘书1.0版

### 重要

项目工程已经添加到百度应用引擎(BAE)

* 添加BAE远程仓库：

`git remote add bae https://git.duapp.com/appidbxe80g2m0g`

* 向BAE仓库发布应用进行测试：

`git push bae <branch>:master`

(<branch>换成要push上去的分支，push完成需要点击快捷发布)

* 提交代码应该提交到gitlab仓库上，BAE仓库用来发布测试应用

* 本地测试应用：

`python index.py`


开发环境：Python2.7 + BAE

Python环境： Flask + SqlAlchemy

访问地址：http://moblife.duapp.com/

mobile目录为代码目录，是一个python package

mobile_life_doc目录为文档目录

分支说明：

* master分支为最终上线版本分支，一般不提交，dev分支测试之后merge即可

* dev分支为开发分支，每个人完成一项功能之后（包括测试）merge到此分支

* 每个成员创建一个个人开发分支，一般每个成员在自己的分支上或者功能分支上开发

* 每一个功能创建一个功能分支，一个人或者几个人在此分支工作，一个人可能会在多个功能分支上开发


现在无法在线测试了，请在本地做好测试