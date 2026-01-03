# 前端项目
#### 项目采用vue3.5.x + vite7.x + ant-design-vue4.2.x + tailwindcss4.x开发，node.js建议使用v22.21以上的版本。前端核心功能特别依赖于以下浏览器版本：
- Chrome 111(发布于2023年03月)
- Safari 16.4(发布于2023年03月)
- Firefox 128(发布于2024年07月)

若遇到样式浏览器兼容问题，请自行升级浏览器版本。

#### 安装依赖
- npm install
#### 启动项目
- npm run serve
#### 打包项目
- npm run build
#### 打包后生成文件
- 打包后生成的文件在dist目录下，将dist目录下的index.html文件复制到/pass-ce/paas/login/templates/login文件夹下，将原login.html删除，并将index.html文件名改为login.html
- 将dist目录下的vite-static文件夹和favicon.ico复制到/paas-ce/paas/login/static文件下，如果/paas-ce/paas/login/static/文件夹下的vite-static文件夹已经存在，请先将此目录下的vite-static删除再进行操作。