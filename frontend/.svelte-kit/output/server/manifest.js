export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set([]),
	mimeTypes: {},
	_: {
		client: {start:"_app/immutable/entry/start.Cw_hpEk4.js",app:"_app/immutable/entry/app.BF9vJsyR.js",imports:["_app/immutable/entry/start.Cw_hpEk4.js","_app/immutable/chunks/CGN0osXo.js","_app/immutable/chunks/BRzekBSy.js","_app/immutable/chunks/CggwGMe1.js","_app/immutable/entry/app.BF9vJsyR.js","_app/immutable/chunks/CGN0osXo.js","_app/immutable/chunks/DTfA-Vau.js","_app/immutable/chunks/mXfHdRHy.js","_app/immutable/chunks/CggwGMe1.js","_app/immutable/chunks/DOZD0HzG.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
