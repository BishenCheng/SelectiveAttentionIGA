const express = require("express");
const path = require("path");
const app = express();
const PORT = 3000;

// app.use((req, res, next) => {
//   console.log(`Request URL: ${req.url}`);
//   next();
// });

//  1. 托管 WebGazer 的静态文件（路径 /calibration）
app.use("/calibration", express.static(path.join(__dirname, "public/calibration")));

//  2. 托管 React 的静态资源（路径 /experiment/static）
app.use("/experiment", express.static(path.join(__dirname, "client/build")));

//  3. 处理 WebGazer 的入口文件（避免自动查找 index.html）
app.get("/calibration", (req, res) => {
  res.sendFile(path.join(__dirname, "public/calibration", "calibration.html"));
});

//  4. 处理 React 的客户端路由（所有 /experiment/* 请求重定向到 index.html）
app.get("/experiment/*", (req, res) => {
  res.sendFile(path.join(__dirname, "client/build", "index.html"));
});


// 启动服务器
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log("主页面: http://localhost:3000/calibration");
  console.log("实验页面: http://localhost:3000/experiment");
});