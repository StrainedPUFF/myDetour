module.exports = {
    webpack: {
      configure: (webpackConfig) => {
        webpackConfig.module.rules.push({
          test: /\.wasm$/,
          type: "javascript/auto",
          loader: "file-loader",
        });
        return webpackConfig;
      },
    },
  };
  