import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'url';
import AutoImport from 'unplugin-auto-import/vite'//自动引入
import Components from 'unplugin-vue-components/vite';
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers'; //引入antd组件
import requireTransform from 'vite-plugin-require-transform';// 
import commonjs from 'vite-plugin-commonjs';
import { compression } from 'vite-plugin-compression2' //gzip压缩

const dependencies = require('./package.json').dependencies;
const isProd = process.env.NODE_ENV === 'production'

// https://vite.dev/config/
export default defineConfig({
	base: isProd ? '/login/static/' : '/',
	plugins: [
		vue(),
		commonjs(),
		tailwindcss(),
		AutoImport({
			include: [
				/\.[tj]sx?$/, // .ts, .tsx, .js, .jsx
				/\.vue$/,
				/\.vue\?vue/, // .vue
				/\.md$/, // .md
			],
			imports: [
				'vue',
				// 'vue-router',
				// 'pinia',
				// { '@/store': ['useAppStore', 'useUserStore'] }
			],
			eslintrc: {
				enabled: true,
				filepath: './.eslintrc-auto-import.json',
				globalsPropValue: true,
			},
		}),
		Components({
			resolvers: [
				AntDesignVueResolver({
					importStyle: false, // css in js
					resolveIcons: true, //自动引入antd图标
				}),
			],
		}),
		requireTransform({
			fileRegex: /.js$|.vue$/
		}),
		compression({
			algorithms: ['gzip'],
		})
	],
	server: {
		host: '0.0.0.0',
		port: 8000,
		open: true,
	},
	build: {
		assetsDir: 'vite-static',
		reportCompressedSize: false, // 设置为false将禁用构建的压缩大小报告。可以稍微提高构建速度
		rollupOptions: {
			treeshake: true, // 开启 Tree Shaking，消除未使用的代码，减小最终的包大小
			output: {
				// 根据不同的js库 拆分包，减少index.js包体积
				manualChunks(id) {
					if (id.includes('node_modules')) {
						// 指定需要拆分的第三方库或模块
						const dependenciesKeys = Object.keys(dependencies);
						const match = dependenciesKeys.find((item) => {
							return id.includes(item);
						});
						const notSplit = ['vue', 'ant-design-vue',];
						if (match && !notSplit.includes(match)) {
							return match;
						}
					}
				},
			},
		},
	},
	resolve: {
		extensions: ['.js', '.ts', '.jsx', '.tsx', '.json', '.vue'],
		alias: {
			'@': fileURLToPath(new URL('./src', import.meta.url)),
		},
	},
	optimizeDeps: {
		include: ['@ant-design/icons-vue', 'ant-design-vue', 'dayjs'],
	},
})
