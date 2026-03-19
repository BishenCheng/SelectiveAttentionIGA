# 项目启动指南
## 1.后端启动

```bash  
#  请先运行requirement.txt，然后进入虚拟环境
cd [Your Python venv]
.\activate

#  回到项目主目录

# 进入后端目录
cd backend

# 启动uvicorn服务器
uvicorn main:app --reload --host 127.0.0.1 --port 8002
```
## 2.前端启动

```bash
# 在主目录下运行，
#localhost:3000:calibration是主界面
npm start
```

## build
```bash
cd client
npm run build

'''
